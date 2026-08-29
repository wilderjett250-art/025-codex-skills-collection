#!/usr/bin/env python3
"""assets.md 解析与更新工具（视频 seg 专用）。

按照 `_convention.md` 定义的标准格式解析 `05-videos/ep{NN}/assets.md`：
- 片段划分表：`| seg | ... |`
- seg 详情块：`### seg-{N}` 下包含 Prompt 代码块、ref-images 列表、audio 列表、版本历史表

命令:
  get-prompt <assets_path> <seg_num>              输出 seg 当前 prompt
  get-refs <assets_path> <seg_num> <project_dir>  输出 seg ref-images 列表（每行一个文件路径）
  get-audios <assets_path> <seg_num> <project>    输出 seg audio 列表
  get-task-id <assets_path> <seg_num>             输出 seg 最新 task_id
  append-version <assets_path> <seg_num> --task-id <id> [--seed <n>] [--new-prompt-file <path>]
                                                   追加新版本到版本历史表；如有新 prompt，追加 Prompt (vN) 块
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


SEG_BLOCK_RE = re.compile(r"^### seg-(\d+)\s*$", re.MULTILINE)
PROMPT_BLOCK_RE = re.compile(
    r"####\s*Prompt\s*\((v\d+),\s*当前\)\s*\n+```[^\n]*\n(.*?)\n```",
    re.DOTALL,
)
PROMPT_HIST_RE = re.compile(
    r"####\s*Prompt\s*\((v\d+),\s*历史\)\s*\n+```[^\n]*\n(.*?)\n```",
    re.DOTALL,
)
# 兼容旧格式：`#### Prompt` 不带版本号
PROMPT_LEGACY_RE = re.compile(r"####\s*Prompt\s*\n+```[^\n]*\n(.*?)\n```", re.DOTALL)

# 旧格式（legacy）：`- 图片N（槽位X-标签）: path`
REF_LEGACY_RE = re.compile(r"^-\s*图片(\d+)[^:：]*[:：]\s*`?([^`\n]+?)`?\s*$", re.MULTILINE)
# 新格式（v2）：markdown 表格 `| 逻辑槽位 | 物理编号 | 文件路径 |`
# 匹配物理编号列（图片N 或 —）和 文件路径列
REF_TABLE_ROW_RE = re.compile(
    r"^\|\s*(槽位-[^\s|]+)\s*\|\s*(图片\d+|—|-)\s*\|\s*`?([^`\n|]*?)`?\s*\|",
    re.MULTILINE,
)
AUDIO_ITEM_RE = re.compile(r"^-\s*音频(\d+)[^:：]*[:：]\s*`?([^`\n]+?)`?\s*$", re.MULTILINE)


@dataclass
class SegBlock:
    seg_num: str
    start: int  # 块起始字符位置（含 ### 行）
    end: int  # 块结束字符位置（下一个 ### 或 EOF 前）
    text: str  # 块正文


def find_seg_block(content: str, seg_num: str) -> Optional[SegBlock]:
    """定位 ### seg-N 块的范围。"""
    matches = list(SEG_BLOCK_RE.finditer(content))
    for i, m in enumerate(matches):
        if m.group(1) == seg_num:
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            return SegBlock(seg_num=seg_num, start=start, end=end, text=content[start:end])
    return None


def extract_prompt(block: SegBlock) -> Optional[str]:
    """提取 seg 当前 prompt。优先找 (vN, 当前)，fallback 到 legacy 格式。"""
    m = PROMPT_BLOCK_RE.search(block.text)
    if m:
        return m.group(2).strip()
    m = PROMPT_LEGACY_RE.search(block.text)
    if m:
        return m.group(1).strip()
    return None


