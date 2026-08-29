#!/usr/bin/env python3
"""跨集漂移热检测（骨架版）。

用途：
  - 治理"每 5 集跨集审计"滞后问题：第 6/7/8 集可能已漂 3 集才被发现
  - 每集成片完成后自动跑，尽早发现角色外观/音色偏离

维度：
  1. 角色外观漂移：提取面部 embedding，与 EP01 golden 做余弦相似度
  2. 角色音色漂移：提取 speaker embedding，与 EP01 golden 做余弦相似度
  3. 场景色调漂移：直方图距离（不需要 ML 依赖，纯 PIL/numpy）

依赖（软）：
  - 角色脸部检测：insightface （`pip install insightface onnxruntime`）
  - 音色 embedding：pyannote-audio（`pip install pyannote.audio`，需 HuggingFace token）
  - 色调检查：numpy + pillow（`pip install numpy pillow`）

如果依赖未安装，脚本**优雅降级**：
  - 缺依赖的维度打印"跳过 + 安装指引"
  - 可用维度仍执行

用法:
    python3 drift_check.py <项目路径> <集号>
    python3 drift_check.py projects/bengong-kaidian 05

退出码:
  0 — 全部维度通过（或全部跳过）
  1 — 至少一个维度检测到漂移

本脚本是**骨架版**——面部/音色 embedding 的完整实现需要下载 ML 模型，首次运行可能较慢。
色调检查始终可用（无 ML 依赖）。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional


# 阈值（余弦相似度，越接近 1 越相似）
FACE_THRESHOLD = 0.85
VOICE_THRESHOLD = 0.80
HIST_THRESHOLD = 0.75  # 色调直方图相关系数


def check_deps():
    """检查可用的依赖。"""
    deps = {
        "numpy": False,
        "PIL": False,
        "insightface": False,
        "onnxruntime": False,
        "pyannote.audio": False,
    }
    try:
        import numpy  # noqa: F401
        deps["numpy"] = True
    except ImportError:
        pass
    try:
        from PIL import Image  # noqa: F401
        deps["PIL"] = True
    except ImportError:
        pass
    try:
        import insightface  # noqa: F401
        deps["insightface"] = True
    except ImportError:
        pass
    try:
        import onnxruntime  # noqa: F401
        deps["onnxruntime"] = True
    except ImportError:
        pass
    try:
        from pyannote.audio import Pipeline  # noqa: F401
        deps["pyannote.audio"] = True
    except ImportError:
        pass
    return deps


def extract_frames_from_video(video_path: Path, out_dir: Path, count: int = 5) -> list[Path]:
    """从视频中抽取指定数量的关键帧。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    # 用 ffmpeg 从视频均匀抽帧
    for i in range(count):
        # 相对位置：每帧取视频 (i+1)/(count+1) 位置
        ratio = (i + 1) / (count + 1)
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-ss", f"{ratio}",  # 这里需要知道总时长才能换算
                "-i", str(video_path),
                "-vframes", "1",
                str(out_dir / f"frame_{i+1:02d}.jpg"),
            ],
            stdin=subprocess.DEVNULL,
        )
    return sorted(out_dir.glob("frame_*.jpg"))


def check_color_histogram(project: Path, ep_num: str) -> tuple[bool, list[str]]:
    """色调检查（纯 numpy + PIL 实现）。

    对比 EP01 成片和当前集成片的 RGB 直方图相关系数。
    相关系数 > HIST_THRESHOLD 视为通过。
    """
    messages = []
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        messages.append("⚠️  跳过色调检查：缺少 numpy 或 PIL 依赖")
        messages.append("    安装：pip install numpy pillow")
        return True, messages

    golden_video = project / "06-output" / "ep01-final.mp4"
    current_video = project / "06-output" / f"ep{ep_num.zfill(2)}-final.mp4"

    if not golden_video.is_file():
        messages.append("⚠️  跳过色调检查：EP01 成片不存在（golden 基准缺失）")
        return True, messages
    if not current_video.is_file():
        messages.append(f"⚠️  跳过色调检查：EP{ep_num} 成片不存在")
        return True, messages

    # 抽样 5 帧
    tmp_dir = project / "07-consistency-check" / "_drift-check" / f"ep{ep_num}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    golden_dir = tmp_dir / "golden"
    current_dir = tmp_dir / "current"

    # 用 ffmpeg 抽帧（基于 fps 以避免需要知道总时长）
    for label, vid, out in [("golden", golden_video, golden_dir),
                             ("current", current_video, current_dir)]:
        out.mkdir(parents=True, exist_ok=True)
        if not list(out.glob("frame_*.jpg")):
            subprocess.run(
                [
                    "ffmpeg", "-y", "-loglevel", "error",
                    "-i", str(vid),
                    "-vf", "fps=0.2,scale=320:568",  # 每 5 秒抽一帧，缩放到小尺寸
                    "-frames:v", "5",
                    str(out / "frame_%03d.jpg"),
                ],
                stdin=subprocess.DEVNULL,
            )

    def compute_hist(img_path: Path):
        """计算归一化 RGB 直方图。"""
        img = Image.open(img_path).convert("RGB")
        arr = np.array(img).reshape(-1, 3)
        hists = []
        for ch in range(3):
            h, _ = np.histogram(arr[:, ch], bins=32, range=(0, 256))
            h = h.astype(float)
            if h.sum() > 0:
                h /= h.sum()
            hists.append(h)
        return np.concatenate(hists)

    golden_hists = [compute_hist(p) for p in sorted(golden_dir.glob("frame_*.jpg"))]
    current_hists = [compute_hist(p) for p in sorted(current_dir.glob("frame_*.jpg"))]

    if not golden_hists or not current_hists:
        messages.append("⚠️  跳过色调检查：未能抽到足够帧")
        return True, messages

    # 取均值向量计算相关系数
    golden_avg = np.mean(golden_hists, axis=0)
    current_avg = np.mean(current_hists, axis=0)
    # 皮尔逊相关系数
    denom = np.std(golden_avg) * np.std(current_avg)
    if denom > 0:
        corr = np.mean((golden_avg - golden_avg.mean()) * (current_avg - current_avg.mean())) / denom
    else:
        corr = 0.0

    ok = corr >= HIST_THRESHOLD
    symbol = "✅" if ok else "⚠️ "
    messages.append(f"{symbol} 色调检查：EP01 vs EP{ep_num} 直方图相关系数 = {corr:.3f}"
                    f"（阈值 {HIST_THRESHOLD}）")
    if not ok:
        messages.append("    → 可能色调漂移。检查场景图 main.png 是否被修改。")

    return ok, messages


