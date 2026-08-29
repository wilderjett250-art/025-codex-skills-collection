#!/usr/bin/env python3
"""剧本一致性校验工具（阶段 05 验收）。

用途：
  - 扫描剧本正文中所有引号对白
  - 对照剧本末尾"对白汇总"表
  - 检查差异，输出哪些对白被遗漏登记

治理的教训：MEMORY.md #16 — "对白/动作覆盖自检必须以剧本正文为准"。
阶段 05 人工扫描脆弱，用脚本做机械检查。

用法:
    python3 validate_script.py <script.md>
    python3 validate_script.py projects/xxx/01-scripts/ep03-script.md

输出示例:
    正文对白扫描：12 条
    汇总表对白：10 条
    差异：2 条仅在正文出现

    [3-30s] 太监: "皇上有旨，新入宫嫔妃逐一上前请安" — 疑似功能性对白未登记
    [45-50s] 众嫔妃: "参见皇上" — 疑似群体齐声对白未登记

    建议：补登到对白汇总表，角色列标注 [功能性] 或 [群体]

退出码:
    0 — 正文与汇总表一致
    1 — 存在差异（CI 可据此阻止进入阶段 07）
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# 正文对白匹配：只认"真对白"——引号前紧跟中文冒号（：）、英文冒号(:)、或说话动词
# 避免把正文里用引号做关键词强调的部分当成对白
# 真对白常见格式：
#   沈鹿溪：["台词"]
#   沈鹿溪（表情）："台词"
#   沈鹿溪说道："台词"
#   沈鹿溪轻声："台词"
#
# 策略：
# 1. 对白台词不跨段落（限制不含换行符），避免正则跨行贪婪匹配
# 2. 对白内不含双引号（配对就终止）
# 3. 前缀必须是说话动词或"）：" 结构（更严格，排除镜头意图里的关键词引用）
SAY_VERBS = r'(?:说道|道|说|问|答|喊|叫|嚷|低语|低声|轻声|嘀咕|嘟囔|大叫|吼|骂|哼|呢喃|喃喃|念|念道|暗想|心想|宣布|宣|宣读|报|禀报|禀|回禀|呼|唤|呼唤|叹|叹息|笑言|笑道)'

# 真对白：前面必须是 `角色名说动词 + 冒号` 或 `角色名（描述）： `
# 台词本身不跨行、不含双引号
BODY_QUOTE_RE = re.compile(
    # 情况 A: 冒号在前（角色名：或 角色名（...）：）
    r'(?:[^"\n\|]{1,30}[：:])\s*"([^"\n]{2,}?)"'
    + r'|'
    # 情况 B: 说话动词在前
    + r'(?:' + SAY_VERBS + r')\s*[:：]?\s*"([^"\n]{2,}?)"'
)

# 时间戳（格式 【{start}-{end}s，共{n}s】 或 [{start}-{end}s]）
TIME_MARKER_RE = re.compile(r'[【\[]\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*s')

# 汇总表行匹配（对白汇总下面的 markdown 表）
# 格式: | 时间 | 时长 | 角色 | 台词 | ... |
SUMMARY_ROW_RE = re.compile(
    r'^\|\s*([\d\.]+\s*-\s*[\d\.]+\s*s)\s*\|[^|]*\|\s*([^|]+?)\s*\|\s*"?([^"|]+?)"?\s*\|',
    re.MULTILINE,
)


@dataclass
class DialogueItem:
    """一句对白（正文或汇总表）。"""

    text: str                # 台词原文，已去首尾空白
    time_range: Optional[tuple[float, float]] = None  # (start, end) 秒
    character: Optional[str] = None  # 角色（仅汇总表有）
    source: str = "body"     # "body" 或 "summary"

    @property
    def normalized(self) -> str:
        """归一化文本用于比对：去全部空白、去标点（保留中文字符）。"""
        return re.sub(r'[\s，。！？、：；…~—\-"""\'\'【】\[\]（）()]+', '', self.text)


def extract_timeline_body(content: str) -> str:
    """截取剧本的"正文时间轴"部分——只扫描这部分的对白。

    正文时间轴：从 `## 时间轴` 开始，到下一个不是时间轴延伸的 `##` 为止。
    排除：`## 对白汇总`、`## 吸引力自检`、`## 时长分配校验`、`## 场景合理性检查` 等元数据段。
    """
    m = re.search(r'##\s*时间轴[^\n]*\n', content)
    if not m:
        # 没有明确的时间轴标题，退回全文扫描
        return content

    start = m.end()
    # 找下一个 ## 段（终点）
    next_section = re.search(r'^##\s', content[start:], re.MULTILINE)
    if next_section:
        return content[start:start + next_section.start()]
    return content[start:]


