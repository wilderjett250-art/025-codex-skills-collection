#!/usr/bin/env python3
"""从 seg-config.py 单源渲染 assets.md 段详情骨架。

用途：
  治理教训 #15（prompt 双写）的根因。seg-config.py 是执行输入（batch_gen 吃），
  assets.md 是审计凭证（门禁 2）。不要求 AI 手动同步两份——从 seg-config.py 单向 render。

行为：
  - 读取 `05-videos/ep{NN}/seg-config.py`
  - 生成每个 seg 的段详情块骨架：
    * #### Prompt (v1, 当前) 代码块
    * #### ref-images（逻辑槽位 → 物理编号）表
    * #### audio 区段
    * #### 命令参数 代码块
    * #### 版本历史 表（只含 v1 待填行）
  - 默认模式：只更新"段详情块的 Prompt/ref-images/audio/命令参数"，不碰"片段划分表"和"版本历史"
    （因为这些由 batch_gen.py 的生成结果填入）
  - 首次生成时如 assets.md 不存在，创建完整骨架

用法:
    python3 render_assets.py <项目路径> <集号>
    python3 render_assets.py projects/bengong-kaidian 03

参数:
    --dry-run   不写入，打印结果到 stdout
    --force-init  强制重新生成整个 assets.md（覆盖现有；用于初次导入）

⚠️ 警告：
  - 不要在生成已开始后跑 --force-init（会丢失 task_id + 版本历史）
  - 默认模式安全：只同步 prompt 和 ref-images 等"Step 4 应双写但人工易忘"的字段
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
from pathlib import Path
from typing import Optional


def load_config(config_path: Path):
    """从 seg-config.py 动态加载（与 batch_gen.py 一致）。"""
    spec = importlib.util.spec_from_file_location("seg_config", str(config_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f'无法加载 {config_path}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    required = ["STYLE", "NO_MARK", "CHARS", "SCENES", "SEGS"]
    missing = [r for r in required if not hasattr(mod, r)]
    if missing:
        raise RuntimeError(f'配置缺失变量: {missing}')
    return mod


def _get_visible_chars(seg):
    """读取"画面中可辨识角色"（兼容新旧字段：visible_chars → chars）。"""
    if 'visible_chars' in seg:
        return seg.get('visible_chars') or []
    return seg.get('chars') or []


def _get_speaking_chars(seg):
    """读取"说话角色"（兼容新旧字段：speaking_chars → audio）。"""
    if 'speaking_chars' in seg:
        return seg.get('speaking_chars') or []
    return seg.get('audio') or []


def build_full_prompt(seg: dict, config) -> str:
    """拼接完整 prompt（与 batch_gen.py 保持一致的拼接规则）。"""
    style = getattr(config, 'STYLE', '').strip()
    no_mark = getattr(config, 'NO_MARK', '').strip()
    body = seg.get('prompt', '').strip()
    parts = []
    if style:
        parts.append(style)
    if no_mark:
        parts.append(no_mark)
    if body:
        parts.append(body)
    return '\n\n'.join(parts)


def build_ref_images_table(seg: dict, config, proj_dir: Path, ep_rel: str) -> list[tuple[str, str, str]]:
    """构建 (逻辑槽位, 物理编号, 文件路径) 的列表。

    顺序：场景 → 角色A → 角色B → 起始画面 → 补充
    缺失的槽位跳过，物理编号按实际传入顺序计算。
    """
    rows: list[tuple[str, str, str]] = []
    phys_idx = 1

    # 1. 场景
    scene_key = seg.get('scene')
    if scene_key:
        scene_dir = config.SCENES[scene_key].rstrip('/')
        rows.append(('槽位-场景', f'图片{phys_idx}', f'./{scene_dir}/main.png'))
        phys_idx += 1

    # 2. 角色（visible_chars 列表顺序，兼容旧字段 chars）
    chars = _get_visible_chars(seg)
    slot_names = ['槽位-角色A', '槽位-角色B', '槽位-角色C', '槽位-角色D', '槽位-角色E']
    for i, char_key in enumerate(chars):
        char_dir = config.CHARS[char_key].rstrip('/')
        slot = slot_names[i] if i < len(slot_names) else f'槽位-角色{i+1}'
        rows.append((slot, f'图片{phys_idx}', f'./{char_dir}/multiview.png'))
        phys_idx += 1

    # 3. 起始画面
    start_frame = seg.get('start_frame')
    if start_frame is not None:
        rows.append((
            '槽位-起始画面',
            f'图片{phys_idx}',
            f'./{ep_rel}/lastframe_seg{start_frame}.png',
        ))
        phys_idx += 1

    # 4. 补充参考图
    extras = seg.get('extras') or []
    for extra in extras:
        path = extra if os.path.isabs(extra) else f'./{extra}'
        rows.append(('槽位-补充', f'图片{phys_idx}', path))
        phys_idx += 1

    return rows


def build_audio_lines(seg: dict, config) -> list[str]:
    """构建 audio 区段的行。"""
    audio = _get_speaking_chars(seg)
    if not audio:
        return []
    lines = []
    for i, char_key in enumerate(audio):
        char_dir = config.CHARS[char_key].rstrip('/')
        lines.append(f'- 音频{i+1}: `./{char_dir}/voice-ref.mp3`')
    return lines


def build_cmd_params(seg: dict) -> dict:
    """推导命令参数。"""
    duration = seg.get('duration', 10)
    params = {
        '--ratio': '9:16',
        '--duration': str(duration),
        '--generate-audio': 'true',
        '--return-last-frame': 'true',
    }
    if _get_speaking_chars(seg):
        params['--audio'] = '（见上方 audio 区段）'
    return params


def render_seg_detail(seg: dict, config, proj_dir: Path, ep_rel: str) -> str:
    """渲染单个 seg 的段详情块骨架。"""
    seg_id = seg['id']
    lines = []
    lines.append(f'### seg-{seg_id}')
    lines.append('')
    lines.append(f'**时长**：{seg.get("duration", "?")}s')
    if seg.get('scene'):
        lines.append(f'**场景**：{seg["scene"]}')
    lines.append(f'**首帧来源**：' +
                 ('文生视频' if seg.get('start_frame') is None
                  else f'seg-{seg["start_frame"]} 尾帧'))
    lines.append(f'**依赖**：' +
                 ('—' if seg.get('start_frame') is None
                  else f'seg-{seg["start_frame"]}'))
    lines.append('')

    # Prompt
    lines.append('#### Prompt (v1, 当前)')
    lines.append('')
    lines.append('```text')
    lines.append(build_full_prompt(seg, config))
    lines.append('```')
    lines.append('')

    # ref-images
    lines.append('#### ref-images（逻辑槽位 → 物理编号）')
    lines.append('')
    lines.append('| 逻辑槽位 | 物理编号 | 文件路径 |')
    lines.append('|---------|---------|----------|')
    for slot, phys, path in build_ref_images_table(seg, config, proj_dir, ep_rel):
        lines.append(f'| {slot} | {phys} | `{path}` |')
    lines.append('')

    # audio
    lines.append('#### audio')
    lines.append('')
    audio_lines = build_audio_lines(seg, config)
    if audio_lines:
        lines.extend(audio_lines)
    else:
        lines.append('无（无人声段）')
    lines.append('')

    # 命令参数
    lines.append('#### 命令参数')
    lines.append('')
    lines.append('```')
    for k, v in build_cmd_params(seg).items():
        lines.append(f'{k} {v}')
    lines.append('```')
    lines.append('')

    # 版本历史
    lines.append('#### 版本历史')
    lines.append('')
    lines.append('| 版本 | task_id | seed | 时间 | 说明 |')
    lines.append('|------|---------|------|------|------|')
    lines.append('| v1 | — | — | — | 待生成 |')
    lines.append('')

    return '\n'.join(lines)


def render_division_table(config) -> str:
    """渲染片段划分表骨架（状态全 pending）。"""
    lines = []
    lines.append('## 片段划分表')
    lines.append('')
    lines.append('| seg | 时长 | 状态 | task_id | seed | 首帧来源 | 依赖 | 备注 |')
    lines.append('|-----|------|------|---------|------|---------|------|------|')
    for seg in config.SEGS:
        source = '文生视频' if seg.get('start_frame') is None \
            else f'seg-{seg["start_frame"]} 尾帧'
        dep = '—' if seg.get('start_frame') is None else f'seg-{seg["start_frame"]}'
        duration = seg.get('duration', '?')
        lines.append(
            f'| {seg["id"]} | {duration}s | pending | — | — | {source} | {dep} |  |'
        )
    lines.append('')
    return '\n'.join(lines)


SEG_BLOCK_RE = re.compile(
    r'(^### seg-(\d+)\s*$\n.*?)(?=^### seg-\d+\s*$|^\Z|^##\s)',
    re.MULTILINE | re.DOTALL,
)


def merge_seg_details(existing: str, new_details: dict[int, str]) -> str:
    """合并模式：只替换现有 assets.md 里每个 seg 的"段详情"（### seg-N 块），
    保留 version 表中的 task_id + seed + 实际生成记录。

    简化策略：对每个 seg 块，替换 #### Prompt 块 + #### ref-images 块 + #### audio 块 +
    #### 命令参数 块（这四个是"Step 4 应双写"的内容）；保留 #### 版本历史。
    """
    def replace_block(match):
        block = match.group(1)
        seg_id = int(match.group(2))
        if seg_id not in new_details:
            return block
        new_full = new_details[seg_id]

        # 从 new_full 中提取前 4 个子区段（Prompt / ref-images / audio / 命令参数）
        # 分隔符：`#### ` 开头
        new_parts = re.split(r'(?=^#### )', new_full, flags=re.MULTILINE)
        # new_parts[0] 是 header（### seg-N 行和基础信息），接下来是若干 #### XX 块
        # 取前 4 个 #### 块
        headers = [p for p in new_parts if p.startswith('#### ')]
        new_top_four = ''.join(headers[:4])  # Prompt/ref-images/audio/命令参数

        # 在现有 block 中，找到"### seg-N"header 到第一个 #### 之间的内容（基础信息）保留
        existing_parts = re.split(r'(?=^#### )', block, flags=re.MULTILINE)
        existing_header = existing_parts[0]
        existing_sub = [p for p in existing_parts if p.startswith('#### ')]

        # 找出版本历史块
        version_block = ''
        for p in existing_sub:
            if '版本历史' in p.split('\n', 1)[0]:
                version_block = p
                break
        if not version_block and len(headers) > 4:
            version_block = headers[4]  # 如果现有没有版本历史，用 new 的 v1 骨架

        # 取新的 header（包含更新后的"场景/首帧来源/依赖"等），替换现有 header
        new_header = new_parts[0] if new_parts else existing_header

        return new_header + new_top_four + version_block

    return SEG_BLOCK_RE.sub(replace_block, existing)


def init_full(config, proj_dir: Path, ep_num: str, ep_rel: str) -> str:
    """首次生成完整 assets.md。"""
    lines = []
    lines.append(f'# EP{ep_num} 视频资产清单')
    lines.append('')
    lines.append('> 由 render_assets.py 从 seg-config.py 生成。')
    lines.append('> 生成完成后，batch_gen.py 会更新片段划分表的状态/task_id/seed 和版本历史。')
    lines.append('')
    lines.append(render_division_table(config))
    lines.append('## 段详情')
    lines.append('')
    for seg in config.SEGS:
        lines.append(render_seg_detail(seg, config, proj_dir, ep_rel))
        lines.append('')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='从 seg-config.py 渲染 assets.md 段详情骨架',
    )
    parser.add_argument('project', type=Path, help='项目根目录')
    parser.add_argument('ep_num', type=str, help='集号（如 03）')
    parser.add_argument('--dry-run', action='store_true',
                        help='打印结果到 stdout，不写入')
    parser.add_argument('--force-init', action='store_true',
                        help='强制重新生成整个 assets.md（丢失现有 task_id/seed）')
    args = parser.parse_args()

    proj_dir = args.project.resolve()
    ep_num = args.ep_num.zfill(2)
    ep_rel = f'05-videos/ep{ep_num}'
    ep_dir = proj_dir / ep_rel

    config_path = ep_dir / 'seg-config.py'
    assets_path = ep_dir / 'assets.md'

    if not config_path.is_file():
        print(f'错误：配置文件不存在 {config_path}', file=sys.stderr)
        sys.exit(2)

    config = load_config(config_path)

    if not assets_path.is_file() or args.force_init:
        new_content = init_full(config, proj_dir, ep_num, ep_rel)
        mode = '初始化' if not assets_path.is_file() else '强制重建'
    else:
        existing = assets_path.read_text(encoding='utf-8')
        new_details = {
            seg['id']: render_seg_detail(seg, config, proj_dir, ep_rel)
            for seg in config.SEGS
        }
        new_content = merge_seg_details(existing, new_details)
        mode = '合并更新'

    if args.dry_run:
        print(new_content)
        return

    assets_path.write_text(new_content, encoding='utf-8')
    print(f'✅ {mode} {assets_path}（共 {len(config.SEGS)} seg）')


if __name__ == '__main__':
    main()