def extract_refs(block: SegBlock, project_dir: str) -> list[str]:
    """提取 ref-images 列表，返回可用文件路径（跳过缺失的槽位）。

    优先解析新格式（表格 `| 逻辑槽位 | 物理编号 | 文件路径 |`），
    退化到旧格式（`- 图片N: path`）。

    传入 Seedance 的顺序 = 槽位固定顺序（场景→角色A→角色B→起始画面→补充），
    跳过缺失槽位。
    **补充槽位可多行**——同一"槽位-补充"名字可出现多行，按物理编号排序返回。
    兼容旧命名 "槽位-尾帧"（向前兼容）。
    """
    # 尝试新格式：按表格行顺序提取
    table_rows = REF_TABLE_ROW_RE.findall(block.text)
    if table_rows:
        refs = []
        # 固定顺序过滤：场景→角色A→角色B→起始画面→补充（补充可多张）
        slot_order_new = ["槽位-场景", "槽位-角色A", "槽位-角色B", "槽位-起始画面", "槽位-补充"]
        slot_order_legacy_alias = {"槽位-尾帧": "槽位-起始画面"}

        # 按槽位分组收集（补充槽位可多行）
        slot_groups: dict[str, list[tuple[str, str]]] = {}
        for slot, idx, path in table_rows:
            normalized = slot_order_legacy_alias.get(slot, slot)
            slot_groups.setdefault(normalized, []).append((idx, path))

        for slot in slot_order_new:
            if slot not in slot_groups:
                continue
            # 按物理编号排序该槽位的所有行（补充可多张）
            def _idx_key(row):
                m = re.match(r"图片(\d+)", row[0])
                return int(m.group(1)) if m else 0
            for idx, path in sorted(slot_groups[slot], key=_idx_key):
                path = path.strip()
                if idx in ("—", "-") or path in ("—", "-", ""):
                    continue
                if path.startswith("./"):
                    full = Path(project_dir) / path[2:]
                elif not path.startswith("/"):
                    full = Path(project_dir) / path
                else:
                    full = Path(path)
                refs.append(str(full))
        return refs

    # 退化到旧格式
    items = REF_LEGACY_RE.findall(block.text)
    items.sort(key=lambda x: int(x[0]))
    refs = []
    for _, path in items:
        path = path.strip()
        if path == "—" or path == "-" or not path:
            continue
        if path.startswith("./"):
            full = Path(project_dir) / path[2:]
        elif not path.startswith("/"):
            full = Path(project_dir) / path
        else:
            full = Path(path)
        refs.append(str(full))
    return refs


def extract_audios(block: SegBlock, project_dir: str) -> list[str]:
    """提取 audio 列表。"""
    items = AUDIO_ITEM_RE.findall(block.text)
    items.sort(key=lambda x: int(x[0]))
    audios = []
    for _, path in items:
        path = path.strip()
        if path == "—" or path == "-" or not path:
            continue
        if path.startswith("./"):
            full = Path(project_dir) / path[2:]
        elif not path.startswith("/"):
            full = Path(project_dir) / path
        else:
            full = Path(path)
        audios.append(str(full))
    return audios


def get_latest_task_id(block: SegBlock) -> Optional[str]:
    """从版本历史表获取最新 task_id。版本历史表表头：| 版本 | task_id | seed | 时间 | 说明 |"""
    # 找到 "| 版本 | task_id |" 表格
    lines = block.text.split("\n")
    table_start = None
    for i, line in enumerate(lines):
        if re.match(r"\|\s*版本\s*\|\s*task_id\s*\|", line):
            table_start = i
            break
    if table_start is None:
        # 退化：查找片段划分表中该 seg 的 task_id
        return None
    # 收集所有 | vN | task_xxx | 行，取最后一行
    last_task = None
    for line in lines[table_start + 2 :]:  # 跳过表头和分隔符
        if not line.strip().startswith("|"):
            break
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 2:
            task = cells[1]
            if task and task not in ("—", "-", ""):
                last_task = task
    return last_task


def get_current_version(block: SegBlock) -> int:
    """获取当前最高版本号（从版本历史表的 vN 中提取 N）。"""
    versions = re.findall(r"\|\s*v(\d+)\s*\|", block.text)
    if not versions:
        return 0
    return max(int(v) for v in versions)


def get_seg_num_from_cmdline(n: str) -> str:
    """规范化 seg 编号（允许传入 3 或 seg-3 或 seg3）。"""
    m = re.match(r"^(?:seg[-_]?)?(\d+)$", n, re.IGNORECASE)
    if m:
        return m.group(1)
    return n


def find_downstream_segs(content: str, seg_num: str) -> list[str]:
    """找出所有依赖于 seg_num 的下游 seg 编号列表。

    从片段划分表的"依赖"列解析。依赖格式如 `seg-3` 或 `seg-1 尾帧`。
    """
    downstream = []
    lines = content.split("\n")
    in_table = False
    header_cols = None
    for line in lines:
        if re.match(r"\|\s*seg\s*\|\s*时长\s*\|", line):
            in_table = True
            header_cols = [c.strip() for c in line.strip("|").split("|")]
            continue
        if in_table and line.strip().startswith("|") and not re.match(r"\|[-\s|]+\|", line):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < len(header_cols):
                continue
            try:
                dep_idx = header_cols.index("依赖")
            except ValueError:
                continue
            dep_cell = cells[dep_idx]
            # 匹配 "seg-N" 或 "seg-N 尾帧" 格式
            m = re.search(r"seg-(\d+)", dep_cell)
            if m and m.group(1) == seg_num:
                downstream.append(cells[0])
        elif in_table and not line.strip().startswith("|"):
            in_table = False
    return downstream


