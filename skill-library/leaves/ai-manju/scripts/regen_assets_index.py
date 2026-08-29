#!/usr/bin/env python3
"""扫描项目目录，生成/更新 ASSETS-INDEX.md。

用途：
  - 治理门禁 5（ASSETS-INDEX.md 同步更新）
  - 把"靠 AI 记得更新"的人工对冲改为"脚本机械扫描"

扫描维度：
  - 场景库 03-scenes/*/
  - 角色库 04-character/*/（含 _extras 群演）
  - 视频产出 05-videos/ep*/
  - 成片产出 06-output/ep*.mp4

用法:
    python3 regen_assets_index.py <项目路径>
    python3 regen_assets_index.py projects/bengong-kaidian

参数:
    --write   直接写入 ASSETS-INDEX.md（否则只打印到 stdout 预览）
    --check   检查模式：不写入，如果当前 ASSETS-INDEX.md 与扫描结果不一致返回 exit 1（CI 用）

设计原则：
  - 只机械生成**骨架表格**（目录/文件状态），不修改备注列
  - 已存在的 ASSETS-INDEX.md 的手写备注列会被保留（通过匹配目录名）
  - 首次生成时备注列留空
  - 只报告机械可判的"存在/不存在"，不判断"有效/无效"
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional


# 从子目录 assets.md 提取中文名（标题第一行 `# XXX 资产清单` / `# XXX 场景库资产` 等）
CN_NAME_PATTERN = re.compile(
    r'^#\s+([^\n]+?)\s*(?:资产|资产清单|场景库资产|角色库资产)?\s*$',
    re.MULTILINE,
)


def extract_cn_name(assets_md: Path) -> str:
    """从子目录的 assets.md 第一行标题提取中文名。

    兼容格式：
      # 沈鹿溪 资产清单
      # 宫道 场景库资产
      # 众嫔妃 群演资产
      # 众嫔妃
    """
    if not assets_md.is_file():
        return '(未登记)'
    try:
        first_line = assets_md.read_text(encoding='utf-8').splitlines()[0]
    except (UnicodeDecodeError, IndexError):
        return '(未登记)'
    m = re.match(r'#\s+(.+?)\s*$', first_line)
    if not m:
        return '(未登记)'
    raw = m.group(1).strip()
    # 去掉已知后缀
    for suffix in ('资产清单', '场景库资产', '角色库资产', '群演资产', '资产'):
        if raw.endswith(suffix):
            raw = raw[:-len(suffix)].strip()
            break
    return raw or '(未登记)'


def extract_voice_info(assets_md: Path) -> str:
    """从角色 assets.md 提取音色 ID 信息。"""
    if not assets_md.is_file():
        return '—'
    text = assets_md.read_text(encoding='utf-8')
    # 查找音色表：| file | 音色 ID | emotion | ... |
    m = re.search(
        r'\|\s*voice-ref\.mp3\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|',
        text,
    )
    if m:
        voice = m.group(1).strip()
        emotion = m.group(2).strip()
        # 简化显示：去掉 `_uranus_bigtts` 后缀
        voice = re.sub(r'_uranus_bigtts$', '', voice)
        return f'{voice} ({emotion})'
    return '—'


def scan_scenes(project_dir: Path) -> list[dict]:
    """扫描 03-scenes/ 目录。"""
    scenes_dir = project_dir / '03-scenes'
    if not scenes_dir.is_dir():
        return []

    results = []
    for child in sorted(scenes_dir.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith('_') or child.name.startswith('.'):
            # 跳过 _props、_backup 等
            continue
        main_png = child / 'main.png'
        assets_md = child / 'assets.md'
        cn_name = extract_cn_name(assets_md)
        variants = sorted(
            f.name for f in child.glob('main-*.png')
        )
        results.append({
            'cn_name': cn_name,
            'dir_name': child.name,
            'has_main': main_png.is_file(),
            'variants': variants,
        })
    return results


def scan_characters(project_dir: Path) -> tuple[list[dict], list[dict]]:
    """扫描 04-character/ 目录，返回 (主角, 群演)。"""
    char_dir = project_dir / '04-character'
    if not char_dir.is_dir():
        return [], []

    main_chars = []
    extras = []

    for child in sorted(char_dir.iterdir()):
        if not child.is_dir():
            continue
        if child.name in ('_extras',):
            # 群演目录
            for extra in sorted(child.iterdir()):
                if not extra.is_dir():
                    continue
                if extra.name.startswith('.'):
                    continue
                multiview = extra / 'multiview.png'
                assets_md = extra / 'assets.md'
                cn_name = extract_cn_name(assets_md)
                extras.append({
                    'cn_name': cn_name,
                    'dir_name': f'_extras/{extra.name}',
                    'has_multiview': multiview.is_file(),
                })
            continue
        if child.name.startswith('_') or child.name.startswith('.'):
            continue

        front = child / 'front.png'
        multiview = child / 'multiview.png'
        voice_ref = child / 'voice-ref.mp3'
        assets_md = child / 'assets.md'
        cn_name = extract_cn_name(assets_md)
        main_chars.append({
            'cn_name': cn_name,
            'dir_name': child.name,
            'has_front': front.is_file(),
            'has_multiview': multiview.is_file(),
            'has_voice': voice_ref.is_file(),
            'voice_info': extract_voice_info(assets_md),
        })

    return main_chars, extras


def scan_videos(project_dir: Path) -> list[dict]:
    """扫描 05-videos/ep*/ 目录。"""
    videos_dir = project_dir / '05-videos'
    if not videos_dir.is_dir():
        return []

    results = []
    for child in sorted(videos_dir.iterdir()):
        if not child.is_dir():
            continue
        if not re.match(r'ep\d+', child.name):
            continue
        segs = sorted(child.glob('seg*.mp4'))
        results.append({
            'ep': child.name.upper(),
            'dir': f'05-videos/{child.name}/',
            'seg_count': len(segs),
        })
    return results


def scan_outputs(project_dir: Path) -> list[dict]:
    """扫描 06-output/*.mp4。"""
    output_dir = project_dir / '06-output'
    if not output_dir.is_dir():
        return []

    results = []
    for f in sorted(output_dir.glob('ep*.mp4')):
        size_mb = f.stat().st_size / 1024 / 1024
        # 推断类型（raw/final）
        kind = 'final' if '-final' in f.name else ('raw' if '-raw' in f.name else '?')
        results.append({
            'file': f.name,
            'size_mb': f'{size_mb:.0f}M',
            'kind': kind,
        })
    return results


def load_existing_remarks(index_path: Path) -> dict[str, str]:
    """从现有 ASSETS-INDEX.md 读取 {dir_name: remark} 字典，用于保留手写备注。"""
    if not index_path.is_file():
        return {}
    text = index_path.read_text(encoding='utf-8')
    remarks = {}
    # 场景库表：| 中文名 | `dir_name` | ✅ | 备注 |
    # 角色库表：| 中文名 | `dir_name` | ✅ | ✅ | ✅ | 音色 ID |（音色 ID 不作为备注保留）
    # 通用提取：匹配带反引号包裹的 dir_name 及其最后一列
    scene_row = re.compile(
        r'\|[^|]*\|\s*`([^`]+)`\s*\|[^|]*\|\s*([^|]*?)\s*\|',
    )
    # 只用于场景库段（有"备注"列）
    in_scenes = False
    for line in text.splitlines():
        if '## 场景库' in line:
            in_scenes = True
            continue
        if in_scenes and line.startswith('##'):
            in_scenes = False
            continue
        if in_scenes:
            m = scene_row.match(line)
            if m:
                dir_name = m.group(1).strip()
                remark = m.group(2).strip()
                if remark and remark not in ('备注', '---'):
                    remarks[dir_name] = remark
    return remarks


def render(
    project_name: str,
    scenes: list[dict],
    main_chars: list[dict],
    extras: list[dict],
    videos: list[dict],
    outputs: list[dict],
    existing_remarks: dict[str, str],
) -> str:
    lines = []
    lines.append(f'# 资产速查表 — {project_name}')
    lines.append('')
    lines.append('> 本文件是项目所有生成资产的快速索引。每次新建/修改资产后同步更新。')
    lines.append('> AI 进入任何阶段前先读此文件定位资产，不需要逐目录扫描。')
    lines.append(f'> 最后更新：{date.today().isoformat()}（由 regen_assets_index.py 生成）')
    lines.append('')
    lines.append('---')
    lines.append('')

    # 场景库
    lines.append('## 场景库（03-scenes/）')
    lines.append('')
    lines.append('| 中文名 | 目录名 | main.png | 备注 |')
    lines.append('|--------|--------|----------|------|')
    for s in scenes:
        mark = '✅' if s['has_main'] else '❌'
        variants_note = ''
        if s['variants']:
            variants_note = f'（含变体 {len(s["variants"])} 个）'
        remark = existing_remarks.get(s['dir_name'], '') + variants_note
        lines.append(
            f'| {s["cn_name"]} | `{s["dir_name"]}` | {mark} | {remark} |'
        )
    lines.append('')
    scene_total = len(scenes)
    scene_ok = sum(1 for s in scenes if s['has_main'])
    lines.append(f'**统计**：{scene_total} 场景，main.png {scene_ok}/{scene_total}')
    lines.append('**ref-images 用法**：阶段 07 直接传入 `main.png`（不需要 multiview）')
    lines.append('')
    lines.append('---')
    lines.append('')

    # 角色库
    lines.append('## 角色库（04-character/）')
    lines.append('')
    lines.append('| 中文名 | 目录名 | front.png | multiview.png | voice-ref.mp3 | 音色 ID |')
    lines.append('|--------|--------|-----------|---------------|---------------|---------|')
    for c in main_chars:
        f_mark = '✅' if c['has_front'] else '❌'
        m_mark = '✅' if c['has_multiview'] else '❌'
        v_mark = '✅' if c['has_voice'] else '❌'
        lines.append(
            f'| {c["cn_name"]} | `{c["dir_name"]}` | {f_mark} | {m_mark} | {v_mark} | {c["voice_info"]} |'
        )
    lines.append('')
    char_total = len(main_chars)
    char_full = sum(
        1 for c in main_chars
        if c['has_front'] and c['has_multiview'] and c['has_voice']
    )
    lines.append(f'**统计**：{char_total} 角色，全套齐全 {char_full}/{char_total}')
    lines.append('')

    if extras:
        lines.append('### 群演角色（04-character/_extras/）')
        lines.append('')
        lines.append('| 中文名 | 目录名 | multiview.png | 用途 |')
        lines.append('|--------|--------|---------------|------|')
        for e in extras:
            m_mark = '✅' if e['has_multiview'] else '❌'
            remark = existing_remarks.get(e['dir_name'], '')
            lines.append(
                f'| {e["cn_name"]} | `{e["dir_name"]}` | {m_mark} | {remark} |'
            )
        lines.append('')

    lines.append('---')
    lines.append('')

    # 视频产出
    lines.append('## 视频产出（05-videos/）')
    lines.append('')
    lines.append('| 集 | 目录 | seg 数 | 状态 |')
    lines.append('|----|------|--------|------|')
    for v in videos:
        status = '✅ 全部生成' if v['seg_count'] > 0 else '⏳ 未生成'
        lines.append(
            f'| {v["ep"]} | `{v["dir"]}` | {v["seg_count"]} | {status} |'
        )
    lines.append('')
    lines.append('---')
    lines.append('')

    # 成片产出
    lines.append('## 成片产出（06-output/）')
    lines.append('')
    lines.append('| 集 | 文件 | 大小 | 状态 |')
    lines.append('|----|------|------|------|')
    for o in outputs:
        ep = re.match(r'(ep\d+)', o['file'])
        ep_name = ep.group(1).upper() if ep else o['file']
        kind_note = '无字幕' if o['kind'] == 'raw' else ('带字幕' if o['kind'] == 'final' else '')
        lines.append(
            f'| {ep_name} | `{o["file"]}`（{kind_note}） | {o["size_mb"]} | ✅ |'
        )
    lines.append('')
    lines.append('---')
    lines.append('')

    # 使用说明
    lines.append('## 使用说明')
    lines.append('')
    lines.append('- **场景引用**：阶段 07 的 ref-images 槽位-场景使用 `./03-scenes/{目录名}/main.png`')
    lines.append('- **角色引用**：阶段 07 的 ref-images 槽位-角色使用 `./04-character/{目录名}/multiview.png`')
    lines.append('- **音频引用**：阶段 07 的 --audio 使用 `./04-character/{目录名}/voice-ref.mp3`')
    lines.append('')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='扫描项目目录，生成/更新 ASSETS-INDEX.md',
    )
    parser.add_argument('project', type=Path, help='项目根目录路径')
    parser.add_argument('--write', action='store_true',
                        help='写入 ASSETS-INDEX.md（否则只打印预览到 stdout）')
    parser.add_argument('--check', action='store_true',
                        help='检查模式：与现有文件比对，不一致则 exit 1')
    args = parser.parse_args()

    project_dir = args.project
    if not project_dir.is_dir():
        print(f'错误：项目目录不存在：{project_dir}', file=sys.stderr)
        sys.exit(2)

    project_name = project_dir.name
    scenes = scan_scenes(project_dir)
    main_chars, extras = scan_characters(project_dir)
    videos = scan_videos(project_dir)
    outputs = scan_outputs(project_dir)

    index_path = project_dir / 'ASSETS-INDEX.md'
    existing_remarks = load_existing_remarks(index_path)

    new_content = render(
        project_name, scenes, main_chars, extras, videos, outputs,
        existing_remarks,
    )

    if args.check:
        if not index_path.is_file():
            print(f'❌ ASSETS-INDEX.md 不存在：{index_path}', file=sys.stderr)
            sys.exit(1)
        current = index_path.read_text(encoding='utf-8')
        # 比较时忽略"最后更新"日期行，只比较结构
        strip_date = lambda t: re.sub(r'> 最后更新：[^\n]+\n', '', t)
        if strip_date(current) == strip_date(new_content):
            print('✅ ASSETS-INDEX.md 与实际资产一致')
            sys.exit(0)
        else:
            print('⚠️  ASSETS-INDEX.md 与实际资产存在差异', file=sys.stderr)
            print('   运行 `regen_assets_index.py <项目> --write` 查看预览', file=sys.stderr)
            print('   注意：脚本按字母序排列角色，若现有文件按"剧情重要性"排序，', file=sys.stderr)
            print('         差异可能仅是顺序问题，非结构问题', file=sys.stderr)
            sys.exit(1)

    if args.write:
        index_path.write_text(new_content, encoding='utf-8')
        print(f'✅ 已写入 {index_path}')
    else:
        print(new_content)


if __name__ == '__main__':
    main()
