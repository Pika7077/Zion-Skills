# 人物输出 Schema

## 顶层结构

```json
{
  "meta": { ... },
  "characters": [ ... ]
}
```

## meta 对象

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| source | string | 是 | "剧本" 或 "视频" |
| source_file | string | 是 | 源文件名（含扩展名）；直接文本输入填 `inline-input` |
| file_type | string | 是 | "txt" / "md" / "docx" / "pdf" / "mp4" / "mov" / "avi" / "mkv" / "webm" |
| processed_at | string | 是 | ISO 8601 格式处理时间 |
| extraction_run_id | string | 新提取结果必填 | 每次提取的唯一 UUID；用于区分同名来源、多份内联输入及重复运行 |
| total_characters | integer | 是 | 识别出的总人物数 |
| extraction_notes | string[] | 否 | 提取过程中的备注说明 |
| video_metadata | object | 否 | 视频源专有元数据 |

### video_metadata 对象（仅当 source=视频）

| 字段 | 类型 | 说明 |
|------|------|------|
| duration_seconds | number | 视频时长（秒） |
| resolution | string | 分辨率，如"1920x1080" |
| fps | number | 帧率 |
| codec | string | 编码格式 |
| asr_available | boolean | 是否成功进行了语音识别 |
| asr_quality | string | "high" / "medium" / "low" / "unavailable" |
| asr_tool | string | 使用的ASR工具/服务名称 |

## characters 数组

每个元素为一个 `Character` 对象：

### Character 对象完整字段

```json
{
  "id": "char_001",
  "extraction_id": "550e8400-e29b-41d4-a716-446655440000:char_001",
  "asset_id": null,
  "name": "林婉儿",
  "aliases": ["婉儿", "林小姐"],
  "gender": "女",
  "age_range": "25-30岁",
  "role_level": "主角",
  "first_appearance": "第3场",
  "appearance_count": 12,
  "appearance": {
    "hair": "及肩黑色直发，刘海斜分",
    "face": "鹅蛋脸，双眼皮，肤色白皙偏冷白",
    "body_type": "体态纤细，身高约165cm",
    "height": "约165cm",
    "skin_tone": "冷白皮",
    "distinguishing_features": ["左手腕有一道浅色疤痕"],
    "clothing_style": "偏好简约干练的职场风格，常穿白色衬衫+高腰西裤"
  },
  "personality": {
    "core_traits": ["聪明冷静", "外冷内热", "完美主义"],
    "behavior_patterns": [
      "紧张时会下意识摩挲左手腕的疤痕",
      "说话前习惯停顿两秒思考"
    ],
    "emotional_style": "不善表达情感，用行动代替言语",
    "strengths": ["逻辑清晰", "临危不乱"],
    "weaknesses": ["过度压抑情感", "不擅长求助"]
  },
  "background": {
    "occupation": "律师事务所合伙人",
    "social_class": "都市中产",
    "education": "法学硕士",
    "family": "单亲家庭，母亲早逝，与父亲关系疏远",
    "backstory": "从小成绩优异，靠奖学金读完大学。母亲去世后与父亲关系恶化，独自在城市打拼。"
  },
  "relationships": [
    {
      "related_character": "陈墨",
      "relation_type": "同事/潜在感情线",
      "description": "律所新来的年轻律师，与林婉儿从对立到互相欣赏",
      "strength": "核心",
      "dynamics": "从师生关系到对等关系"
    },
    {
      "related_character": "林建国",
      "relation_type": "父女",
      "description": "关系疏远，多年未见，是林婉儿不愿提起的过去",
      "strength": "重要",
      "dynamics": "回避→认知→和解"
    }
  ],
  "dialogue_style": {
    "tone": "冷静克制，偶尔带讽刺",
    "habits": ["爱用反问句", "说话简短有力，不说废话"],
    "pace": "偏慢，每句话前有停顿",
    "keywords": ["法律术语频率高", "常用'我认为''基于事实'开头"],
    "sample_lines": [
      "'证据呢？没有证据的事就不要浪费时间。'",
      "'我从不相信感觉，我只相信逻辑。'"
    ]
  },
  "visual_dna": {
    "visual_symbol": "左手腕的疤痕——母亲去世那年留下的",
    "color_scheme": "冷色调为主，白色+深蓝+灰色，少量酒红点缀",
    "posture": "坐姿挺直但肩部微含，习惯性自我保护的体态",
    "gait": "步幅偏小、落步轻，走路时重心微前倾，双手习惯插兜",
    "aura_keywords": ["清冷", "克制", "孤独", "坚韧"]
  },
  "evidence_levels": {
    "name": "原文明确",
    "gender": "原文明确",
    "age": "原文明确",
    "appearance": "原文明确",
    "personality": "合理推断",
    "background": "原文明确",
    "relationships": "合理推断",
    "dialogue_style": "原文明确"
  },
  "asr_quality": "N/A"
}
```

