---
name: ai-manju
description: AI 漫剧创作全流程工作流。Seedream 5.0 出图 + Seedance 2.0 出视频 + FFmpeg 合成。全程火山方舟。触发词：AI漫剧、漫剧创作、ai漫画剧、漫剧制作。
---

# AI 漫剧工作流

## 一句话

11 个自包含阶段的串行流水线（阶段 11 可选）：整季大纲（含分集骨架 3-5 beat + 叙事状态追踪）→ 风格板 → 灯光配色 → 场景库 → 角色设计 → 剧本（逐集展开 + 更新叙事状态）→ 视频 prompt 组装审核 → 依赖链并行提交 → 合成（自动备份旧版）→ AI 预筛 + 用户复核 → 批量 → 发布前处理。

## 快速开始

```bash
# 1. 设置环境变量
export ARK_API_KEY="your-ark-api-key"         # 火山方舟
export DOUBAO_TTS_API_KEY="your-tts-api-key"  # 豆包TTS（可选，用于角色音色）

# 2. 初始化项目（创建目录 + 复制阶段文件 + 写入 STATE.md）
#    OpenClaw 环境自动使用 /root/.openclaw/projects/
#    其他环境（Kiro/Claude）使用当前目录下的 projects/
python3 <ai-manju>/scripts/init_project.py <项目名> \
  --duration 90 \           # 每集目标时长（秒），默认 90
  --episodes 20             # 总集数，默认 20

# 或从已有项目复制角色库/场景库（跨项目复用）
python3 <ai-manju>/scripts/init_project.py <新项目名> --from-template <源项目名>

# 3. 进入项目，读 STATE.md
cd projects/<项目名>/    # 或 /root/.openclaw/projects/<项目名>/
cat STATE.md

# 4. 执行当前阶段
cat stages/01-outline.md
# → 按文件内指令执行 → 完成后更新 STATE.md → 进入下一阶段
```

## 阶段总览

11 个连续编号阶段，流程无跳级：

| # | 阶段 | 工具 | 产出 |
|---|------|------|------|
| 01 | 整季叙事大纲 | DeepSeek | `series-bible.md` + `character-bible.md` + `episode-skeleton.md`（每集 3-5 beat）+ `narrative-state.md` |
| 02 | 风格板 Moodboard | Seedream | `02-moodboard/` 5-8 张概念图 |
| 03 | 灯光哲学 + 配色 | 人工+DeepSeek | `lighting-philosophy.md` + `color-palette.md` |
| 04 | 角色设计 | Seedream + TTS | `04-character/{角色}/` front.png + multiview + voice-ref |
| 05 | 剧本（单集） | DeepSeek | `ep{NN}-script.md` + 更新 `narrative-state.md` |
| 06 | 场景图（按需） | Seedream | `03-scenes/{场景名}/` 按剧本内容生成/复用/修改 |
| 07 | 视频组装+审核+依赖链并行生成 | Seedance | `05-videos/ep{NN}/seg*.mp4` |
| 08 | 合成 | FFmpeg | `06-output/ep{NN}-final.mp4`（concat 拼接，旧版自动备份） |
| 09 | 成片检查 | AI 预筛 + 人工复核 | 检查清单通过 |
| 10 | 批量生产 | 循环 05-09 | 后续集（每 5 集跨集审计） |
| 11 | 发布前处理（可选） | FFmpeg | 多平台转码 + 封面 + 文案 |

> ⚠️ **阶段重排说明（2026-05-06）**：原流程为 04-scenes → 04-character → 06-script。现改为 04-character → 05-script → 06-scenes。原因：场景图需结合剧本内容按需生成，而非提前猜测一次性生成全部场景。场景库采用"逐集积累"模式——每集剧本确认后，处理该集涉及的场景图（复用/修改/新建）。

> ⚠️ 从旧版升级：旧编号（`03-5-scenes`、`05-script`、`07-video`、`11-composite`、`12-review`、`13-batch`）已全部连续化。旧项目升级时需同步更新 `STATE.md` 的阶段进度列表。

## 项目目录

> ⚠️ **目录编号说明**：目录编号（01-07）是**资产逻辑分层**，与阶段编号（01-11）不完全一一对应。`01-scripts` 被多个阶段共用（01/03/05），`03-scenes` 对应阶段 06（按需生成）。其余目录与阶段编号对齐或接近。按 STATE.md 的当前阶段找对应产出目录即可。

