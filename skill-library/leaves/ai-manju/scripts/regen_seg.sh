#!/bin/bash
# 重新生成单个 seg 视频脚本（版本化版本）
#
# 从 assets.md 中读取指定 seg 的完整参数（按 _convention.md 标准格式），
# 重新提交 Seedance，等待完成后下载，备份旧文件，
# 在 assets.md 的版本历史表中追加新版本（不覆盖旧 prompt）。
#
# 用法:
#   bash regen_seg.sh <项目目录> <集号> <seg号> [选项]
#
# 选项:
#   -s <seed>          指定 seed 值（不传则随机）
#   -S                 自动使用上一次的 seed（从 task_id 查询）
#   --prompt-file <路径>  使用文件中的新 prompt 替代旧 prompt（会在 assets.md 写入 vN 块）
#   --seedance <路径>  seedance.py 路径（默认 video-generation/scripts/seedance.py）
#   --yes-cascade      跳过级联重生成确认（危险，慎用）
#
# 示例:
#   bash regen_seg.sh projects/new-drama 01 3                         # 随机 seed，复用原 prompt
#   bash regen_seg.sh projects/new-drama 01 3 -S                      # 复用上一次 seed
#   bash regen_seg.sh projects/new-drama 01 3 -s 12345                # 指定 seed
#   bash regen_seg.sh projects/new-drama 01 3 --prompt-file new.txt   # 用新 prompt 重生成
#
# 流程:
#   1. 从 assets.md 解析该 seg 的 prompt、ref-images、audio（新标准格式）
#   2. **检测下游依赖链**——如 seg-3 是 seg-4/seg-5 的起始画面来源，提示用户是否级联重生成
#   3. 备份旧的 seg{N}.mp4 和 lastframe_seg{N}.png 到 _backup/
#   4. 如有新 prompt，将 vN 块追加到 assets.md 中对应的 seg 区域
#   5. 提交 Seedance 任务（可选传入 seed）
#   6. 等待完成并下载
#   7. 重命名为 seg{N}.mp4 和 lastframe_seg{N}.png
#   8. 在 assets.md 的版本历史表追加新行，更新片段划分表的 task_id/seed
#   9. 如用户确认级联，自动递归重生成所有下游 seg
#
# 前置条件:
#   - ARK_API_KEY 环境变量已设置
#   - assets.md 使用 _convention.md 定义的标准 seg 格式

set -e

# ── 参数解析 ──────────────────────────────────────────

PROJECT=""
EP=""
SEG=""
SEEDANCE="video-generation/scripts/seedance.py"
SEED_VALUE=""
USE_PREV_SEED=false
PROMPT_FILE=""
YES_CASCADE=false

while [ $# -gt 0 ]; do
  case "$1" in
    -s) SEED_VALUE="$2"; shift 2 ;;
    -S) USE_PREV_SEED=true; shift ;;
    --prompt-file) PROMPT_FILE="$2"; shift 2 ;;
    --seedance) SEEDANCE="$2"; shift 2 ;;
    --yes-cascade) YES_CASCADE=true; shift ;;
    *)
      if [ -z "$PROJECT" ]; then PROJECT="$1"
      elif [ -z "$EP" ]; then EP="$1"
      elif [ -z "$SEG" ]; then SEG="$1"
      fi
      shift ;;
  esac
done

if [ -z "$PROJECT" ] || [ -z "$EP" ] || [ -z "$SEG" ]; then
  echo "用法: bash $0 <项目目录> <集号> <seg号> [选项]"
  echo "选项: -s <seed>  指定seed  |  -S  复用上一次seed"
  echo "      --prompt-file <路径>  使用新 prompt"
  echo "      --seedance <路径>     seedance.py 路径"
  echo "      --yes-cascade         自动级联重生成下游 seg（慎用）"
  exit 1
fi

VDIR="$PROJECT/05-videos/ep${EP}"
ASSETS="$VDIR/assets.md"
BACKUP="$VDIR/_backup"

if [ ! -f "$ASSETS" ]; then
  echo "❌ 未找到: $ASSETS"
  exit 1
fi

if [ ! -f "$SEEDANCE" ]; then
  echo "❌ 未找到 seedance.py: $SEEDANCE"
  exit 1
fi

echo "🔄 重新生成 EP${EP} seg${SEG}"

# ── 使用独立 Python 脚本解析 assets.md ───────────────

PARSE_SCRIPT=$(dirname "$0")/_assets_parser.py

if [ ! -f "$PARSE_SCRIPT" ]; then
  echo "❌ 未找到解析器: $PARSE_SCRIPT"
  exit 1
fi

