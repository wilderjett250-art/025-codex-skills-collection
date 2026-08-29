#!/bin/bash
# 合成脚本 - 直接 concat 拼接所有 seg，不加转场
#
# 用法:
#   bash composite.sh <项目目录> <集号> [--srt <字幕文件>]
#
# 示例:
#   bash composite.sh projects/new-drama 01
#   bash composite.sh projects/new-drama 01 --srt projects/new-drama/05-videos/ep01/subtitles.srt
#
# 流程:
#   1. 扫描 05-videos/ep{集号}/ 目录下的所有 seg*.mp4 文件（按文件名排序）
#   2. 统一编码参数（避免 concat demuxer 报错）
#   3. 如目标文件已存在，自动备份到 06-output/_backup/
#   4. 用 concat demuxer 直接拼接
#   5. 可选：如果提供 --srt，用 subtitles 滤镜烧录字幕到成片
#
# 产出:
#   06-output/ep{集号}-raw.mp4       （无字幕）
#   06-output/ep{集号}-final.mp4     （烧录字幕，仅当传入 --srt 时生成）
#
# 备份规则:
#   旧版 raw/final 自动移动到 06-output/_backup/ep{集号}-{type}-v{N}-{timestamp}.mp4

set -e

# ── 参数解析 ──────────────────────────────────────────

PROJECT=""
EP=""
SRT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --srt) SRT="$2"; shift 2 ;;
    *)
      if [ -z "$PROJECT" ]; then PROJECT="$1"
      elif [ -z "$EP" ]; then EP="$1"
      fi
      shift ;;
  esac
done

if [ -z "$PROJECT" ] || [ -z "$EP" ]; then
  echo "用法: bash $0 <项目目录> <集号> [--srt <字幕文件>]"
  echo "示例: bash $0 projects/new-drama 01"
  echo "      bash $0 projects/new-drama 01 --srt projects/new-drama/05-videos/ep01/subtitles.srt"
  exit 1
fi

VDIR="$PROJECT/05-videos/ep${EP}"
ODIR="$PROJECT/06-output"
BACKUP="$ODIR/_backup"
TMP="$ODIR/_tmp_ep${EP}"

if [ ! -d "$VDIR" ]; then
  echo "❌ 未找到视频目录: $VDIR"
  exit 1
fi

# 扫描 seg*.mp4 文件（按文件名排序）
SEG_FILES=$(ls "$VDIR"/seg*.mp4 2>/dev/null | sort -V)
if [ -z "$SEG_FILES" ]; then
  echo "❌ 未找到 seg*.mp4 文件: $VDIR"
  exit 1
fi

SEG_COUNT=$(echo "$SEG_FILES" | wc -l)
echo "📋 找到 $SEG_COUNT 个 seg:"
echo "$SEG_FILES" | sed 's/^/   /'

mkdir -p "$TMP" "$ODIR" "$BACKUP"

# ── 备份函数 ─────────────────────────────────────────

# 备份旧版文件到 _backup/
# 用法: backup_if_exists <文件路径> <类型标签>
backup_if_exists() {
  local file="$1"
  local label="$2"
  if [ -f "$file" ]; then
    local base=$(basename "$file" .mp4)
    local ts=$(date +%Y%m%d_%H%M%S)
    # 查找当前已有的版本号
    local v=1
    while ls "$BACKUP/${base}-v${v}-"* 2>/dev/null | grep -q .; do
      v=$((v + 1))
    done
    local dst="$BACKUP/${base}-v${v}-${ts}.mp4"
    mv "$file" "$dst"
    echo "   💾 旧${label}已备份: $dst"
  fi
}

# ── 步骤 1：统一编码参数 ──────────────────────────────

echo ""
echo "🔄 统一编码参数..."
INDEX=0
while IFS= read -r seg; do
  INDEX=$((INDEX + 1))
  ffmpeg -i "$seg" \
    -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 128k -ar 44100 \
    -y "$TMP/s${INDEX}.mp4" </dev/null 2>/dev/null
done <<< "$SEG_FILES"

# ── 步骤 2：concat 拼接 ─────────────────────────────

echo "🎬 拼接..."
CONCAT="$TMP/concat.txt"
ABS_TMP="$(cd "$TMP" && pwd)"
: > "$CONCAT"

for i in $(seq 1 "$SEG_COUNT"); do
  echo "file '${ABS_TMP}/s${i}.mp4'" >> "$CONCAT"
done

RAW_OUTPUT="$ODIR/ep${EP}-raw.mp4"
backup_if_exists "$RAW_OUTPUT" "raw"

ffmpeg -f concat -safe 0 -i "$CONCAT" \
  -c:v libx264 -preset medium -crf 18 \
  -c:a aac -b:a 128k \
  -y "$RAW_OUTPUT" 2>/dev/null

RAW_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$RAW_OUTPUT")
echo "✅ 无字幕成片: $RAW_OUTPUT (${RAW_DUR}s)"

# ── 步骤 3：烧录字幕（可选） ────────────────────────

if [ -n "$SRT" ]; then
  if [ ! -f "$SRT" ]; then
    echo "⚠️  字幕文件不存在: $SRT"
    echo "   仅生成 raw 版本，请检查字幕路径"
  else
    echo ""
    echo "📝 烧录字幕..."
    FINAL_OUTPUT="$ODIR/ep${EP}-final.mp4"
    backup_if_exists "$FINAL_OUTPUT" "final"

    # 使用 subtitles 滤镜烧录硬字幕
    # force_style 统一字幕样式（白字+黑色描边，底部居中）
    # 编码参数与 raw 保持一致（crf 18，避免字幕烧录导致画质下降）
    ffmpeg -i "$RAW_OUTPUT" \
      -vf "subtitles='$SRT':force_style='FontName=Source Han Sans,FontSize=10,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=2,Alignment=2,MarginV=20'" \
      -c:v libx264 -preset medium -crf 18 \
      -c:a copy \
      -y "$FINAL_OUTPUT" 2>/dev/null

    echo "✅ 带字幕成片: $FINAL_OUTPUT"
  fi
fi

# ── 清理 ─────────────────────────────────────────────

rm -rf "$TMP"

echo ""
echo "🎬 EP${EP} 合成完成"
