#!/usr/bin/env python3
"""初始化 AI 漫剧项目目录结构。

用法:
    python3 init_project.py <项目名> [--base <项目根目录>] [--from-template <源项目>]

创建标准项目目录 + 复制阶段模板文件 + 写入 STATE.md。

可选的 --from-template 从现有项目复制可复用资产（角色库、场景库、Moodboard、灯光配色、character-bible），
支持同世界观续作复用。
"""

import argparse
import os
import shutil
import sys
from datetime import datetime, timezone, timedelta


CST = timezone(timedelta(hours=8))


# 可复用资产清单（--from-template 时复制这些）
REUSABLE_ASSETS = [
    "04-character",
    "03-scenes",
    "02-moodboard",
    "01-scripts/lighting-philosophy.md",
    "01-scripts/color-palette.md",
    "01-scripts/visual-style-spec.md",
    "01-scripts/character-bible.md",
]


def resolve_base(arg_base):
    """自动检测项目根目录。OpenClaw 用绝对路径，其他环境用当前目录。"""
    if arg_base is not None:
        return arg_base
    if os.path.isdir("/root/.openclaw"):
        return "/root/.openclaw/projects"
    return os.path.join(os.getcwd(), "projects")


def copy_reusable_assets(template_dir, project_dir):
    """从模板项目复制可复用资产。"""
    copied = []
    skipped = []
    for asset in REUSABLE_ASSETS:
        src = os.path.join(template_dir, asset)
        dst = os.path.join(project_dir, asset)
        if not os.path.exists(src):
            skipped.append(asset)
            continue
        # 确保目标父目录存在
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        copied.append(asset)
    return copied, skipped


