# 阶段 09：成片检查

> 工具：AI 多模态预筛（截帧图片检查）+ 用户最终审核
> ⚠️ AI 只做"预筛"——挑出高置信问题让用户重点关注，不全权代理。用户仍需看一遍成片。

## 前置条件

- `06-output/ep{NN}-final.mp4` 存在
- 场景库、角色多视图可供对比

## AI 自检能力边界（重要）

| 维度 | AI 能力 | 可信度 |
|------|--------|--------|
| 画面崩坏（手指变形/面部扭曲） | 高 | ✅ 可自主判断 |
| 场景色调漂移（对比场景库） | 中 | ⚠️ 预筛，用户复核 |
| 角色面部一致性 | 中 | ⚠️ 预筛，用户复核 |
| 光影连续性 | 低 | ❌ AI 难以准确判断，用户主导 |
| 口型同步 | 低 | ❌ 需要音频，AI 无法听 |
| 音色一致性 | 无 | ❌ AI 不能听 |
| 情感表现力 | 无 | ❌ AI 不能听 |
| 字幕错别字 | 高 | ✅ AI 可检查 SRT 文本 |
| 剧情/叙事自检 | 中 | ⚠️ 对照剧本预筛 |

> ⚠️ 以前宣称"画面由 AI 自检，用户只审音频"——过于乐观。现改为 AI **预筛** + 用户**复核**两步走。

## 流程

### 步骤 0：视频截帧（AI 预筛前置）

```bash
# 每段视频每 2 秒截一帧
for seg in ./05-videos/ep{NN}/seg*.mp4; do
  name=$(basename "$seg" .mp4)
  ffmpeg -i "$seg" -vf "fps=0.5" "./07-consistency-check/ep{NN}_${name}_%03d.jpg"
done
```

AI 逐帧预筛以下项目。

### 步骤 1：AI 预筛（高置信维度）

#### 画面崩坏（AI 可自主判断）
- [ ] 无手指/肢体变形（多指、扭曲、消失）
- [ ] 无物理逻辑错误（衣服穿透、物品凭空消失、比例突变）
- [ ] 无 AI 文字乱码（如画面中出现的牌匾/文书）
- [ ] 无非自然闪烁/帧间色彩跳变
- [ ] 面部身份一致（同段内角色面部无漂移变脸）

#### 字幕（AI 可检查 SRT）
- [ ] SRT 文件内容与剧本对白一致
- [ ] SRT 时间戳与实际对白位置同步（允许 ±0.5s 偏差）
- [ ] 无错别字
- [ ] 字幕样式统一（字体/字号/位置跨集一致）

#### 叙事（AI 对照剧本预筛）
- [ ] 3 秒钩子有冲击力
- [ ] 情绪弧线完整（结构模板落地）
- [ ] 结尾悬念有效
- [ ] 场景目的达成（推进剧情+揭示角色）

### 步骤 2：AI 预筛 + 用户复核（中置信维度）

AI 先标记"疑似问题帧"，用户在这些位置重点审核：

#### 场景色调
- [ ] 场景色调与场景库 `main.png` 一致（AI 对比色相直方图，发现偏移预警）
- [ ] 画风与 Moodboard 一致

#### 角色外观
- [ ] 角色外观与多视图一致（AI 标记面部差异大的帧）
- [ ] 角色标识物正确出现（AI 标记缺失或错位的帧）

### 步骤 3：用户主导（低置信维度 / AI 无法判断）

#### 光影专项（用户主导，AI 仅预警明显偏差）
- [ ] 主光方向在镜头间保持一致（非叙事动机变化时）
- [ ] 光比与场景情绪匹配，无随机漂移
- [ ] 色温在整段内无意外跳变
- [ ] 角色面部曝光一致
- [ ] 分离光有效（角色不从暗背景中消失）
- [ ] 特写中眼神光存在且方向一致
- [ ] 灯光母题在关键帧中可见

#### 声音（⚠️ 用户必审——AI 无法听）
- [ ] 配音清晰可辨，无含混吞字
- [ ] 角色声音区分度明显（A 和 B 闭眼能分辨）
- [ ] 各角色音色与 voice-ref.mp3 一致
- [ ] 情感表现符合剧本标注
- [ ] 语速节奏自然，与画面情绪同步
- [ ] 环境音效符合场景
- [ ] 音量无突变/爆音
- [ ] 对白无缺失
- [ ] 口型与配音同步程度可接受

