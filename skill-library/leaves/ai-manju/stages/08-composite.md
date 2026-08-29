# 阶段 08：合成成片

> 工具：FFmpeg（concat 拼接）
> ⚠️ 所有 seg 按顺序直接拼接，不加转场。字幕后期独立添加。

## 前置条件

- 本集所有 seg `05-videos/ep{NN}/seg{1-N}.mp4` 已确认

## 流程

### 步骤 1：直接拼接（使用 composite.sh 脚本）

推荐用封装脚本（自动备份旧版本）：

```bash
bash <ai-manju>/scripts/composite.sh projects/{项目名} {集号}
```

脚本会：
1. 扫描 `05-videos/ep{集号}/` 目录下所有 `seg*.mp4` 文件（按文件名排序）
2. 统一编码参数（避免 concat demuxer 报错）
3. 用 concat demuxer 直接拼接
4. 若 `06-output/ep{集号}-raw.mp4` 已存在，自动备份到 `06-output/_backup/ep{集号}-raw-v{N}-{timestamp}.mp4`
5. 输出到 `06-output/ep{集号}-raw.mp4`

### 步骤 1（手动版）：逐命令执行

如需手动执行（命令中的相对路径以项目根为基准，执行前用 `cd` 切到项目根）：

```bash
cd projects/{项目名}   # 确保当前目录是项目根

# 扫描所有片段（用 realpath 转绝对路径避免 ffmpeg 路径解析失败）
> concat.txt
for f in ./05-videos/ep{NN}/seg*.mp4; do
  echo "file '$(realpath "$f")'" >> concat.txt
done

# 备份旧版本（如存在）
if [ -f ./06-output/ep{NN}-raw.mp4 ]; then
  mkdir -p ./06-output/_backup
  mv ./06-output/ep{NN}-raw.mp4 ./06-output/_backup/ep{NN}-raw-$(date +%s).mp4
fi

# 拼接
ffmpeg -f concat -safe 0 -i concat.txt \
  -c:v libx264 -preset medium -crf 18 \
  -c:a aac -b:a 128k \
  ./06-output/ep{NN}-raw.mp4

# 清理临时文件
rm concat.txt
```

> ⚠️ concat demuxer 要求 `file '...'` 中的路径可被 ffmpeg 解析。推荐用 `realpath` 转绝对路径，避免 ffmpeg 当前工作目录和 concat.txt 所在目录不一致时路径错误。

### 步骤 2：生成 SRT 字幕文件

从剧本的对白汇总表提取时间戳和台词，生成 SRT 字幕文件，然后用 Whisper 自动对齐到真实音频时间戳。

存放位置：`05-videos/ep{NN}/subtitles.srt`

#### 2a. 初始 SRT（剧本时间戳 + 0.3s 偏移）

先按剧本对白汇总表生成初始 SRT（作为 Whisper 对齐的文本输入）。

**时间戳规则**：
- 从剧本对白汇总表提取每句对白的起止时间
- 起止时间统一 +0.3 秒偏移，补偿 Seedance 的对白启动延迟
- 字幕显示时长尽量 ≥ 对白时长 + 0.5 秒；连续紧接对白间可降至与对白时长相等，优先保证不重叠

#### 2b. Whisper 自动对齐（推荐）

用 `align_srt.py` 识别 raw 视频音频的真实发声时间戳，配合剧本文本输出精确对齐的 SRT：

```bash
HF_ENDPOINT=https://hf-mirror.com python3 <ai-manju>/scripts/align_srt.py \
  --video ./06-output/ep{NN}-raw.mp4 \
  --srt ./05-videos/ep{NN}/subtitles.srt \
  --out ./05-videos/ep{NN}/subtitles.srt \
  --model medium --lang zh --device cpu --compute-type int8
```

**工作原理**（v2 词级对齐）：
1. Whisper 识别 raw 视频音频（`word_timestamps=True`）→ 得到每个字的精确时间戳
2. 将所有识别字拼成文本流（繁→简转换）
3. 对剧本每句对白，在文本流中做模糊子串匹配（滑动窗口 + SequenceMatcher）
4. 匹配成功 → 取第一个字的 start 和最后一个字的 end 作为字幕时间戳
5. 后处理：修复重叠、最短时长保障、按字数限制最长显示时长

**精度**：±0.1s（词级），远优于段级对齐或静态偏移

**依赖**：`faster-whisper`、`zhconv`

**回退**：如果 Whisper 对齐匹配率 < 80%，保留步骤 2a 的静态偏移版本

### 步骤 3：烧录字幕（硬字幕）

```bash
bash <ai-manju>/scripts/composite.sh projects/{项目名} {集号} --srt ./05-videos/ep{NN}/subtitles.srt
```

