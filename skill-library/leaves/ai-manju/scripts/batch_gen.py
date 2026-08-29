#!/usr/bin/env python3
"""
批量生成 Seedance 视频 — 按依赖链动态调度并发提交

用法:
  python3 batch_gen.py <项目路径> <集号> [--max-parallel 3]

示例:
  python3 ai-manju/scripts/batch_gen.py projects/bengong-kaidian 02
  python3 ai-manju/scripts/batch_gen.py projects/bengong-kaidian 03 --max-parallel 2

配置文件:
  {项目路径}/05-videos/ep{集号}/seg-config.py

配置文件必须定义以下模块级变量:
  STYLE      — 画风关键词字符串
  NO_MARK    — 反面约束字符串（水印/字幕）
  CHARS      — dict，角色键 → 角色目录（相对项目根）
  SCENES     — dict，场景键 → 场景目录（相对项目根）
  SEGS       — list of dict，每个 seg 的完整配置

SEGS 每项字段:
  id          (int)       — seg 序号（1-based）
  duration    (int)       — 时长秒数（4-15）
  scene       (str|None)  — 场景键（SCENES 中的 key），None=无场景参考
  chars       (list[str]) — 角色键列表，顺序决定 ref-images 中角色槽位顺序
  audio       (list[str]) — 需要传入 voice-ref 的角色键列表（纯动作段=空）
  start_frame (int|None)  — 起始画面来源 seg id，None=文生视频
  prompt      (str)       — seg 正文 prompt（不含画风关键词和反面约束，会自动拼接）
  extras      (list[str]) — 可选，补充参考图（相对项目根的路径列表）

流程:
  1. 加载 seg-config.py，构建依赖 DAG
  2. 动态调度：就绪 seg 并发提交到 seedance，上限 max_parallel
  3. 每 seg 完成后重命名（seg{N}.mp4、lastframe_seg{N}.png），更新 assets.md
  4. 汇总报告

实现要点:
  - ref-images 顺序：场景 → 角色A → 角色B ... → 起始画面 → 补充
  - prompt 自动拼接 STYLE + NO_MARK + 配置的 prompt 正文
  - 失败不会让整体挂掉；依赖失败 seg 的后续 seg 被标记为阻塞
"""
import argparse
import importlib.util
import os
import re
import subprocess
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path