def check_face_drift(project: Path, ep_num: str, deps: dict) -> tuple[bool, list[str]]:
    """角色外观漂移检测（需 insightface）。"""
    messages = []
    if not deps["insightface"] or not deps["onnxruntime"]:
        messages.append("⚠️  跳过角色外观检查：缺少 insightface/onnxruntime 依赖")
        messages.append("    安装：pip install insightface onnxruntime")
        messages.append("    首次运行会自动下载 ~200MB 模型")
        return True, messages

    # TODO: 完整实现
    # 1. 从 EP01 和 current ep 的成片中抽帧
    # 2. 用 insightface 检测和提取面部 embedding
    # 3. 每个角色单独聚类（同一集的同角色多张脸应该自然聚在一起）
    # 4. 对每个角色，取 EP01 最集中的聚类中心 vs current ep 对应聚类中心算余弦相似度
    # 5. 低于阈值 → 该角色漂移
    messages.append("⚠️  角色外观检查骨架未完整实现（需要集成 insightface 流程）")
    messages.append("    当前阶段：依赖已可用，待补完 embedding 提取和聚类逻辑")
    return True, messages


def check_voice_drift(project: Path, ep_num: str, deps: dict) -> tuple[bool, list[str]]:
    """角色音色漂移检测（需 pyannote.audio）。"""
    messages = []
    if not deps["pyannote.audio"]:
        messages.append("⚠️  跳过音色检查：缺少 pyannote.audio 依赖")
        messages.append("    安装：pip install pyannote.audio")
        messages.append("    需要 HuggingFace token，详见 https://huggingface.co/pyannote")
        return True, messages

    # TODO: 完整实现
    # 1. 从 EP01 成片中提取各角色 golden voice-ref（按对白时间段切割）
    # 2. 从 current ep 中提取同角色的对白片段
    # 3. 用 pyannote 提取 speaker embedding
    # 4. 计算余弦相似度，低于阈值 → 音色漂移
    messages.append("⚠️  角色音色检查骨架未完整实现（需要集成 pyannote 流程）")
    return True, messages


def main():
    parser = argparse.ArgumentParser(
        description="跨集漂移热检测（每集成片后运行）",
    )
    parser.add_argument("project", type=Path, help="项目根目录")
    parser.add_argument("ep_num", type=str, help="当前集号（如 05）")
    parser.add_argument("--skip-face", action="store_true", help="跳过角色外观检查")
    parser.add_argument("--skip-voice", action="store_true", help="跳过音色检查")
    parser.add_argument("--skip-color", action="store_true", help="跳过色调检查")
    args = parser.parse_args()

    project = args.project.resolve()
    ep_num = args.ep_num.zfill(2)

    if not project.is_dir():
        print(f"错误：项目目录不存在：{project}", file=sys.stderr)
        sys.exit(2)

    print(f"📊 漂移检测：EP{ep_num} vs EP01 golden")
    print()

    deps = check_deps()
    all_ok = True

    if not args.skip_color:
        ok, msgs = check_color_histogram(project, ep_num)
        for m in msgs:
            print(m)
        if not ok:
            all_ok = False
        print()

    if not args.skip_face:
        ok, msgs = check_face_drift(project, ep_num, deps)
        for m in msgs:
            print(m)
        if not ok:
            all_ok = False
        print()

    if not args.skip_voice:
        ok, msgs = check_voice_drift(project, ep_num, deps)
        for m in msgs:
            print(m)
        if not ok:
            all_ok = False
        print()

    if not all_ok:
        print("=" * 60)
        print("⚠️  检测到漂移。建议：")
        print("  1. 人工复核当前集成片")
        print("  2. 对照 EP01 golden 确认漂移程度")
        print("  3. 严重漂移 → 降级信心度等级（参考 _convention.md 工作流变更降级）")
        sys.exit(1)

    print("✅ 全部通过（可用维度）")


if __name__ == "__main__":
    main()
