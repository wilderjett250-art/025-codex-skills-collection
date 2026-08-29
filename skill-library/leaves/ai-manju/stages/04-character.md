# 阶段 04：角色设计

> 工具：Seedream 5.0（全身图 + 多视图）+ TTS skill（音色参考）
> ⚠️ 必须先用户确认全身图，再生成多视图
>
> **阶段顺序说明（2026-05-06 重排后）**：04-character → 05-script → 06-scenes。场景图按剧本需要逐集生成，角色库一次出齐。

## 前置条件

- `01-scripts/character-bible.md` 存在（角色内在画像）
- `01-scripts/lighting-philosophy.md` 存在
- `01-scripts/color-palette.md` 存在

## 流程概览

每个角色按三步生成：

| Step | 产出 | 方式 | 用途 |
|------|------|------|------|
| 1 | 全身正面图（9:16 竖版，灰底，无标注） | 独立 prompt 生成 | 锁定外观金标准 |
| 2 | 多视图组合图（16:9 横版，面部特写 + 正/侧/背全身） | 用全身图做图生图 | **传入 Seedance ref-images** |
| 3 | voice-ref.mp3（3-5 秒标志性台词） | TTS 合成 | 传入 Seedance --audio |

> ⚠️ **不需要表情变体**。角色情绪变化靠 prompt 文字描述 + 场景图传递。

## 流程

### 步骤 1：编写全身图 Prompt

参照 character-bible.md 的外在描述 + visual-style-spec 画风规格。

> ⚠️ **Prompt 审核门禁（门禁 1）**：组装完成后，对照 `references/prompt-guide.md` §八「图片 Prompt 审查清单」角色设计专项逐项自查。**批次审核**——所有角色的全身图 prompt 一次性发给用户审核。

**Prompt 结构**（自然语言连贯描述，按以下模块顺序）：

```
{画风关键词}，单人照。
年龄约{N}岁，性别{男/女}，{族裔/时代背景}。
{发色}{发质}{发型结构}，{发饰}。
脸型为{脸型}，{眉形}，{眼型}，瞳色{颜色}，{鼻型}，{唇形}，{肤色}。
体态为{N头身比例}，{身形}，{肩颈/体态特征}，全身正面站立。
灰色背景，无文字，全身正面站立照。
服饰为{主色调}{服装类型}，{结构层次}，{剪裁风格与气质暗示}。
{标识物}作为最重要的个人标识。
鞋子为{鞋子描述}。
服装面料表现为{面料质感}，结构设计{设计理念}。
材质与风格关键词：高质量3D角色设定，{画风}，电影感光影,{角色定位}，{题材}角色标准立绘。
```

### 步骤 2：角色差异化设计（强制）

> 同一个 prompt 跑多个角色，会产出长得像兄弟姐妹的人。必须在每个角色的 prompt 中注入**差异化锚点**。

#### 面容特征对撞表

每个角色的面容必须从以下维度中做出**互斥选择**：

| 维度 | 角色A（示例） | 角色B（示例） | 角色C（示例） |
|------|-------------|-------------|-------------|
| 脸型 | 瘦长瓜子脸 | 方正国字脸 | 圆润鹅蛋脸 |
| 眼型 | 细长凤眼，眼角上挑 | 大圆眼，眼角下垂 | 杏眼偏大，瞳色琥珀 |
| 眉型 | 剑眉，眉尾上扬 | 柳叶弯眉，柔和 | 粗短浓眉，眉头紧锁 |
| 鼻型 | 高挺窄鼻 | 圆润小巧 | 鹰钩鼻，鼻梁微弯 |
| 嘴型 | 薄唇，嘴角下撇 | 厚唇，嘴角微扬 | 小嘴，唇线分明 |
| 下颌 | 尖下巴 | 方下巴 | 圆下巴 |

> ⚠️ 生成前检查：任意两个角色的面容特征是否有 ≥3 项不同？不够就调。

#### 服装差异化原则

- 角色A：丝绸质地，修身剪裁，有光泽
- 角色B：粗麻质地，宽松披挂，有磨损
- 角色C：双层叠穿，内紧外松
- 角色D：单肩披风，不对称设计

### 步骤 3：用户批次确认 + 生成全身正面图

所有角色的 prompt 一次性提交。用户确认后批量生成。

```bash
python3 <video-gen>/scripts/seedream.py create \
  -p "<确认后的全身图 prompt>" \
  --size 9:16 \
  -d ./04-character/{角色名}/
# 重命名为 front.png
mv ./04-character/{角色名}/seedream_*.jpg ./04-character/{角色名}/front.png
```

⚠️ **即时登记门禁（门禁 2）**：生成后立即写入 assets.md（完整 prompt + task_id + 参数）。

**用户确认全身图满意后**，进入步骤 4。

### 步骤 4：生成多视图组合图（图生图）

用全身图做图生图，生成一张包含面部特写 + 正/侧/背全身的组合图。

**Prompt 模板**：

```
{画风关键词}，单人角色设定图。
年龄约{N}岁，性别{男/女}。
外貌特征与参考图完全一致。
服装设计与参考图完全一致。
一张组合图，包含：左侧为面部正面特写（半身），右侧为三个全身站立视角（正面、右侧面、背面），角色保持相同服装和姿势。
灰色背景，无文字，均匀柔光照明。
材质与风格关键词：高质量3D角色设定，{画风}，角色多视图参考图。
```