def load_config(config_path):
    """动态加载 seg-config.py 模块。"""
    spec = importlib.util.spec_from_file_location("seg_config", str(config_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    required = ["STYLE", "NO_MARK", "CHARS", "SCENES", "SEGS"]
    missing = [r for r in required if not hasattr(mod, r)]
    if missing:
        raise RuntimeError(f"配置缺失变量: {missing}")
    return mod


def _get_visible_chars(seg):
    """读取"画面中可辨识角色"列表（支持新旧字段名）。

    优先 visible_chars，退回旧字段名 chars（教训 #10 的字段重命名，保持兼容）。
    """
    if "visible_chars" in seg:
        return seg.get("visible_chars") or []
    if "chars" in seg:
        # 旧字段名，打印弃用警告
        import warnings
        warnings.warn(
            f"seg-{seg.get('id', '?')} 使用旧字段名 `chars`，建议改为 `visible_chars`"
            f"（教训 #10：字段名语义清晰化）",
            DeprecationWarning,
            stacklevel=2,
        )
        return seg.get("chars") or []
    return []


def _get_speaking_chars(seg):
    """读取"说话角色"列表（支持新旧字段名）。

    优先 speaking_chars，退回旧字段名 audio。
    """
    if "speaking_chars" in seg:
        return seg.get("speaking_chars") or []
    if "audio" in seg:
        import warnings
        warnings.warn(
            f"seg-{seg.get('id', '?')} 使用旧字段名 `audio`，建议改为 `speaking_chars`",
            DeprecationWarning,
            stacklevel=2,
        )
        return seg.get("audio") or []
    return []


def build_ref_images(seg, config, proj_dir, ep_dir):
    """按固定顺序构建 --ref-images 路径列表。"""
    refs = []
    # 1. 场景
    if seg.get("scene"):
        scene_dir = config.SCENES[seg["scene"]].rstrip("/")
        refs.append(f"{proj_dir}/{scene_dir}/main.png")
    # 2. 角色（按 visible_chars 列表顺序，兼容旧字段 chars）
    for char_key in _get_visible_chars(seg):
        char_dir = config.CHARS[char_key].rstrip("/")
        refs.append(f"{proj_dir}/{char_dir}/multiview.png")
    # 3. 起始画面
    if seg.get("start_frame"):
        refs.append(f"{ep_dir}/lastframe_seg{seg['start_frame']}.png")
    # 4. 补充参考图（可选）
    for extra in seg.get("extras") or []:
        if os.path.isabs(extra):
            refs.append(extra)
        else:
            refs.append(f"{proj_dir}/{extra}")
    return refs


def build_audio(seg, config, proj_dir):
    """构建 --audio voice-ref 列表。"""
    audios = []
    for char_key in _get_speaking_chars(seg):
        char_dir = config.CHARS[char_key].rstrip("/")
        audios.append(f"{proj_dir}/{char_dir}/voice-ref.mp3")
    return audios


def build_full_prompt(seg, config):
    """拼接完整 prompt：画风 + 反面约束 + 正文。"""
    body = seg["prompt"].strip()
    return f"{config.STYLE}\n\n{config.NO_MARK}\n\n{body}"


def submit_seg(seg, config, proj_dir, ep_dir, seedance_script):
    """提交单个 seg 到 Seedance。返回 task_id，失败抛异常。"""
    prompt = build_full_prompt(seg, config)
    refs = build_ref_images(seg, config, proj_dir, ep_dir)
    audios = build_audio(seg, config, proj_dir)

    cmd = [
        "python3", seedance_script, "create",
        "--prompt", prompt,
        "--ref-images", *refs,
        "--ratio", "9:16",
        "--duration", str(seg["duration"]),
        "--generate-audio", "true",
        "--return-last-frame", "true",
    ]
    if audios:
        cmd.extend(["--audio", *audios])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"seedance create 失败: {result.stderr.strip() or result.stdout.strip()}")
    m = re.search(r"ID:\s*(\S+)", result.stdout)
    if not m:
        raise RuntimeError(f"未能从输出提取 task_id: {result.stdout[-500:]}")
    return m.group(1)


def wait_and_download(task_id, ep_dir, seedance_script, interval=15):
    """等待 task 完成并下载。返回 (success, seed, output)。"""
    cmd = [
        "python3", seedance_script, "wait", task_id,
        "--interval", str(interval),
        "--download", ep_dir,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    full = result.stdout + result.stderr
    seed_m = re.search(r"Seed:\s*(\S+)", full)
    seed = seed_m.group(1) if seed_m else "?"
    return result.returncode == 0, seed, full


def rename_seg_files(ep_dir, task_id, seg_id):
    """重命名 seedance_xxx.mp4 → seg{N}.mp4，lastframe_xxx.png → lastframe_seg{N}.png。"""
    ep_path = Path(ep_dir)
    mp4s = list(ep_path.glob(f"seedance_{task_id}_*.mp4"))
    if mp4s:
        mp4s[0].rename(ep_path / f"seg{seg_id}.mp4")
    lf = ep_path / f"lastframe_{task_id}.png"
    if lf.exists():
        lf.rename(ep_path / f"lastframe_seg{seg_id}.png")


def update_assets_md(assets_path, seg_id, task_id, seed, status="completed"):
    """更新 assets.md 片段划分表行：pending → completed，填入 task_id 和 seed。"""
    if not assets_path.exists():
        return 0
    content = assets_path.read_text(encoding="utf-8")
    # 匹配格式: | {id} | {duration}s | pending | — | — | ...
    pattern = re.compile(
        rf"^(\|\s*{seg_id}\s*\|\s*\S+\s*\|)\s*pending\s*\|\s*—\s*\|\s*—\s*\|",
        re.MULTILINE,
    )
    replacement = rf"\1 {status} | {task_id} | {seed} |"
    new_content, count = pattern.subn(replacement, content, count=1)
    if count > 0:
        assets_path.write_text(new_content, encoding="utf-8")
    return count


def write_seg_details(assets_path, config, proj_dir, ep_dir):
    """
    生成前写入所有段详情到 assets.md（方案 A：即时登记门禁）。
    在 assets.md 末尾追加每段的完整 prompt、ref-images 映射、audio、命令参数。
    即使生成中断，所有 prompt 都有记录可追溯。
    """
    lines = ["\n---\n\n## 段详情\n"]

    for seg in config.SEGS:
        seg_id = seg["id"]
        duration = seg["duration"]
        scene_key = seg.get("scene")
        start_frame = seg.get("start_frame")
        full_prompt = build_full_prompt(seg, config)
        refs = build_ref_images(seg, config, proj_dir, ep_dir)
        audios = build_audio(seg, config, proj_dir)

        # 场景名
        scene_name = scene_key or "—"
        # 首帧来源
        frame_src = f"seg-{start_frame} 尾帧" if start_frame else "文生视频"
        dep = f"seg-{start_frame}" if start_frame else "—"

        lines.append(f"### seg-{seg_id}\n")
        lines.append(f"**时长**：{duration}s")
        lines.append(f"**场景**：{scene_name}")
        lines.append(f"**首帧来源**：{frame_src}")
        lines.append(f"**依赖**：{dep}")
        lines.append("")
        lines.append("#### Prompt (v1, 当前)\n")
        lines.append("```text")
        lines.append(full_prompt)
        lines.append("```\n")

        # ref-images 映射表
        lines.append("#### ref-images（逻辑槽位 → 物理编号）\n")
        lines.append("| 逻辑槽位 | 物理编号 | 文件路径 |")
        lines.append("|---------|---------|----------|")
        phys_idx = 1
        if scene_key:
            scene_dir = config.SCENES[scene_key].rstrip("/")
            lines.append(f"| 槽位-场景 | 图片{phys_idx} | `./{scene_dir}/main.png` |")
            phys_idx += 1
        for i, char_key in enumerate(_get_visible_chars(seg)):
            char_dir = config.CHARS[char_key].rstrip("/")
            label = chr(ord("A") + i)
            lines.append(f"| 槽位-角色{label} | 图片{phys_idx} | `./{char_dir}/multiview.png` |")
            phys_idx += 1
        if start_frame:
            lines.append(f"| 槽位-起始画面 | 图片{phys_idx} | `./05-videos/ep{{NN}}/lastframe_seg{start_frame}.png` |")
            phys_idx += 1
        for extra in seg.get("extras") or []:
            lines.append(f"| 槽位-补充 | 图片{phys_idx} | `./{extra}` |")
            phys_idx += 1
        lines.append("")

        # audio
        lines.append("#### audio\n")
        if audios:
            for i, a in enumerate(audios, 1):
                # 转为相对路径显示
                rel = a.replace(proj_dir + "/", "./")
                lines.append(f"- 音频{i}: `{rel}`")
        else:
            lines.append("无（无人声段）")
        lines.append("")

        # 命令参数
        lines.append("#### 命令参数\n")
        lines.append("```bash")
        audio_flag = ""
        if audios:
            audio_flag = " --audio " + " ".join(f'"{a.replace(proj_dir + "/", "./")}"' for a in audios)
        lines.append(f"--ratio 9:16 --duration {duration} --generate-audio true --return-last-frame true{audio_flag}")
        lines.append("```\n")

        # 版本历史
        lines.append("#### 版本历史\n")
        lines.append("| 版本 | task_id | seed | 时间 | 说明 |")
        lines.append("|------|---------|------|------|------|")
        lines.append("| v1 | — | — | — | 待生成 |")
        lines.append("\n---\n")

    # 追加到 assets.md
    with open(assets_path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return len(config.SEGS)


def main():
    parser = argparse.ArgumentParser(description="批量生成 Seedance 视频")
    parser.add_argument("project", help="项目路径，如 projects/bengong-kaidian")
    parser.add_argument("episode", help="集号，如 02")
    parser.add_argument("--max-parallel", type=int, default=3, help="并发上限（默认 3）")
    parser.add_argument("--seedance-script", default="video-generation/scripts/seedance.py",
                        help="seedance.py 脚本路径")
    parser.add_argument("--wait-interval", type=int, default=15, help="轮询间隔秒数")
    args = parser.parse_args()

    proj_dir = os.path.abspath(args.project)
    ep_dir = os.path.join(proj_dir, "05-videos", f"ep{args.episode}")
    config_path = Path(ep_dir) / "seg-config.py"
    assets_path = Path(ep_dir) / "assets.md"

    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}", file=sys.stderr)
        sys.exit(1)
    seedance_script = os.path.abspath(args.seedance_script)
    if not os.path.exists(seedance_script):
        print(f"❌ seedance.py 不存在: {seedance_script}", file=sys.stderr)
        sys.exit(1)

    config = load_config(config_path)
    segs_by_id = {s["id"]: s for s in config.SEGS}
    total = len(segs_by_id)
    print(f"📋 项目: {args.project}  集号: ep{args.episode}")
    print(f"📋 加载 {total} 个 seg  (并发上限: {args.max_parallel})")

    # 生成前写入段详情（方案 A：即时登记门禁）
    if assets_path.exists():
        content = assets_path.read_text(encoding="utf-8")
        if "## 段详情" not in content:
            n = write_seg_details(assets_path, config, proj_dir, ep_dir)
            print(f"📝 已写入 {n} 段详情到 assets.md（生成前登记）")
        else:
            print(f"📝 assets.md 已有段详情，跳过写入")

    completed = set()
    in_flight = {}  # seg_id → task_id
    failed = set()
    blocked = set()  # 因依赖失败而阻塞

    def deps_ok(seg_id):
        seg = segs_by_id[seg_id]
        sf = seg.get("start_frame")
        if sf is None:
            return True
        if sf in failed or sf in blocked:
            return None  # 依赖链断开
        return sf in completed

    def ready_segs():
        """未提交、未完成、依赖已满足的 seg id 列表。"""
        out = []
        for sid in sorted(segs_by_id):
            if sid in completed or sid in in_flight or sid in failed or sid in blocked:
                continue
            status = deps_ok(sid)
            if status is None:
                blocked.add(sid)
                continue
            if status:
                out.append(sid)
        return out

    executor = ThreadPoolExecutor(max_workers=args.max_parallel)
    pending = {}  # future → seg_id

    def launch(seg_id):
        seg = segs_by_id[seg_id]
        dep_tag = f"依赖 seg-{seg['start_frame']}" if seg.get("start_frame") else "文生"
        print(f"  ➤ 提交 seg-{seg_id} ({seg['duration']}s, {dep_tag})")
        try:
            task_id = submit_seg(seg, config, proj_dir, ep_dir, seedance_script)
            in_flight[seg_id] = task_id
            print(f"     task_id={task_id}")
            fut = executor.submit(wait_and_download, task_id, ep_dir, seedance_script, args.wait_interval)
            pending[fut] = seg_id
        except Exception as e:
            print(f"     ❌ 提交失败: {e}")
            failed.add(seg_id)

    def fill_slots():
        """用就绪 seg 填满并发槽位。"""
        while len(pending) < args.max_parallel:
            ready = ready_segs()
            if not ready:
                break
            launch(ready[0])

    start_time = time.time()
    fill_slots()

    while pending:
        done, _ = wait(list(pending.keys()), return_when=FIRST_COMPLETED)
        for fut in done:
            seg_id = pending.pop(fut)
            task_id = in_flight.get(seg_id, "?")
            try:
                success, seed, output = fut.result()
            except Exception as e:
                print(f"  ❌ seg-{seg_id} 异常: {e}")
                failed.add(seg_id)
                in_flight.pop(seg_id, None)
                continue

            if success:
                rename_seg_files(ep_dir, task_id, seg_id)
                updated = update_assets_md(assets_path, seg_id, task_id, seed)
                print(f"  ✅ seg-{seg_id} 完成 (seed={seed}, assets.md +{updated})")
                completed.add(seg_id)
                in_flight.pop(seg_id, None)
            else:
                # 从输出里捞一行错误提示
                err_line = ""
                for line in output.splitlines():
                    if "error" in line.lower() or "failed" in line.lower() or "Error" in line:
                        err_line = line.strip()[:200]
                        break
                print(f"  ❌ seg-{seg_id} 生成失败  {err_line}")
                failed.add(seg_id)
                in_flight.pop(seg_id, None)
        fill_slots()

    elapsed = int(time.time() - start_time)
    print(f"\n🎬 完成 {len(completed)}/{total}  耗时 {elapsed}s")
    if failed:
        print(f"❌ 失败: {sorted(failed)}")
    if blocked:
        print(f"⛔ 阻塞（依赖失败）: {sorted(blocked)}")

    # 写批次报告
    _write_batch_report(
        Path(ep_dir) / "batch-report.md",
        args.episode, total, completed, failed, blocked,
        elapsed, in_flight, segs_by_id,
    )

    if failed or blocked:
        sys.exit(1)


def _write_batch_report(
    report_path, ep_num, total, completed, failed, blocked,
    elapsed, in_flight, segs_by_id,
):
    """生成批次执行报告（无论成功还是失败都写）。"""
    from datetime import datetime
    lines = []
    lines.append(f"# EP{ep_num} 批次生成报告")
    lines.append("")
    lines.append(f"**执行时间**：{datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"**总 seg 数**：{total}")
    lines.append(f"**成功**：{len(completed)} ({len(completed)*100//max(total,1)}%)")
    lines.append(f"**失败**：{len(failed)}")
    lines.append(f"**阻塞**：{len(blocked)}（因依赖失败）")
    lines.append(f"**耗时**：{elapsed}s ({elapsed//60}m {elapsed%60}s)")
    lines.append("")

    if failed:
        lines.append("## 失败 seg")
        lines.append("")
        lines.append("| seg | 依赖 | 建议动作 |")
        lines.append("|-----|------|---------|")
        for sid in sorted(failed):
            seg = segs_by_id.get(sid, {})
            sf = seg.get("start_frame")
            dep = f"seg-{sf}" if sf else "—"
            action = (
                "检查 content_filter 错误，调整 prompt 里可能触发过滤的描述"
                if sid in in_flight
                else "检查 prompt 和 ref-images 参数，用 regen_seg.sh 重跑"
            )
            lines.append(f"| seg-{sid} | {dep} | {action} |")
        lines.append("")

    if blocked:
        lines.append("## 阻塞 seg（依赖链中断）")
        lines.append("")
        lines.append("以下 seg 因上游失败而未执行。修复失败 seg 后重跑 batch_gen 可继续。")
        lines.append("")
        for sid in sorted(blocked):
            seg = segs_by_id.get(sid, {})
            lines.append(f"- seg-{sid}（依赖 seg-{seg.get('start_frame', '?')}）")
        lines.append("")

    if not failed and not blocked:
        lines.append("## ✅ 全部成功")
        lines.append("")
        lines.append("进入阶段 08（合成）：")
        lines.append("")
        lines.append("```bash")
        lines.append(f"bash <ai-manju>/scripts/composite.sh <项目路径> {ep_num}")
        lines.append("```")
        lines.append("")

    lines.append("## 后续操作建议")
    lines.append("")
    if failed or blocked:
        lines.append("1. 查看上方失败表，针对 content_filter/prompt/参考图等问题分别处理")
        lines.append("2. 单 seg 修复：`bash <ai-manju>/scripts/regen_seg.sh <项目> <集号> <seg>`")
        lines.append("3. 修复后可再次运行 `batch_gen.py`，已完成的 seg 会跳过")
    else:
        lines.append("1. 目测每段视频质量（角色一致性、场景色调）")
        lines.append("2. 运行 `regen_assets_index.py --check` 确认 ASSETS-INDEX 已同步")
        lines.append("3. 进入合成阶段")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"📄 批次报告：{report_path}")


if __name__ == "__main__":
    main()