```
projects/<项目名>/
├── STATE.md
├── COST.md                      # API 成本累计
├── stages/                      # 阶段指令文件副本
├── references/                  # prompt 指南副本
├── 01-scripts/                  # 阶段 01、03、05 产出
│   ├── series-bible.md
│   ├── character-bible.md
│   ├── episode-skeleton.md      # 分集骨架（每集 3-5 beat）
│   ├── narrative-state.md       # 叙事状态追踪
│   ├── lighting-philosophy.md   # 阶段 03 产出
│   ├── color-palette.md         # 阶段 03 产出
│   └── ep{NN}-script.md
├── 02-moodboard/                # 阶段 02 产出
├── 03-scenes/{场景名}/          # 阶段 06 产出（场景库，按需生成）
├── 04-character/{角色}/         # 阶段 04 产出（角色库）
├── 05-videos/ep{NN}/            # 阶段 07 产出
│   ├── seg*.mp4
│   ├── lastframe_seg*.png
│   ├── assets.md                # 按 _convention.md 标准格式
│   └── _backup/                 # seg 重生成时旧版本
├── 06-output/                   # 阶段 08 产出
│   ├── ep{NN}-raw.mp4
│   ├── ep{NN}-final.mp4
│   ├── _backup/                 # 合成重跑时旧版本
│   └── publish/                 # 阶段 11 产出
└── 07-consistency-check/        # 阶段 09、10 产出
```

## 五大门禁（全局硬性约束）

> 完整定义和违规后果见 `stages/_convention.md` §五大门禁。本节只列名称，避免多处定义不同步。

1. **Prompt 审核门禁**：调用任何生成 API 前，完整 prompt + 参数必须先给用户审核
2. **即时登记门禁**：生成 → 重命名 → 登记 assets.md 三步连贯，禁止批量补录
3. **STATE.md 门禁**：每个阶段完成立即更新 STATE.md，不更新不进下一阶段
4. **narrative-state 门禁**：剧本（阶段 05）确认后必须更新 narrative-state.md，否则不进阶段 07
5. **ASSETS-INDEX 门禁**：任何产生/修改/删除资产的阶段完成后必须同步更新 ASSETS-INDEX.md

## 核心约束

### 必须做
- **STATE.md 门禁**：跨会话唯一恢复入口
- **prompt 审核**：发用户确认后才提交
- **即时登记 assets.md**：生成 → 重命名 → 登记三连
- **更新 narrative-state**：剧本确认后立即更新，否则不进视频阶段
- **资产删除前备份**：删除或替换资产前必须备份到 `_backup/` 或 `07-consistency-check/`

### 禁止做
- **字幕内嵌**：Seedance prompt 必须禁用字幕生成（"保持无字幕"），字幕在阶段 08 独立烧录
- **编号跳级**：流程按 01-11 连续执行，不跳号
- **seg 批量补录**：禁止先生成多个 seg 再回头补 assets.md
- **重生成前不通知用户**：任何 Seedance 重新生成必须先用户同意
- **术语混用**：beat（骨架节拍）和 seg（视频段）严格区分

### 默认约定
- **依赖链内串行、链间并行**：阶段 07 的 seg 按依赖 DAG 拓扑提交
- **起始画面衔接**：同场景相邻 seg 用 ref-images 起始画面槽位传入上一 seg 的尾帧文件（物理编号按实际传入顺序）
- **ref-images 逻辑槽位**：场景 → 角色A → 角色B → 起始画面 → 补充（缺失跳过，物理编号按实际传入顺序）
- **用户确认分级**：P0 全确认（EP01）→ P1 批次确认（EP2-5）→ P2 预授权批处理（EP6+，仅阶段 07）
- **逐集独立**：每集起始画面重新生成，不沿用上集
- **对白双引号**：prompt 中对白用双引号包裹
- **场景库复用**：同场景跨集复用同一张 main.png，新场景按需补充
- **环境音分离标注**：prompt 中环境音用 `<>` 包裹
- **合成方式**：纯 concat 拼接，不加转场

## 术语表（强制遵守）

| 术语 | 含义 |
|------|------|
| **beat** | 骨架里的剧情节拍（episode-skeleton 中每集 3-5 个 beat） |
| **seg** | 视频片段（`seg{N}.mp4`） |
| **起始画面** | 视频段首帧（通过 ref-images + prompt 声明） |
| **尾帧** | 视频段末帧（`lastframe_seg{N}.png`） |
| **voice-ref** | 角色音色参考（`voice-ref.mp3`） |
| **金标准** | 角色 front.png / 场景 main.png |
| **multiview** | 多视图组合图（传入 Seedance 的 ref-images） |
| **narrative-state** | 叙事状态追踪文件 |

完整术语表见 `stages/_convention.md`。

## 版本化与备份