def cmd_find_downstream(args):
    """查找依赖指定 seg 的下游 seg 列表。"""
    content = Path(args.assets).read_text()
    seg = get_seg_num_from_cmdline(args.seg)
    downstream = find_downstream_segs(content, seg)
    for s in downstream:
        print(s)


def append_version(
    assets_path: Path,
    seg_num: str,
    task_id: str,
    seed: Optional[str] = None,
    new_prompt: Optional[str] = None,
) -> bool:
    """
    在 assets.md 中追加新版本到版本历史表。
    - 如果 new_prompt 不为 None：将旧 `#### Prompt (vN, 当前)` 改为 `(vN, 历史)`，追加新 `(v(N+1), 当前)` 块
    - 版本历史表追加一行
    - 片段划分表的 task_id/seed/状态列更新
    """
    content = assets_path.read_text()
    block = find_seg_block(content, seg_num)
    if block is None:
        print(f"未找到 seg-{seg_num} 块", file=sys.stderr)
        return False

    current_v = get_current_version(block)
    next_v = current_v + 1 if new_prompt else current_v if current_v > 0 else 1

    new_block_text = block.text
    # 处理新 prompt：旧 (vN, 当前) → (vN, 历史)，追加 (v(N+1), 当前) 块
    if new_prompt:
        # 将当前块的 "当前" 标记改为 "历史"
        new_block_text = re.sub(
            r"(####\s*Prompt\s*\(v\d+),\s*当前\)",
            r"\1, 历史)",
            new_block_text,
            count=1,
        )
        # 在版本历史表之前插入新 prompt 块
        hist_table_m = re.search(r"####\s*版本历史", new_block_text)
        new_prompt_block = f"\n#### Prompt (v{next_v}, 当前)\n\n```text\n{new_prompt.strip()}\n```\n"
        if hist_table_m:
            insert_pos = hist_table_m.start()
            new_block_text = new_block_text[:insert_pos] + new_prompt_block + "\n" + new_block_text[insert_pos:]
        else:
            # 没有版本历史表，追加到块末尾
            new_block_text += new_prompt_block

    # 追加版本历史表行
    ts = datetime.now().strftime("%Y-%m-%d")
    seed_str = seed if seed else "—"
    new_row = f"| v{next_v} | {task_id} | {seed_str} | {ts} | 重新生成 |"

    # 找到版本历史表
    hist_re = re.compile(
        r"(####\s*版本历史\s*\n+\|\s*版本\s*\|[^\n]+\|\s*\n\|[-\s|]+\|\s*\n)((?:\|[^\n]+\|\s*\n)+)"
    )
    m = hist_re.search(new_block_text)
    if m:
        table_header = m.group(1)
        table_rows = m.group(2)
        # 确保表格后保留空行与下一块分隔
        tail = new_block_text[m.end() :]
        if not tail.startswith("\n\n"):
            tail = "\n" + tail.lstrip("\n")
        new_block_text = (
            new_block_text[: m.start()]
            + table_header
            + table_rows.rstrip()
            + "\n"
            + new_row
            + "\n"
            + tail
        )
    else:
        # 没有版本历史表，新建一个
        new_table = (
            "\n#### 版本历史\n\n"
            "| 版本 | task_id | seed | 时间 | 说明 |\n"
            "|------|---------|------|------|------|\n"
            f"| v{next_v} | {task_id} | {seed_str} | {ts} | 重新生成 |\n"
        )
        new_block_text += new_table

    # 替换原块
    new_content = content[: block.start] + new_block_text + content[block.end :]

    # 同步更新片段划分表（如果有的话）
    # 匹配 | N | ... | status | task_id | seed | ... | 或类似结构
    divider_table_re = re.compile(
        r"(\|\s*" + re.escape(seg_num) + r"\s*\|[^\n]+?\|\s*)(pending|completed|[^\|\s]+)(\s*\|\s*)([^\|]+?)(\s*\|\s*)([^\|]+?)(\s*\|[^\n]*)"
    )

    def replace_row(m):
        # 保留其他列，更新 status/task_id/seed
        # 这里简化处理，按表头顺序匹配：| seg | 时长 | 状态 | task_id | seed | 首帧来源 | 依赖 | 备注 |
        # 仅更新 "状态/task_id/seed" 三列
        # 输入 m 捕获复杂度高，改用精准替换策略
        return m.group(0)  # 占位，实际替换由下面函数处理

    # 精准替换片段划分表行：找到含 | {seg_num} | 的行，分割 cells 后改第 2/3/4 列（基于 0-index 且第 0 列是空）
    def update_divider_table(text: str) -> str:
        lines = text.split("\n")
        in_table = False
        header_cols = None
        for i, line in enumerate(lines):
            if re.match(r"\|\s*seg\s*\|\s*时长\s*\|", line):
                in_table = True
                header_cols = [c.strip() for c in line.strip("|").split("|")]
                continue
            if in_table and line.strip().startswith("|") and not re.match(r"\|[-\s|]+\|", line):
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) >= len(header_cols) and cells[0] == seg_num:
                    # 定位列
                    try:
                        status_idx = header_cols.index("状态")
                        task_idx = header_cols.index("task_id")
                        seed_idx = header_cols.index("seed")
                        cells[status_idx] = "completed"
                        cells[task_idx] = task_id
                        cells[seed_idx] = seed_str
                        lines[i] = "| " + " | ".join(cells) + " |"
                    except ValueError:
                        pass
            elif in_table and not line.strip().startswith("|"):
                in_table = False
        return "\n".join(lines)

    new_content = update_divider_table(new_content)

    assets_path.write_text(new_content)
    return True


