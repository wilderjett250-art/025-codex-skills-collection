#!/usr/bin/env python3
"""
字幕自动对齐工具 v2 — 用 faster-whisper 词级时间戳精确对齐字幕。

用法:
  python3 align_srt.py --video <raw.mp4> --srt <input.srt> --out <output.srt> [--model medium] [--lang zh]

算法（v2 词级对齐）:
  1. Whisper 识别视频音频（word_timestamps=True）→ 得到每个字的精确时间戳
  2. 将所有识别字拼成文本流（带时间戳索引）
  3. 对剧本每句对白，在文本流中做模糊子串匹配
  4. 匹配成功 → 取第一个字的 start 和最后一个字的 end 作为字幕时间戳
  5. 匹配失败 → 回退到段级对齐或保留原始时间戳

优势：
  - 精度 ±0.1s（词级），远优于段级 ±2-5s
  - 不受 VAD 合并影响（直接在字流中搜索）
  - 不受 Seedance 对白时间偏移影响（只要能识别到字就能定位）
"""
import argparse
import difflib
import re
import sys
from pathlib import Path


def parse_srt(path):
    """解析 SRT 文件为 [{'index', 'start', 'end', 'text'}] 列表。"""
    text = Path(path).read_text(encoding="utf-8")
    blocks = re.split(r"\n\n+", text.strip())
    entries = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        idx = int(lines[0].strip())
        ts_line = lines[1].strip()
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", ts_line)
        if not m:
            continue
        g = m.groups()
        start = int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 1000
        end = int(g[4]) * 3600 + int(g[5]) * 60 + int(g[6]) + int(g[7]) / 1000
        text_content = "\n".join(lines[2:]).strip()
        entries.append({"index": idx, "start": start, "end": end, "text": text_content})
    return entries