**生成命令**：

```bash
python3 <video-gen>/scripts/seedream.py create \
  -p "<多视图prompt>" \
  -i ./04-character/{角色名}/front.png \
  --size 16:9 \
  -d ./04-character/{角色名}/
# 重命名为 multiview.png
mv ./04-character/{角色名}/seedream_*.jpg ./04-character/{角色名}/multiview.png
```

> 💡 多视图用 **16:9 横版**（与全身图的 9:16 竖版不同），一张图同时提供面部细节 + 多角度服装信息。
>
> 这张图是后续 Seedance 视频生成的主要 ref-images——不传入全身图，只传多视图。

### 步骤 5：生成角色音色参考（voice-ref.mp3）

> 角色印象由眼+耳共同建立。Seedance 的 `--audio` 参数会模仿此音色生成配音。
> 前置：`tts` skill 已安装，`DOUBAO_TTS_API_KEY` 已设置。

为每个重要角色生成一段 **3-5 秒** 的标志性音色参考：

```bash
python3 <tts-skill>/scripts/doubao_tts.py synthesize \
  --text "{最能体现角色性格的一句台词，3-5秒时长}" \
  --speaker {匹配角色气质的音色} \
  --emotion {角色默认情绪基调} \
  --encoding mp3 \
  -d ./04-character/{角色名}/

# 重命名为 voice-ref.mp3
mv ./04-character/{角色名}/tts_*.mp3 ./04-character/{角色名}/voice-ref.mp3
```

**音色选择参考**：

| 角色类型 | 推荐音色 | emotion |
|---------|---------|----------|
| 霸道男主/反派 | zh_male_qingcang_uranus_bigtts | coldness |
| 清冷男主 | zh_male_ruyayichen_uranus_bigtts | coldness |
| 热血男主 | zh_male_shaonianzixin_uranus_bigtts | excited |
| 高冷御姐 | zh_female_gaolengyujie_uranus_bigtts | coldness |
| 温柔女主 | zh_female_meilinvyou_uranus_bigtts | tender |
| 撒娇萌妹 | zh_female_sajiaoxuemei_uranus_bigtts | lovey-dovey |
| 霸气女帝/太后 | zh_female_wuzetian_uranus_bigtts | coldness |
| 成熟女性/旁白 | zh_female_roumeinvyou_uranus_bigtts | storytelling |

> 完整音色列表：`python3 <tts-skill>/scripts/doubao_tts.py voices`
> 一个角色只生成一个 voice-ref.mp3（标志性台词 + 默认情绪），不搞变体。

### 步骤 6：文件整理与资产登记

```
04-character/{角色名}/
├── front.png           # 全身正面图（金标准）
├── multiview.png       # 多视图组合（传入 Seedance 用）
├── voice-ref.mp3       # 角色音色参考
└── assets.md           # 资产清单
```

**assets.md 模板**：

```markdown
# {角色名} 资产清单

## 全身正面图
| 文件 | 完整 Prompt | 命令参数 | 任务 ID | 生成时间 |
|------|------------|---------|---------|----------|
| front.png | "<完整 prompt>" | --size 9:16 | task_xxx | ... |

## 多视图组合图
| 文件 | 完整 Prompt | 命令参数 | 任务 ID | 生成时间 |
|------|------------|---------|---------|----------|
| multiview.png | "<完整 prompt>" | -i front.png --size 16:9 | task_yyy | ... |

## 音色参考
| 文件 | 音色 ID | emotion | 合成文本 | 任务 ID | 生成时间 |
|------|---------|---------|---------|---------|----------|
| voice-ref.mp3 | zh_female_xxx | neutral | "..." | — | ... |
```

⚠️ **即时登记门禁（门禁 2）**：每生成一个文件立即登记。

## 跨项目复用

本阶段产出的角色库可复用到同世界观的续作项目。使用 `init_project.py --from-template <源项目>` 复制角色库。

## 产出

| 文件 | 说明 |
|------|------|
| `04-character/{角色}/front.png` | 全身正面图（金标准） |
| `04-character/{角色}/multiview.png` | 多视图组合（传入 Seedance 用） |
| `04-character/{角色}/voice-ref.mp3` | 音色参考 |
| `04-character/{角色}/assets.md` | 资产清单 |

## 验收

- [ ] 每个角色有 front.png + multiview.png + voice-ref.mp3
- [ ] 任意两个角色的面容特征 ≥3 项不同（差异化检查）
- [ ] 服装材质和穿法差异化明显
- [ ] 角色标识物在 front.png 中清晰可见
- [ ] 多视图的面部特征与全身图一致
- [ ] voice-ref.mp3 音色与角色气质匹配
- [ ] 资产清单完整（prompt + task_id + 参数）
- [ ] **ASSETS-INDEX.md 已同步更新**（门禁 5，新增角色行）
- [ ] 用户已确认

## 完成后

→ `stages/05-script.md`
将 `STATE.md` 中 `当前阶段` 更新为 `05-script`，勾选 04。