def main():
    parser = argparse.ArgumentParser(description="初始化 AI 漫剧项目目录")
    parser.add_argument("name", help="项目名称（英文，用于目录名）")
    parser.add_argument(
        "--base",
        default=None,
        help="项目根目录（默认:当前目录下 projects/，OpenClaw 环境为 /root/.openclaw/projects）",
    )
    parser.add_argument(
        "--from-template",
        default=None,
        help="从已有项目复制可复用资产（角色库、场景库、Moodboard 等）",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=90,
        help="每集目标时长（秒，默认 90）。合理范围 60-180。影响剧本切分和 seg 数量",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=20,
        help="总集数（默认 20）",
    )
    args = parser.parse_args()

    if not (60 <= args.duration <= 180):
        print(f"⚠️ 每集时长 {args.duration}s 超出推荐范围 60-180，仍继续。", file=sys.stderr)

    base = resolve_base(args.base)
    project_dir = os.path.join(base, args.name)

    if os.path.exists(project_dir):
        print(f"❌ 项目目录已存在: {project_dir}", file=sys.stderr)
        return 1

    # 技能目录
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    stages_src = os.path.join(skill_dir, "stages")

    if not os.path.isdir(stages_src):
        print(f"❌ 未找到阶段模板目录: {stages_src}", file=sys.stderr)
        return 1

    # 创建产出目录（连续编号 01-07）
    dirs = [
        "01-scripts",
        "02-moodboard",
        "03-scenes",
        "04-character",
        "05-videos",
        "06-output",
        "06-output/_backup",
        "06-output/publish",
        "07-consistency-check/faces",
        "07-consistency-check/audio",
        "07-consistency-check/audio/golden",
    ]

    for d in dirs:
        os.makedirs(os.path.join(project_dir, d), exist_ok=True)

    # 复制阶段模板文件
    stages_dst = os.path.join(project_dir, "stages")
    os.makedirs(stages_dst, exist_ok=True)

    stage_files = sorted(f for f in os.listdir(stages_src) if f.endswith(".md"))
    for f in stage_files:
        shutil.copy2(os.path.join(stages_src, f), os.path.join(stages_dst, f))

    # 复制 references/
    references_src = os.path.join(skill_dir, "references")
    references_dst = os.path.join(project_dir, "references")
    if os.path.isdir(references_src):
        os.makedirs(references_dst, exist_ok=True)
        for f in os.listdir(references_src):
            if f.endswith(".md"):
                shutil.copy2(
                    os.path.join(references_src, f),
                    os.path.join(references_dst, f),
                )

    # 从模板项目复制可复用资产（如指定）
    template_info = ""
    copied_assets = []  # 保存实际复用的资产列表，后面用于打印提示
    if args.from_template:
        template_dir = os.path.join(base, args.from_template)
        if not os.path.isdir(template_dir):
            print(f"❌ 模板项目不存在: {template_dir}", file=sys.stderr)
            shutil.rmtree(project_dir)
            return 1
        copied, skipped = copy_reusable_assets(template_dir, project_dir)
        copied_assets = copied
        template_info = f"\n**模板来源**: {args.from_template}\n**已复用资产**: {', '.join(copied) if copied else '（无）'}"
        if skipped:
            template_info += f"\n**模板中缺失（未复用）**: {', '.join(skipped)}"

    # 写入 STATE.md
    now = datetime.now(CST).strftime("%Y-%m-%d %H:%M")

    # seg 数量范围推导: [max(4, d//10), max(6, d//6)]
    # 单 seg 时长是硬约束（4-15s），不展示派生的"平均值"避免与硬约束字面冲突
    seg_min = max(4, args.duration // 10)
    seg_max = max(6, args.duration // 6)

    state_content = f"""# STATE — {args.name}（中文名待定）

**当前阶段**: 01-outline
**状态**: pending
**最后更新**: {now}
**当前集**: ep01
**总集数**: {args.episodes}
**每集目标时长**: {args.duration}s（初始化时确定，后续剧本/切分以此为基准）
**信心度等级**: P0-全确认
{template_info}

---

## 时长参考（基于 {args.duration}s/集）

| 类型 | 典型值 |
|------|--------|
| 每集 beat 数 | 3-5 |
| 每集 seg 数 | {seg_min}-{seg_max} |
| **单 seg 时长** | **4-15s（硬约束，每个 seg 必须在此区间）** |
| 对白密度 | 见 stages/07-video.md 规则 3 |

---

## 阶段进度

- [ ] 01-outline
- [ ] 02-moodboard
- [ ] 03-lighting
- [ ] 04-scenes
- [ ] 04-character
- [ ] 06-script
- [ ] 07-video
- [ ] 08-composite
- [ ] 09-review
- [ ] 10-batch
- [ ] 11-publish  ← 可选

## 本集进度（ep01）

- [ ] 06-script
- [ ] 07-video
- [ ] 08-composite
- [ ] 09-review
"""
    with open(os.path.join(project_dir, "STATE.md"), "w") as f:
        f.write(state_content)

    # 创建叙事管理占位文件（从模板复用时会被覆盖——但 series-bible/skeleton/narrative 不在复用列表中，所以必建）
    scripts_dir = os.path.join(project_dir, "01-scripts")

    skeleton_path = os.path.join(scripts_dir, "episode-skeleton.md")
    if not os.path.exists(skeleton_path):
        with open(skeleton_path, "w") as f:
            f.write(f"# {args.name} 分集骨架\n\n（阶段 01 生成）\n")

    narrative_path = os.path.join(scripts_dir, "narrative-state.md")
    if not os.path.exists(narrative_path):
        with open(narrative_path, "w") as f:
            f.write(
                f"# 叙事状态追踪 — {args.name}\n\n**最后更新集**: EP00（初始化）\n\n（阶段 01 生成）\n"
            )

    # COST.md
    cost_path = os.path.join(project_dir, "COST.md")
    if not os.path.exists(cost_path):
        with open(cost_path, "w") as f:
            f.write(
                f"# {args.name} 成本记录\n\n"
                f"| 集 | Seedance 段数 | 重试次数 | 估算成本 | 累计 |\n"
                f"|----|-------------|---------|---------|------|\n"
            )

    # README
    readme_path = os.path.join(project_dir, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write(f"# {args.name}\n\nAI 漫剧项目\n\n开始 → 读 `STATE.md`\n")

    print(f"✅ 项目已初始化: {project_dir}")
    print(f"   📋 STATE.md — 当前进度")
    print(f"   📂 stages/ — {len(stage_files)} 个阶段指令文件")
    if args.from_template:
        print(f"   🔁 从模板 {args.from_template} 复用资产")
        # 基于实际复用列表判断，而不是常量——模板中若没有 character-bible.md，不应弹出警告
        if "01-scripts/character-bible.md" in copied_assets:
            print(f"   ⚠️ character-bible.md 已复用——请检查 Want/Need/Flaw/Ghost 是否适配新剧")
            print(f"      若新剧与模板剧无剧情关联，需手动清空四维（保留外在描述）")
    print(f"   💰 COST.md — 成本追踪")

    return 0


if __name__ == "__main__":
    sys.exit(main())