| 资产 | 版本化机制 | 备份位置 |
|------|----------|---------|
| seg 视频 | `regen_seg.sh` 自动版本化 | `05-videos/ep{NN}/_backup/` |
| raw/final 成片 | `composite.sh` 自动备份旧版 | `06-output/_backup/` |
| seg assets.md 中的 prompt | 版本历史块（v1/v2/v3），不覆盖 | `assets.md` 内联 |
| 资产手动修改 | 手动备份到 `_backup/` 或 `07-consistency-check/` | 同左 |

## 跨项目资产复用

同世界观的续作可复用角色库、场景库、Moodboard：

```bash
python3 <ai-manju>/scripts/init_project.py <新项目名> --from-template <源项目名>
```

默认复用：
- `04-character/` 角色库（外观 + multiview + voice-ref）
- `03-scenes/` 场景库
- `02-moodboard/` 风格板
- `01-scripts/lighting-philosophy.md` + `color-palette.md` + `visual-style-spec.md`
- `01-scripts/character-bible.md` ⚠️（见下方警告）

不复用：剧本（`ep{NN}-script.md`）、`series-bible.md`、`episode-skeleton.md`、`narrative-state.md`、视频产出（需重新创作）。

### ⚠️ character-bible 复用警告

character-bible 包含角色的 **Want/Need/Flaw/Ghost** 四维——这些是**剧情背景**，不是外观。复用时注意：
- 如果新剧是同世界观续作（如第二季），四维可以沿用
- 如果新剧只想借**角色外观**不借背景（如"同一张脸演不同人"），必须手动**清空 Want/Need/Flaw/Ghost 四维**，保留外在描述和语言指纹（语言指纹可选保留）
- 不清空会导致新剧人物动机受旧剧污染，角色行为不符合新剧设定

`init_project.py --from-template` 执行后会提示复用了 character-bible，用户必须检查并按需清理。

## 依赖

- `video-generation` skill（Seedance + Seedream 脚本）
- `tts` skill（角色音色参考，可选）
- FFmpeg
- `faster-whisper`（字幕自动对齐，pip install faster-whisper）
- `zhconv`（繁简转换，pip install zhconv）

## 工具脚本

- `scripts/init_project.py` — 初始化项目（支持 `--from-template`）
- `scripts/composite.sh` — 合成成片（concat 拼接，自动备份旧版）
- `scripts/regen_seg.sh` — 重新生成单 seg（版本化、备份、更新 assets.md）
- `scripts/batch_gen.py` — 批量生成一集所有 seg（读 seg-config.py，自动依赖调度+并发+重命名+更新 assets.md+生成 batch-report.md）
- `scripts/align_srt.py` — Whisper 词级字幕自动对齐（faster-whisper + zhconv）
- `scripts/validate_script.py` — 剧本正文 vs 汇总表一致性校验（阶段 05 验收，治理教训 #16）
- `scripts/regen_assets_index.py` — 扫描项目资产生成 ASSETS-INDEX.md（门禁 5，支持 `--check` CI 模式）
- `scripts/render_assets.py` — 从 seg-config.py 单源渲染 assets.md 段详情（治理教训 #15 双写）
- `scripts/drift_check.py` — 跨集漂移热检测（色调检查始终可用，面部/音色需 insightface+pyannote）

## 参考

- `stages/_convention.md` — 阶段文件格式规范、术语表、四大门禁、assets.md 标准格式
- `references/prompt-guide.md` — prompt 模板 + 审查清单 + 精简流程 + 内心独白指南 + 细节防错规范
- `references/workflow-detail.md` — 分步详解

## 未来优化 TODO

以下改进已识别但尚未实施（保留给后续迭代）：

- **narrative-state checkpoint 机制**：每 5 集把已兑现伏笔和已揭露信息归档到 `narrative-state-archive/ep01-05.md`，主文件保留活跃条目（避免 20 集后文件过长）
- **P1 批次审核 AI 预审标红**：AI 预审时标出"高风险段"（3 角色同框、复合动作、手部特写、镜面反射），用户重点审核
- **字幕 SRT 烧录前 diff**：align_srt 烧录前把 SRT 与剧本对白汇总表做编辑距离对比，差异大时警告
- **drift_check 完整实现**：`drift_check.py` 的骨架已就绪，面部/音色 embedding 提取逻辑待补完
  - **面部检测**：集成 insightface（MIT 协议，无需 API Key，首次运行自动下载约 200-300MB 模型）
  - **音色检测（推荐方案）**：用 Resemblyzer（MIT 协议，完全免登录，一行 `pip install resemblyzer` 即可）
  - **音色检测（高精度可选）**：pyannote.audio —— 库本身免费但模型是 HuggingFace gated model，需要用户注册 HF 账号 + 接受条款 + 配置 `HF_TOKEN`。适合对音色一致性有更高要求的项目
  - 实施时优先 Resemblyzer 作为默认方案，pyannote 作为 opt-in 高精度模式（`--backend pyannote`）