def format_ts(seconds):
    """秒 → HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms == 1000:
        s += 1
        ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(entries, path):
    """将 entries 写为 SRT 文件。"""
    lines = []
    for i, e in enumerate(entries, 1):
        lines.append(str(i))
        lines.append(f"{format_ts(e['start'])} --> {format_ts(e['end'])}")
        lines.append(e["text"])
        lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def to_simplified(s):
    """繁→简转换。"""
    try:
        from zhconv import convert
        return convert(s, "zh-cn")
    except ImportError:
        return s


def strip_punct(s):
    """去标点空格，用于匹配。"""
    return re.sub(r"[，。！？、……\"\"''《》,.!?\"'\s\n]", "", s)


def find_subsequence(words_text, query, start_from=0):
    """
    在 words_text（纯字符串，每个字符对应 words 列表的一个元素）中
    找 query 的最佳模糊匹配位置。返回 (start_idx, end_idx, score) 或 None。
    
    使用滑动窗口 + 相似度匹配。
    """
    q = strip_punct(to_simplified(query))
    if not q:
        return None
    
    best_score = 0
    best_start = -1
    best_end = -1
    q_len = len(q)
    
    # 滑动窗口：窗口大小在 q_len*0.7 ~ q_len*1.5 之间搜索
    min_win = max(1, int(q_len * 0.7))
    max_win = min(len(words_text) - start_from, int(q_len * 1.5) + 2)
    
    for win_size in range(min_win, max_win + 1):
        for i in range(start_from, len(words_text) - win_size + 1):
            window = words_text[i:i + win_size]
            score = difflib.SequenceMatcher(None, q, window).ratio()
            if score > best_score:
                best_score = score
                best_start = i
                best_end = i + win_size
    
    if best_score >= 0.5:
        return (best_start, best_end, best_score)
    return None


def fix_overlaps(entries, gap=0.05):
    """相邻字幕如重叠，在前段末尾减去 gap 留出间隙。"""
    for i in range(len(entries) - 1):
        if entries[i]["end"] > entries[i + 1]["start"]:
            entries[i]["end"] = entries[i + 1]["start"] - gap
            if entries[i]["end"] < entries[i]["start"] + 0.3:
                entries[i]["end"] = entries[i]["start"] + 0.3
    return entries


def cap_duration(entries, chars_per_sec=4.0, min_cap=2.0, max_cap=8.0):
    """字幕显示时长上限：按文本字数估算合理阅读时长。"""
    for e in entries:
        text_len = len(strip_punct(e["text"]))
        cap = max(min_cap, min(text_len / chars_per_sec + 1.0, max_cap))
        if e["end"] - e["start"] > cap:
            e["end"] = e["start"] + cap
    return entries


def ensure_min_duration(entries, min_dur=0.8):
    """字幕显示时长过短时延长。"""
    for i, e in enumerate(entries):
        duration = e["end"] - e["start"]
        if duration < min_dur:
            new_end = e["start"] + min_dur
            if i + 1 < len(entries):
                limit = entries[i + 1]["start"] - 0.05
                new_end = min(new_end, limit)
            e["end"] = max(new_end, e["start"] + 0.3)
    return entries


def main():
    parser = argparse.ArgumentParser(description="Whisper 词级字幕自动对齐 v2")
    parser.add_argument("--video", required=True, help="输入视频或音频文件")
    parser.add_argument("--srt", required=True, help="输入 SRT（提供剧本文本）")
    parser.add_argument("--out", required=True, help="输出对齐后的 SRT")
    parser.add_argument("--model", default="medium", help="Whisper 模型大小")
    parser.add_argument("--lang", default="zh", help="语言代码")
    parser.add_argument("--device", default="cpu", help="cpu / cuda")
    parser.add_argument("--compute-type", default="int8", help="int8 / float16 / float32")
    args = parser.parse_args()

    video = Path(args.video)
    srt_in = Path(args.srt)
    if not video.exists():
        print(f"❌ 视频不存在: {video}", file=sys.stderr)
        sys.exit(1)
    if not srt_in.exists():
        print(f"❌ SRT 不存在: {srt_in}", file=sys.stderr)
        sys.exit(1)

    # 1. 读取剧本 SRT
    script_entries = parse_srt(srt_in)
    print(f"📜 剧本对白: {len(script_entries)} 句")

    # 2. Whisper 识别（词级时间戳）
    print(f"🔊 加载模型 {args.model} ({args.device}/{args.compute_type}) ...")
    from faster_whisper import WhisperModel
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)

    print(f"🎧 识别视频音频（词级时间戳）...")
    segments, info = model.transcribe(
        str(video),
        language=args.lang,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 100},
        word_timestamps=True,
        initial_prompt="以下是普通话的简体中文对白。",
    )

    # 收集所有词（每个字一个条目）
    all_words = []  # [{'word': str, 'start': float, 'end': float}]
    for seg in segments:
        if seg.words:
            for w in seg.words:
                all_words.append({"word": w.word.strip(), "start": w.start, "end": w.end})

    print(f"🔤 识别到 {len(all_words)} 个词/字")

    if not all_words:
        print("❌ 未识别到任何词，回退到原始 SRT", file=sys.stderr)
        write_srt(script_entries, args.out)
        sys.exit(0)

    # 3. 构建纯文本流（去标点简体化）用于匹配
    words_text_raw = "".join(w["word"] for w in all_words)
    words_text = strip_punct(to_simplified(words_text_raw))
    
    # 建立 words_text 每个字符 → all_words 索引的映射
    char_to_word_idx = []
    wi = 0
    ci = 0
    for w in all_words:
        clean = strip_punct(to_simplified(w["word"]))
        for ch in clean:
            char_to_word_idx.append(wi)
            ci += 1
        wi += 1

    print(f"📝 文本流长度: {len(words_text)} 字符")
    print(f"   前50字: {words_text[:50]}...")

    # 4. 对每句剧本对白做模糊子串匹配
    aligned = []
    search_from = 0  # 单调递增搜索起点

    for i, entry in enumerate(script_entries):
        query = entry["text"]
        result = find_subsequence(words_text, query, start_from=search_from)

        if result:
            start_ci, end_ci, score = result
            # 映射回 all_words 的索引
            word_start_idx = char_to_word_idx[start_ci]
            word_end_idx = char_to_word_idx[min(end_ci - 1, len(char_to_word_idx) - 1)]
            
            ts_start = all_words[word_start_idx]["start"]
            ts_end = all_words[word_end_idx]["end"]
            
            aligned.append({
                "text": query,
                "start": ts_start,
                "end": ts_end,
                "score": score,
            })
            # 下次从匹配结束位置开始搜索（保证单调）
            search_from = end_ci
        else:
            # 回退到原始时间戳
            aligned.append({
                "text": query,
                "start": entry["start"],
                "end": entry["end"],
                "score": 0.0,
            })
            print(f"   ⚠️ #{i+1} 未匹配: {query[:20]}...")

    # 5. 后处理
    aligned = fix_overlaps(aligned)
    aligned = ensure_min_duration(aligned)
    aligned = cap_duration(aligned)

    # 6. 输出
    write_srt(aligned, args.out)

    # 7. 报告
    print(f"\n📊 对齐报告:")
    print(f"{'#':>3}  {'原始':>8}  {'对齐':>8}  {'偏差':>7}  {'分数':>5}  文本")
    for i, (a, s) in enumerate(zip(aligned, script_entries), 1):
        delta = a["start"] - s["start"]
        marker = "✅" if a["score"] >= 0.5 else "⚠️ "
        print(f"{marker}{i:>2}  {s['start']:>6.2f}s  {a['start']:>6.2f}s  {delta:>+6.2f}s  {a['score']:.2f}  {a['text'][:25]}")

    matched = sum(1 for a in aligned if a["score"] >= 0.5)
    print(f"\n✅ 成功对齐 {matched}/{len(aligned)} 句")
    print(f"📝 输出: {args.out}")


if __name__ == "__main__":
    main()