def cmd_get_prompt(args):
    content = Path(args.assets).read_text()
    seg = get_seg_num_from_cmdline(args.seg)
    block = find_seg_block(content, seg)
    if block is None:
        sys.exit(1)
    p = extract_prompt(block)
    if p:
        print(p)
    else:
        sys.exit(1)


def cmd_get_refs(args):
    content = Path(args.assets).read_text()
    seg = get_seg_num_from_cmdline(args.seg)
    block = find_seg_block(content, seg)
    if block is None:
        sys.exit(1)
    for r in extract_refs(block, args.project):
        print(r)


def cmd_get_audios(args):
    content = Path(args.assets).read_text()
    seg = get_seg_num_from_cmdline(args.seg)
    block = find_seg_block(content, seg)
    if block is None:
        sys.exit(1)
    for a in extract_audios(block, args.project):
        print(a)


def cmd_get_task_id(args):
    content = Path(args.assets).read_text()
    seg = get_seg_num_from_cmdline(args.seg)
    block = find_seg_block(content, seg)
    if block is None:
        sys.exit(1)
    t = get_latest_task_id(block)
    if t:
        print(t)


def cmd_append_version(args):
    new_prompt = None
    if args.new_prompt_file:
        new_prompt = Path(args.new_prompt_file).read_text()
    seg = get_seg_num_from_cmdline(args.seg)
    ok = append_version(
        Path(args.assets),
        seg,
        task_id=args.task_id,
        seed=args.seed,
        new_prompt=new_prompt,
    )
    if not ok:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="assets.md 解析与更新工具")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("get-prompt")
    p.add_argument("assets")
    p.add_argument("seg")
    p.set_defaults(func=cmd_get_prompt)

    p = sub.add_parser("get-refs")
    p.add_argument("assets")
    p.add_argument("seg")
    p.add_argument("project")
    p.set_defaults(func=cmd_get_refs)

    p = sub.add_parser("get-audios")
    p.add_argument("assets")
    p.add_argument("seg")
    p.add_argument("project")
    p.set_defaults(func=cmd_get_audios)

    p = sub.add_parser("get-task-id")
    p.add_argument("assets")
    p.add_argument("seg")
    p.set_defaults(func=cmd_get_task_id)

    p = sub.add_parser("append-version")
    p.add_argument("assets")
    p.add_argument("seg")
    p.add_argument("--task-id", required=True)
    p.add_argument("--seed")
    p.add_argument("--new-prompt-file")
    p.set_defaults(func=cmd_append_version)

    p = sub.add_parser("find-downstream", help="列出依赖指定 seg 的下游 seg 编号")
    p.add_argument("assets")
    p.add_argument("seg")
    p.set_defaults(func=cmd_find_downstream)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