# 查询上一次 seed
if $USE_PREV_SEED && [ -z "$SEED_VALUE" ]; then
  PREV_TASK_ID=$(python3 "$PARSE_SCRIPT" get-task-id "$ASSETS" "$SEG" 2>/dev/null)
  if [ -n "$PREV_TASK_ID" ] && [ "$PREV_TASK_ID" != "—" ]; then
    echo "   查询上一次 seed (task: $PREV_TASK_ID)..."
    PREV_SEED=$(python3 "$SEEDANCE" status "$PREV_TASK_ID" 2>/dev/null | python3 -c "
import sys, re
m = re.search(r'\"seed\"\s*:\s*(\d+)', sys.stdin.read())
if m: print(m.group(1))
" 2>/dev/null)
    if [ -n "$PREV_SEED" ]; then
      SEED_VALUE="$PREV_SEED"
      echo "   上一次 seed: $SEED_VALUE"
    else
      echo "   ⚠️ 无法查询上一次 seed，将使用随机 seed"
    fi
  fi
fi

if [ -n "$SEED_VALUE" ]; then
  echo "   seed: $SEED_VALUE"
else
  echo "   seed: 随机"
fi

# 读取新 prompt（如指定了 --prompt-file）
NEW_PROMPT=""
if [ -n "$PROMPT_FILE" ]; then
  if [ ! -f "$PROMPT_FILE" ]; then
    echo "❌ prompt 文件不存在: $PROMPT_FILE"
    exit 1
  fi
  NEW_PROMPT=$(cat "$PROMPT_FILE")
  echo "   使用新 prompt（${#NEW_PROMPT} 字符）"
fi

# 获取当前 prompt
if [ -n "$NEW_PROMPT" ]; then
  PROMPT="$NEW_PROMPT"
else
  PROMPT=$(python3 "$PARSE_SCRIPT" get-prompt "$ASSETS" "$SEG")
fi

if [ -z "$PROMPT" ]; then
  echo "❌ 无法获取 seg ${SEG} 的 prompt"
  exit 1
fi

echo "   prompt: $(echo "$PROMPT" | head -1 | cut -c1-60)..."

# 获取 ref-images 和 audio 列表
REF_IMAGES=$(python3 "$PARSE_SCRIPT" get-refs "$ASSETS" "$SEG" "$PROJECT")
AUDIO_FILES=$(python3 "$PARSE_SCRIPT" get-audios "$ASSETS" "$SEG" "$PROJECT")

REF_COUNT=$(echo "$REF_IMAGES" | grep -cv '^$' || echo 0)
AUDIO_COUNT=$(echo "$AUDIO_FILES" | grep -cv '^$' || echo 0)

echo "   ref-images: ${REF_COUNT} 张"
echo "   audio: ${AUDIO_COUNT} 条"

# ── 备份旧文件 ────────────────────────────────────────

mkdir -p "$BACKUP"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

if [ -f "$VDIR/seg${SEG}.mp4" ]; then
  cp "$VDIR/seg${SEG}.mp4" "$BACKUP/seg${SEG}_${TIMESTAMP}.mp4"
  echo "   💾 备份: seg${SEG}.mp4 → _backup/seg${SEG}_${TIMESTAMP}.mp4"
fi

if [ -f "$VDIR/lastframe_seg${SEG}.png" ]; then
  cp "$VDIR/lastframe_seg${SEG}.png" "$BACKUP/lastframe_seg${SEG}_${TIMESTAMP}.png"
  echo "   💾 备份: lastframe_seg${SEG}.png → _backup/"
fi

# ── 构建 seedance 命令 ────────────────────────────────

CMD="python3 $SEEDANCE create"
CMD="$CMD --prompt \"$PROMPT\""

if [ -n "$REF_IMAGES" ]; then
  REF_ARGS=""
  while IFS= read -r ref; do
    [ -z "$ref" ] && continue
    if [ ! -f "$ref" ]; then
      echo "⚠️  ref-image 不存在: $ref"
    else
      REF_ARGS="$REF_ARGS $ref"
    fi
  done <<< "$REF_IMAGES"
  if [ -n "$REF_ARGS" ]; then
    CMD="$CMD --ref-images$REF_ARGS"
  fi
fi

if [ -n "$AUDIO_FILES" ]; then
  AUDIO_ARGS=""
  while IFS= read -r aud; do
    [ -z "$aud" ] && continue
    if [ ! -f "$aud" ]; then
      echo "⚠️  audio 不存在: $aud"
    else
      AUDIO_ARGS="$AUDIO_ARGS $aud"
    fi
  done <<< "$AUDIO_FILES"
  if [ -n "$AUDIO_ARGS" ]; then
    CMD="$CMD --audio$AUDIO_ARGS"
  fi
fi

CMD="$CMD --ratio 9:16 --generate-audio true --return-last-frame true"

if [ -n "$SEED_VALUE" ]; then
  CMD="$CMD --seed $SEED_VALUE"
fi

echo ""
echo "📤 提交 Seedance 任务..."
echo ""

TASK_OUTPUT=$(eval "$CMD" 2>&1)
echo "$TASK_OUTPUT"

TASK_ID=$(echo "$TASK_OUTPUT" | grep -oP 'ID:\s*\K\S+' | head -1)
if [ -z "$TASK_ID" ]; then
  TASK_ID=$(echo "$TASK_OUTPUT" | grep -oP '"id":\s*"\K[^"]+' | head -1)
fi

if [ -z "$TASK_ID" ]; then
  echo "❌ 无法提取 task_id"
  exit 1
fi

echo ""
echo "⏳ 等待任务完成: $TASK_ID"
python3 "$SEEDANCE" wait "$TASK_ID" --download "$VDIR/"

# ── 重命名下载文件 ────────────────────────────────────

NEW_VIDEO=$(ls -t "$VDIR"/seedance_${TASK_ID}_*.mp4 2>/dev/null | head -1)
NEW_LASTFRAME=$(ls -t "$VDIR"/lastframe_${TASK_ID}.png 2>/dev/null | head -1)

if [ -n "$NEW_VIDEO" ]; then
  mv "$NEW_VIDEO" "$VDIR/seg${SEG}.mp4"
  echo "✅ seg${SEG}.mp4 已更新"
fi

if [ -n "$NEW_LASTFRAME" ]; then
  mv "$NEW_LASTFRAME" "$VDIR/lastframe_seg${SEG}.png"
  echo "✅ lastframe_seg${SEG}.png 已更新"
fi

# 查询新 seed
NEW_SEED=$(python3 "$SEEDANCE" status "$TASK_ID" 2>/dev/null | python3 -c "
import sys, re
m = re.search(r'\"seed\"\s*:\s*(\d+)', sys.stdin.read())
if m: print(m.group(1))
" 2>/dev/null)

# ── 更新 assets.md ────────────────────────────────────

# 构建更新命令
UPDATE_ARGS=""
UPDATE_ARGS="$UPDATE_ARGS --task-id $TASK_ID"
if [ -n "$NEW_SEED" ]; then
  UPDATE_ARGS="$UPDATE_ARGS --seed $NEW_SEED"
fi
if [ -n "$NEW_PROMPT" ]; then
  # 写入临时文件避免命令行长度问题
  TMP_PROMPT=$(mktemp)
  echo "$NEW_PROMPT" > "$TMP_PROMPT"
  UPDATE_ARGS="$UPDATE_ARGS --new-prompt-file $TMP_PROMPT"
fi

python3 "$PARSE_SCRIPT" append-version "$ASSETS" "$SEG" $UPDATE_ARGS

if [ -n "$TMP_PROMPT" ] && [ -f "$TMP_PROMPT" ]; then
  rm -f "$TMP_PROMPT"
fi

echo ""
echo "🎬 重新生成完成: EP${EP} seg${SEG}"
echo "   新 task_id: $TASK_ID"
if [ -n "$NEW_SEED" ]; then
  echo "   新 seed: $NEW_SEED"
fi
echo "   旧文件备份在: $BACKUP/"
echo ""

# ── 级联检测：找出依赖本 seg 的下游 seg ──────────────

DOWNSTREAM_SEGS=$(python3 "$PARSE_SCRIPT" find-downstream "$ASSETS" "$SEG" 2>/dev/null)

if [ -n "$DOWNSTREAM_SEGS" ]; then
  echo "⚠️  级联影响检测：以下 seg 依赖 seg-${SEG} 的尾帧作为起始画面："
  echo "$DOWNSTREAM_SEGS" | sed 's/^/       seg-/'
  echo ""
  echo "   新 seg-${SEG} 生成后，其尾帧已变化。下游 seg 的起始画面与"
  echo "   重生成的 seg-${SEG} 尾帧**不一致**，衔接会断。"
  echo ""

  if $YES_CASCADE; then
    echo "   --yes-cascade 已设置，自动级联重生成。"
    CASCADE="yes"
  else
    read -p "   是否级联重生成所有下游 seg？[y/N] " CASCADE
    CASCADE=$(echo "$CASCADE" | tr '[:upper:]' '[:lower:]')
  fi

  if [ "$CASCADE" = "y" ] || [ "$CASCADE" = "yes" ]; then
    echo ""
    echo "🔁 开始级联重生成..."
    for downstream_seg in $DOWNSTREAM_SEGS; do
      echo ""
      echo "  → 级联重生成 seg-${downstream_seg}"
      # 递归调用自己重跑下游 seg
      bash "$0" "$PROJECT" "$EP" "$downstream_seg" --seedance "$SEEDANCE" --yes-cascade
    done
    echo ""
    echo "✅ 级联重生成完成"
  else
    echo ""
    echo "⚠️  用户选择不级联。衔接可能不完美，请人工确认。"
    echo "   或稍后运行: bash $0 $PROJECT $EP <下游seg号>"
  fi
fi

echo ""
echo "下一步: 重新合成成片"
echo "   bash <ai-manju>/scripts/composite.sh $PROJECT $EP"
echo "   （<ai-manju> 在 OpenClaw 环境下为 /root/.openclaw/workspace/skills/ai-manju，其他环境为工作区根目录下 ai-manju/）"