def extract_body_dialogues(content: str) -> list[DialogueItem]:
    """从剧本正文提取所有引号对白，并尽量关联到最近的上文时间段。"""
    # 找出所有时间戳的位置
    time_markers = [
        (m.start(), float(m.group(1)), float(m.group(2)))
        for m in TIME_MARKER_RE.finditer(content)
    ]

    items: list[DialogueItem] = []
    for m in BODY_QUOTE_RE.finditer(content):
        start_pos = m.start()
        # 两个捕获组（情况 A 或 B），取非 None 的那个
        text = (m.group(1) or m.group(2) or '').strip()
        # 跳过纯标点或太短的内容
        if len(text) < 2:
            continue
        # 跳过看起来像文档引用的（"xxx.md"、"图片N" 等）
        if re.search(r'\.(md|png|jpg|mp4|mp3|py|sh|json)$', text, re.IGNORECASE):
            continue
        if re.fullmatch(r'图片\d+', text):
            continue

        # 找到当前位置之前最近的时间戳
        time_range: Optional[tuple[float, float]] = None
        for tm_pos, tm_start, tm_end in reversed(time_markers):
            if tm_pos < start_pos:
                time_range = (tm_start, tm_end)
                break

        items.append(DialogueItem(text=text, time_range=time_range, source="body"))

    return items


def find_summary_table(content: str) -> Optional[str]:
    """定位"对白汇总"表的内容（markdown 表格）。"""
    # 找到"对白汇总"标题，然后截取到下一个 ## 或文件结束
    m = re.search(r'##\s*对白汇总[^\n]*\n', content)
    if not m:
        return None
    start = m.end()
    next_section = re.search(r'^##\s', content[start:], re.MULTILINE)
    if next_section:
        return content[start:start + next_section.start()]
    return content[start:]


def extract_summary_dialogues(content: str) -> list[DialogueItem]:
    """从对白汇总表提取所有对白条目。"""
    table = find_summary_table(content)
    if not table:
        return []

    items: list[DialogueItem] = []
    for m in SUMMARY_ROW_RE.finditer(table):
        time_str = m.group(1).strip()
        character = m.group(2).strip()
        text = m.group(3).strip()

        # 跳过表头（| 时间 | 时长 | 角色 | 台词 |）
        if character in ('角色', '---', ''):
            continue

        time_range = None
        tm = re.match(r'([\d\.]+)\s*-\s*([\d\.]+)', time_str)
        if tm:
            time_range = (float(tm.group(1)), float(tm.group(2)))

        items.append(DialogueItem(
            text=text, time_range=time_range,
            character=character, source="summary"
        ))

    return items


def match_dialogues(body: list[DialogueItem], summary: list[DialogueItem]):
    """按归一化文本匹配正文 vs 汇总表。

    返回:
        body_only: 只在正文出现的条目
        summary_only: 只在汇总表出现的条目
        matched: 匹配上的 (body, summary) 对
    """
    summary_by_norm = {item.normalized: item for item in summary}
    body_only = []
    matched = []
    matched_summary_norms = set()

    for bitem in body:
        norm = bitem.normalized
        if norm in summary_by_norm:
            matched.append((bitem, summary_by_norm[norm]))
            matched_summary_norms.add(norm)
        else:
            body_only.append(bitem)

    summary_only = [
        s for s in summary
        if s.normalized not in matched_summary_norms
    ]
    return body_only, summary_only, matched


def format_item(item: DialogueItem) -> str:
    """格式化输出一条对白。"""
    time_str = ''
    if item.time_range:
        time_str = f'[{item.time_range[0]:g}-{item.time_range[1]:g}s] '
    char_str = f'{item.character}: ' if item.character else ''
    return f'{time_str}{char_str}"{item.text}"'


def validate(script_path: Path) -> int:
    if not script_path.is_file():
        print(f'错误：文件不存在：{script_path}', file=sys.stderr)
        return 2

    content = script_path.read_text(encoding='utf-8')

    body = extract_body_dialogues(extract_timeline_body(content))
    summary = extract_summary_dialogues(content)

    body_only, summary_only, matched = match_dialogues(body, summary)

    print(f'正文对白扫描：{len(body)} 条')
    print(f'汇总表对白：{len(summary)} 条')
    print(f'匹配上：{len(matched)} 条')
    print()

    has_diff = False

    if body_only:
        has_diff = True
        print(f'⚠️  仅在正文出现（疑似未登记汇总表）：{len(body_only)} 条')
        for item in body_only:
            print(f'   - {format_item(item)}')
        print()
        print('   建议：补登到对白汇总表。功能性对白（宣旨/旁白/广播）的')
        print('   "角色"列后加 [功能性] 标记；群体齐声对白角色列写"群体"。')
        print()

    if summary_only:
        has_diff = True
        print(f'⚠️  仅在汇总表出现（疑似正文遗漏）：{len(summary_only)} 条')
        for item in summary_only:
            print(f'   - {format_item(item)}')
        print()
        print('   建议：检查汇总表是否登记了不存在的对白，或正文里对白被删除时未同步汇总表。')
        print()

    if not has_diff:
        print('✅ 正文对白与汇总表完全一致')
        return 0

    print('='*60)
    print('❌ 校验未通过。阶段 05 验收要求正文和汇总表一致。')
    print('   遗漏会导致阶段 07 seg 切分时漏掉对白（见 MEMORY.md 教训 #16）。')
    return 1


def main():
    parser = argparse.ArgumentParser(
        description='剧本一致性校验：扫描正文引号对白，对照对白汇总表',
    )
    parser.add_argument('script', type=Path, help='剧本文件路径 (ep{NN}-script.md)')
    args = parser.parse_args()
    sys.exit(validate(args.script))


if __name__ == '__main__':
    main()