## 字段完整说明

### 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 兼容旧消费者的局部序号，如 `char_001`；只在本份结果内唯一，不能作跨文件或稳定资产 ID |
| extraction_id | string | 新提取结果必填 | `extraction_run_id:id`；用于批量区分提取记录，同一保存结果内保持不变 |
| asset_id | string/null | 新提取结果必填 | 已确认登记的稳定资产 ID；脚本输出 null，不根据局部序号或姓名自动生成 |
| name | string | 是 | 正式姓名；无姓名者用身份/场景角色描述 |
| aliases | string[] | 否 | 别名/昵称/称谓列表 |
| gender | string | 是 | "男"/"女"/"未知" |
| age_range | string | 是 | 年龄段或具体年龄；无法确定时填"未知" |
| role_level | string | 是 | "主角"/"重要配角"/"功能角色"/"龙套" |
| first_appearance | string | 否 | 首次出场位置（场次或时间码） |
| appearance_count | integer | 否 | 出场次数 |

### appearance 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| hair | string | 发型描述（颜色、长度、造型） |
| face | string | 面部特征（脸型、五官、皮肤状态） |
| body_type | string | 体型描述 |
| height | string | 身高或区间 |
| skin_tone | string | 肤色 |
| distinguishing_features | string[] | 标志性特征（疤痕、纹身、胎记等） |
| clothing_style | string | 服装风格关键词 |

### personality 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| core_traits | string[] | 2-3个核心性格特质 |
| behavior_patterns | string[] | 典型行为习惯 |
| emotional_style | string | 情感表达方式 |
| strengths | string[] | 性格优点 |
| weaknesses | string[] | 性格缺陷 |

### background 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| occupation | string | 职业/身份 |
| social_class | string | 社会阶层 |
| education | string | 教育背景 |
| family | string | 家庭背景 |
| backstory | string | 关键背景故事 |

### relationships 数组

| 字段 | 类型 | 说明 |
|------|------|------|
| related_character | string | 关联人物名称 |
| relation_type | string | 关系类型 |
| description | string | 关系说明 |
| strength | string | "核心"/"重要"/"一般" |
| dynamics | string | 关系动态/发展弧线 |

### dialogue_style 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| tone | string | 语气特点 |
| habits | string[] | 语言习惯列表 |
| pace | string | 说话节奏 |
| keywords | string[] | 高频用词/特征词 |
| sample_lines | string[] | 代表性台词原文摘录（2-3句） |

### visual_dna 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| visual_symbol | string | 视觉符号及来源故事 |
| color_scheme | string | 配色倾向 |
| posture | string | 体态习惯（静态站坐姿态） |
| gait | string | 行走特征：步幅、节奏、重心与习惯动作。**背影、远景或隐藏型人物靠它被认出**；不露脸镜头较多的角色应写明，材料不足时按"未知"保留 |
| aura_keywords | string[] | 3-5个气质关键词 |

### evidence_levels 对象

每个字段的值必须为以下之一：
- `"原文明确"`：原文直接陈述
- `"合理推断"`：由2+条独立信息交叉推断
- `"设计补全"`：为完整性提出的可替换设计
- `"未知"`：无法获取任何信息

`age_range` 保留在人物卡中。是否把年龄直接写入图像或视频提示词，由用户要求、目标模型、合规条件和表现效果决定。

### asr_quality 字段

仅视频来源时有效：
- `"high"` / `"medium"` / `"low"` / `"unavailable"` / `"N/A"`（非视频源）

## 批量合并 JSON 结构

批量合并按来源记录的 `extraction_id` 追溯，不按裸 `id` 去重。同一人物只有经证据核对才共用 `asset_id`；未确定是否同一人的记录分别保留，`asset_id` 为 null。旧结果升级与稳定身份映射按 [资产登记与交接](asset-registry-and-handoff.md) 执行。每次重新提取都会生成新运行标识，不能仅凭相同姓名沿用上次映射。

```json
{
  "meta": {
    "batch_source": "多文件批量处理",
    "file_count": 3,
    "processed_at": "2026-08-12T10:40:00+08:00",
    "total_unique_characters": 12,
    "source_files": ["file1.txt", "file2.txt", "file3.mp4"]
  },
  "characters": [
    // 去重合并后的所有人物
  ],
  "merge_notes": [
    {
      "character": "林婉儿",
      "asset_id": "char_lin_waner",
      "source_extraction_ids": ["550e8400-e29b-41d4-a716-446655440000:char_001"],
      "appeared_in": ["file1.txt", "file2.txt"],
      "info_consolidated": true,
      "conflicts": []
    }
  ]
}
```