### 步骤 4：迭代精修（如果需要）

> 70% 合格、25% 需微调、5% 需重来。优先精修可定位的问题，不整集重做。
>
> ⚠️ **视频重生成门禁**：涉及重新提交 Seedance 生成视频的精修方案，必须先向用户报告问题并获得明确同意。未经同意禁止重新生成视频。

| 问题类型 | 精修方案 | 需要用户同意？ |
|----------|----------|--------------|
| 字幕错别字 | 直接改 SRT 文件，重新烧录 | ❌ 不需要 |
| 某 seg 视频画面质量不合格 | 用 `regen_seg.sh` 重新生成该 seg | ✅ **必须用户同意** |
| 某 seg 节奏偏慢/快 | 调整 `--duration` 重新生成 | ✅ **必须用户同意** |
| 某 seg 分离光不足 | 重新生成，强化 prompt 光线描述 | ✅ **必须用户同意** |
| 场景色调整体偏差 | 重新生成场景库 main.png + multiview.png，再重新生成受影响的 seg | ✅ **必须用户同意** |

> ⚠️ **级联影响**：如果重生成的 seg 有下游依赖（后续 seg 用其尾帧做起始画面），`regen_seg.sh` 会自动检测并提示"是否级联重生成"。**必须级联**——旧下游 seg 的起始画面与新重生成 seg 的尾帧不一致，衔接会断。选择不级联时衔接会崩，脚本会警告。

```bash
# 重新生成单个 seg（旧版自动备份）
bash <ai-manju>/scripts/regen_seg.sh projects/{项目名} {集号} {seg 号}

# 修改 SRT 后重新烧录字幕
bash <ai-manju>/scripts/composite.sh projects/{项目名} {集号} --srt ./05-videos/ep{NN}/subtitles.srt
```

### 步骤 5：提交终审

AI 预筛完成后，向用户发送成片，附带：
- 预筛结果摘要（高置信通过项、中置信疑似问题帧位置、需要用户主导的维度）
- 需要用户关注的项目（光影+音频优先）
- 如有未能自主修复的问题，列出具体位置和原因

> 用户需要完整看一遍成片——AI 预筛不能替代用户判断。

### 步骤 6：技术参数检查（具体指标）🆕

用 ffprobe 自动检查，任何一项不达标必须修复：

```bash
# 1. 时长检查
ACTUAL_DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 ./06-output/ep{NN}-final.mp4)
TARGET_DUR={STATE.md 的每集目标时长}
DIFF=$(echo "scale=2; ($ACTUAL_DUR - $TARGET_DUR) / $TARGET_DUR * 100" | bc)
# 判定：|DIFF| ≤ 5% 通过

# 2. 视频码率
BITRATE=$(ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate -of csv=p=0 ./06-output/ep{NN}-final.mp4)
# 判定：≥ 4_000_000（4 Mbps）

# 3. 音量峰值
PEAK=$(ffmpeg -i ./06-output/ep{NN}-final.mp4 -af volumedetect -f null - 2>&1 | grep max_volume)
# 判定：max_volume 在 -3dB 到 -1dB 之间
# 过高 = 可能爆音，过低 = 音量不足

# 4. 分辨率
RES=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 ./06-output/ep{NN}-final.mp4)
# 判定：1080x1920（竖屏 9:16）
```

**技术参数检查清单**：

| 指标 | 标准 | ffmpeg 命令 |
|------|------|------------|
| 时长偏差 | 在 [目标下限, 目标下限×2] 范围内（如 120-240s） | `ffprobe ... -show_entries format=duration` |
| 视频码率 | 720p ≥2.5 Mbps / 1080p ≥4 Mbps | `ffprobe ... -select_streams v:0 -show_entries stream=bit_rate` |
| 音量峰值 | -3dB 到 -1dB（≤ -0.5dB 亦可接受，>-0.5dB 需降音量） | `ffmpeg ... -af volumedetect` |
| 分辨率 | 720×1280（默认，满足抖音/视频号等平台需求）或 1080×1920（需显式传 `--resolution 1080p`） | `ffprobe ... -show_entries stream=width,height` |
| 帧率 | 24/25/30（连贯即可） | `ffprobe ... -show_entries stream=r_frame_rate` |
| 音频采样率 | 44100 或 48000 Hz | `ffprobe ... -select_streams a:0 -show_entries stream=sample_rate` |