脚本会用 ffmpeg 的 subtitles 滤镜烧录字幕到 `06-output/ep{NN}-final.mp4`（若已存在则自动备份旧版本到 `_backup/`）。

**字幕样式**（统一，跨集一致）：
- 字体：Source Han Sans（思源黑体）
- 字号：36
- 主色：白色
- 描边色：黑色，粗细 2
- 位置：底部居中，距底边 60px

手动执行：

```bash
ffmpeg -i ./06-output/ep{NN}-raw.mp4 \
  -vf "subtitles=./05-videos/ep{NN}/subtitles.srt:force_style='FontName=Source Han Sans,FontSize=36,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=2,Alignment=2,MarginV=60'" \
  -c:a copy \
  ./06-output/ep{NN}-final.mp4
```

### 步骤 4（可选）：字幕错别字修复

如果发现字幕文件中有错别字，直接改 SRT 文件重新烧录（不需要重新生成视频）：

```bash
# 修改 subtitles.srt
# 重新烧录（旧版自动备份）
bash <ai-manju>/scripts/composite.sh projects/{项目名} {集号} --srt ./05-videos/ep{NN}/subtitles.srt
```

## 成本追踪

本集合成完成后，AI 自动累计本集 API 消耗到项目级 `COST.md`。

### 成本估算公式

```
本集成本 = Seedance seg 数 × 单段成本 × (1 + 重试系数)
         + 场景库新增场景数 × 场景成本
         + 其他（TTS 重做等）

其中：
  单段成本     ≈ 3 元（视时长，实际以火山方舟账单为准）
  场景成本     ≈ 0.2 元（main + multiview 共 2 张）
  重试系数     = 该集 seg 重生成次数 / seg 总数
```

### 填写归属

- **触发者**：`composite.sh` 完成后，AI 读取本集 `05-videos/ep{NN}/assets.md` 的片段划分表和版本历史，计算本集消耗并追加到 `COST.md`
- **数据源**：
  - Seedance seg 数 = 片段划分表行数
  - 重试次数 = 每 seg 版本历史表行数之和 - seg 总数（即所有 v2/v3/... 的总和）
- **频率**：每集 `08-composite` 完成后一次，不要每 seg 单独更新

### COST.md 格式

```markdown
# {项目名} 成本记录

| 集 | Seedance seg 数 | 重试 seg 次数 | 新增场景 | 估算成本 | 累计 |
|----|----------------|-------------|---------|---------|------|
| 01 | 8 | 2 | 3 | ~30 元 | 30 元 |
| 02 | 9 | 0 | 1 | ~28 元 | 58 元 |
| ... |

**最后更新**: {日期}
**总预算估算**: ~{数字} 元
**已消耗**: ~{数字} 元
**剩余预算**: ~{数字} 元
```

> ⚠️ 估算仅供参考。实际费用以火山方舟账单为准。每 5 集跨集审计时核对估算与实际的差距，必要时调整系数。

## 产出

| 文件 | 说明 |
|------|------|
| `06-output/ep{NN}-raw.mp4` | 无字幕成片（当前） |
| `06-output/ep{NN}-final.mp4` | 带字幕成片（最终，当前） |
| `06-output/_backup/ep{NN}-*-v{N}-*.mp4` | 历史版本 |
| `05-videos/ep{NN}/subtitles.srt` | SRT 字幕源文件 |

## 验收

- [ ] 所有 seg 已按顺序拼接
- [ ] 音频无断裂或音量突变
- [ ] 字幕时间戳与对白基本同步（允许 ±0.5s 偏差）
- [ ] 字幕无错别字
- [ ] 字幕样式统一（字体、字号、位置）
- [ ] 总时长符合剧本预期
- [ ] final 视频码率与 raw 偏差 ≤ 5%（自检命令见下方）
- [ ] 旧版本（如有）已备份到 `_backup/`
- [ ] **ASSETS-INDEX.md 已同步更新**（门禁 5，新增本集 raw/final 行到"成片产出"段）

### 码率自检命令

```bash
RAW_BR=$(ffprobe -v error -show_entries stream=bit_rate -select_streams v:0 -of csv=p=0 ./06-output/ep{NN}-raw.mp4)
FINAL_BR=$(ffprobe -v error -show_entries stream=bit_rate -select_streams v:0 -of csv=p=0 ./06-output/ep{NN}-final.mp4)
DIFF=$(echo "scale=2; ($FINAL_BR - $RAW_BR) * 100 / $RAW_BR" | bc)
echo "raw=${RAW_BR} final=${FINAL_BR} 偏差=${DIFF}%"
# 偏差绝对值 ≤ 5% 为通过
```

## 完成后

→ `stages/09-review.md`
将 `STATE.md` 中 `当前阶段` 更新为 `09-review`，勾选 08。
