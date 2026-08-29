# 阶段 11：发布前处理（可选）

> 工具：FFmpeg
> ⚠️ 可选阶段。用于将成片转换为各分发平台要求的规格。

## 前置条件

- `06-output/ep{NN}-final.mp4` 存在且已通过阶段 09 检查

## 流程

### 前置：创建平台子目录

```bash
mkdir -p ./06-output/publish/{douyin,weixin,youtube-shorts,covers,copy}
```

> 按需添加其他平台子目录（如 kuaishou、xiaohongshu 等）。

### 步骤 1：确定分发平台

根据项目分发计划，确认目标平台：

| 平台 | 规格要求 |
|------|---------|
| 抖音 | 竖屏 1080×1920，码率 5-8 Mbps，H.264，AAC，≤15 min |
| 快手 | 竖屏 1080×1920，码率 5-8 Mbps，H.264，≤57 min |
| 小红书 | 竖屏 1080×1920 或 3:4，码率 3-5 Mbps，≤15 min |
| 视频号 | 竖屏 1080×1920，码率 ≤2 Mbps，≤60 min |
| B 站竖屏 | 1080×1920，码率 ≤8 Mbps，H.264/H.265 |
| YouTube Shorts | 1080×1920，≤60 秒（注意时长限制） |
| Reels (Instagram) | 1080×1920，≤90 秒 |

> 以上规格为截至 2026 年的常见要求，各平台政策会变，建议发布前再确认当期最新规格。

### 步骤 2：转码

为每个平台生成对应规格的版本。

**抖音/快手/小红书通用版**（高码率）：

```bash
ffmpeg -i ./06-output/ep{NN}-final.mp4 \
  -c:v libx264 -preset medium -crf 20 -maxrate 6M -bufsize 12M \
  -vf "scale=1080:1920" \
  -c:a aac -b:a 192k -ar 44100 \
  -movflags +faststart \
  ./06-output/publish/douyin/ep{NN}.mp4
```

**视频号版**（低码率）：

```bash
ffmpeg -i ./06-output/ep{NN}-final.mp4 \
  -c:v libx264 -preset medium -crf 24 -maxrate 2M -bufsize 4M \
  -vf "scale=1080:1920" \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  ./06-output/publish/weixin/ep{NN}.mp4
```

**YouTube Shorts 版**（需注意时长限制，如超过 60 秒需做二次剪辑）：

```bash
ffmpeg -i ./06-output/ep{NN}-final.mp4 \
  -c:v libx264 -preset slow -crf 18 \
  -vf "scale=1080:1920" \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  ./06-output/publish/youtube-shorts/ep{NN}.mp4
```

### 步骤 3：生成封面帧

从成片中提取封面帧（通常取 3 秒钩子的高潮帧）：

```bash
# 从 3 秒处截取封面
ffmpeg -i ./06-output/ep{NN}-final.mp4 \
  -ss 00:00:03 -vframes 1 \
  -vf "scale=1080:1920" \
  ./06-output/publish/covers/ep{NN}-cover.jpg

# 或从指定时间点截取（可选）
ffmpeg -i ./06-output/ep{NN}-final.mp4 \
  -ss {时间} -vframes 1 \
  ./06-output/publish/covers/ep{NN}-cover.jpg
```

### 步骤 4（可选）：封面加标题

用 ffmpeg 在封面上添加集标题：

```bash
ffmpeg -i ./06-output/publish/covers/ep{NN}-cover.jpg \
  -vf "drawtext=fontfile=/path/to/SourceHanSans.ttc:text='{集标题}':x=(w-text_w)/2:y=h-200:fontsize=80:fontcolor=white:borderw=3:bordercolor=black" \
  ./06-output/publish/covers/ep{NN}-cover-titled.jpg
```

### 步骤 5：生成发布文案

为每集生成发布文案（由 AI 根据剧本和叙事状态自动生成）：

```markdown
# {剧名} EP{NN}：{集标题}

{一段 100 字以内的集简介，含悬念}

#AI漫剧 #{剧名} #{题材类型} #短剧 #爽文

👉 下集预告：{一句话预告，不剧透}
```

存放位置：`06-output/publish/copy/ep{NN}-copy.md`

### 步骤 6：发布排期表

在 `06-output/publish/schedule.md` 维护集的发布节奏：

```markdown
# 发布排期

| 集 | 平台 | 计划发布时间 | 实际发布时间 | 状态 |
|----|------|------------|------------|------|
| 01 | 抖音/快手/小红书 | 2026-05-06 18:00 | 2026-05-06 18:05 | published |
| 02 | 抖音/快手/小红书 | 2026-05-07 18:00 | — | pending |
```

## 产出

```
06-output/publish/
├── douyin/
│   ├── ep01.mp4
│   ├── ep02.mp4
│   └── ...
├── weixin/
├── youtube-shorts/
├── covers/
│   ├── ep01-cover.jpg
│   └── ...
├── copy/
│   ├── ep01-copy.md
│   └── ...
└── schedule.md
```

## 验收

- [ ] 每集至少生成一个目标平台的转码版本
- [ ] 封面帧已生成且有视觉吸引力
- [ ] 发布文案已生成
- [ ] 发布排期已制定

## 完成后

将 `STATE.md` 中 `状态` 标记为 `published` 或 `done`。