> ⚠️ **分辨率说明**：Seedance API 默认输出 720×1280（竖屏 720p）。对于短视频分发平台（抖音/快手/视频号/小红书），720p 是可接受下限，平台会再次压缩。如果需要 1080p 源，Seedance 调用必须显式传 `--resolution 1080p`（成本更高）。

任一不达标时自动修复（重烧合成调参数）或用户手动介入。

## 步骤 7：EP01 专属——Golden 签字（硬前置条件）🆕

> ⚠️ 本步骤**仅 EP01 执行一次**。EP02 及以后直接跳过，Golden 已在 EP01 冻结，后续集只做"对比审计"（见阶段 10）。
>
> Golden 签字是跨集一致性的基石。如果 EP01 的音色不达标就被冻结为金标准，问题会复制到整个项目。

### 前置条件

- EP01 已完成步骤 1-6 的全部检查
- 技术参数检查通过

### 流程

#### 1. 播放角色对白样本

从 EP01 成片中为每个主要角色提取 **3 句不同情绪**的对白：

```bash
# 示例：为角色"沈鹿溪"提取 3 句不同情绪的对白
ffmpeg -i ./06-output/ep01-final.mp4 -ss {时间1} -t {时长1} -vn -acodec copy \
  ./07-consistency-check/audio/{角色名}_ep01_neutral.mp3
ffmpeg -i ./06-output/ep01-final.mp4 -ss {时间2} -t {时长2} -vn -acodec copy \
  ./07-consistency-check/audio/{角色名}_ep01_excited.mp3
ffmpeg -i ./06-output/ep01-final.mp4 -ss {时间3} -t {时长3} -vn -acodec copy \
  ./07-consistency-check/audio/{角色名}_ep01_angry.mp3
```

#### 2. 用户对每个角色明确签字

签字三档：

| 状态 | 动作 |
|------|------|
| ✅ **达到预期** | 可作为 golden，对白片段移入 `07-consistency-check/audio/golden/` |
| ⚠️ **勉强接受** | 调 voice-ref 后重生成 EP01 受影响 seg，通过后再定 golden |
| ❌ **不合格** | 必须重跑：调 TTS 音色/emotion 参数、重生成 voice-ref、重生成 EP01 受影响 seg，通过后再定 golden |

#### 3. 写入 GOLDEN_SIGNOFF.md

存放位置：`07-consistency-check/audio/golden/GOLDEN_SIGNOFF.md`

```markdown
# Golden 签字记录

**项目**: {项目名}
**签字集**: EP01
**签字日期**: 2026-05-15

## 角色音色签字状态

| 角色 | 状态 | 签字日期 | 备注 |
|------|------|---------|------|
| 沈鹿溪 | ✅ 达到预期 | 2026-05-15 | 情感张力足，可作为 golden |
| 萧珩 | ⚠️ 勉强接受 | 2026-05-15 | angry 情绪偏弱，EP02 后复测 |
| 太后 | ❌ 未签字 | — | 音色偏年轻，需重跑 voice-ref |
```

#### 4. 移入 golden 目录

签字状态为 ✅ 的角色，对白片段正式归档为金标准：

```bash
mv ./07-consistency-check/audio/{角色名}_ep01_*.mp3 \
   ./07-consistency-check/audio/golden/
```

### 硬门禁

**所有主要角色全部 ✅ 签字前，禁止进入阶段 10（批量生产）**——这是和 STATE.md 门禁、narrative-state 门禁同级的硬约束。

## 验收

- [ ] AI 预筛高置信项目全部通过（画面崩坏/字幕/叙事）
- [ ] 中置信项目用户已复核
- [ ] 光影+音频项目用户已主导审核
- [ ] 技术参数检查通过（时长/码率/音量，具体指标见步骤 6）
- [ ] 用户明确确认进入下一集/结束项目
- [ ] **仅 EP01 需要**：Golden 签字已完成（步骤 7），所有主要角色 ✅ 签字，记录写入 `07-consistency-check/audio/golden/GOLDEN_SIGNOFF.md`

## 完成后

将 `STATE.md` 中 `当前阶段` 更新为 `10-batch`，勾选 09。

- 如果只需要一集 → 标记 `状态: done`，可选进入 `11-publish`
- 如果多集 → → `stages/10-batch.md`
