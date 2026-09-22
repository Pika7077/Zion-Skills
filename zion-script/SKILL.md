---
name: zion-script
description: 创作、改编和细化 AIGC 短片或短剧剧本。适用于从题材、构思、一句话创意或已有正文发展故事、场次与对白；资产制作、导演分镜和验收分别使用 zion-assets、zion-storyboard、zion-qa。
---

# Zion Script：剧本创作

负责“写故事与剧本”。产出深度跟随用户要求，不默认扩张为完整制作包。

## Zion 家族统一规则

遇到冲突时按以下顺序处理：

1. 用户本轮明确要求，以及已经确认的平台、画幅、时长、模型和交付范围。
2. 用户提供的原始故事事实、对白、人物关系与修改权限。
3. 本次交付契约：内容完整、可读、时长可行、跨场连续。
4. 已核验的目标模型或平台限制；未核验的经验不得写成硬限制。
5. 风格偏好、模板和默认值。

继承已确认的平台、画幅和视觉方向。纯剧本若不依赖画幅即可继续；需要简版镜头构想时再按平台与构图需求采用合理画幅并说明，仅在关键冲突无法判断时询问。剧本阶段不询问或预设生成模型。

用户未指定交付物时，交付满足请求所需的最小完整结果，不附加资产表、逐镜生成提示词、小说版或宣传文案。

## 可执行条件

先继承会话中已有的信息，只收集会改变故事或交付的内容：核心故事或待处理正文；目标时长、集数与平台；已定人物、关系、结局和不可修改项；需要的交付物；实际影响叙事的视觉要求。

“创作、扩写、改编”等请求已授权其范围内的创作选择，无需“你定”等额外口令。材料足以动笔时直接写，必要时简述假设；可逆的细节可以在范围内补全，不为填满需求表连续追问。

缺少核心材料、必须遵守的关键方向，或受保护事实互相冲突时，先问能解除阻碍的简短问题；相关问题可合并，同时推进无依赖的部分。用户指定逐项沟通时遵循该偏好。局部润色只处理目标段落，不重建整套世界观。

需要图片或视频提示词时，先锁定剧本事实，再分别交给 `zion-assets`、`zion-storyboard`。

## 承接范围

- 从创意、题材或一句话故事创作剧本。
- 扩写、改编、重写、续写或细化已有剧本。
- 设计故事结构、场次、对白、人物弧线和必要的视觉动作。
- 用户明确要求时，附加节拍表、场次表、简版镜头构想或制作备注。

以下请求交给对应 skill：

- 人物、场景、道具或其他资产的提取、设计、图像提示词与登记：`zion-assets`。
- 已有剧本或大纲要制作级导演分镜、画幅适配、资产引用或视频提示词：`zion-storyboard`。
- 文件、可读性、提示词或生成结果验收：`zion-qa`。

若请求同时包含创作和制作，先在本档完成或补齐剧本事实，再按需要由 `zion-assets` 建立资产、由 `zion-storyboard` 完成分镜；不得在后续阶段重复改写已确认内容。

相关技能未安装或不可读时，完成剧本范围内的交付和明确的制作需求，不声称已调用其它技能或已完成制作。

进入下游前给项目分配稳定 `project_id`、剧本版本 `script_version`，并给每场分配不随标题或顺序轻易变化的 `scene_id`（如 `SC001`）。修订剧本时递增版本并列出受影响场次，供资产、分镜和 QA 判断旧交付是否失效。

## 工作方法

1. 建立故事约束：题材、目标观众、时长、平台、核心人物、冲突和用户要求保留的事实。核心冲突按四要素检查（双方目标不能同时成立、筹码与代价、阻碍的可见形式、退路），见 [故事设计](references/03-story-requirements.md) 的冲突构造一节。确定这部戏给观众的情绪经验与每场兑现的情绪回报，判据与选择集见 [受众期待与情绪回报](references/13-audience-and-payoff.md)；不自行假设观众群体。
2. 选择适合内容的结构，不强制三幕式、固定钩子时点或固定反转频率。分集讲述时同时安排单集曲线与全剧曲线、切开类型与三张跨集状态表，见 [分集连载](references/14-serial-structure.md)。项目有明确类型或混合类型时，再按 [类型机制](references/16-genre-mechanics.md) 锁定观看承诺、推进证据与回报，不把类型当美术标签。
3. 写场次与对白。需要写场、改场、删场、组织多场序列或诊断流水账时，读取 [分场结构](references/15-scene-architecture.md)，先分清镜头—场—序列—幕的实际边界，再核对进入状态、当场目标、策略与阻力、转向和退出状态；不要求每场都有冲突、完整起承转合或固定节拍。对白按语言指纹、潜台词、推进力、信息效率与时长自检；需要时读 [对白设计与诊断](references/04-dialogue-design.md)。落笔写正文时按 [剧本正文](references/17-script-page-and-format.md) 的格式：动作行只写可拍可听，场标含稳定 `scene_id`，对白标明说话人与来源。
4. 把关键情绪落实为可观察的表演、行动、空间距离或声音；FACS 只在它能提高表演精度时使用，不强制逐句编码。
5. 检查人物动机、信息顺序、时长、前后状态和结尾完成度；人物变化与作品主张是否对得上（见 [人物弧线与主题](references/18-character-arc-and-theme.md)），高风险场面与画面内文字是否已随交付标注（见 [可生成性对剧本的约束](references/21-script-generatability.md)）。

用户要求严格原文时，只做授权范围内的编辑。用户允许创作补全时，可以补充合理的场景、表演和过渡，但不得悄然改变核心关系、动机或结局。

## 输出契约

| 请求 | 默认交付 |
|---|---|
| 写剧本 | 项目参数简述 + 场次式完整剧本 |
| 扩写或改写 | 修改后的目标段落或完整版本 + 必要的改动说明 |
| 故事设计 | 一句话故事 + 人物与冲突 + 结构大纲 |
| 要求制作信息 | 仅附用户点名的节拍、简版镜头构想或制作备注；图像/视频提示词交给对应下游 Skill |

剧本中需要呈现的信息写清楚；不为了填表强制输出固定 43 项、固定人物字段数、固定镜头数或完整摄影参数。用户要求附带简版镜头构想时，按参考路由读取相关文件；制作级逐镜稿交给 `zion-storyboard`。

## 质量标准

- 人物选择有动机，结果由行动和因果产生。
- 每场保留理由可说明，进入与退出之间存在信息、关系、处境、物理状态或观众预期的有效差值。
- 有明确类型时，关键场次持续提供该类型承诺所需的推进证据，最终回报能回指前文铺垫。
- 情绪回报有铺垫支撑；关键爆点同时满足期待与出人意料，且结果由前文信息支撑（见 [受众期待与情绪回报](references/13-audience-and-payoff.md)）。
- 台词符合人物身份，避免重复解释观众已经看到的信息。
- 正文只写可拍可听的内容：动作行不含摄影机与调色指令，场标、声音来源与说话人标注完整（见 [剧本正文](references/17-script-page-and-format.md)）。
- 关键情绪可以被表演、听见或通过行为推断。
- 重要人物、道具、伤情、时间和信息跨场连续。
- 时长约束存在时，朗读、动作和停顿总量可实现。
- 人物判断依据确有变化时，能说出它由哪个外部事件逼出；作品主张能从事件读出，不靠台词宣布。
- 高风险场面、需精确呈现的文字与稀有资产已随交付标注，供下游安排。
- 风格、摄影器材、帧率、钩子位置和闭环形式均按项目需要选择，不设全项目通用硬值。

## 参考路由

- 故事设计： [references/03-story-requirements.md](references/03-story-requirements.md)
- 改编（小说、真实事件、已有剧本或梗概）： [references/19-adaptation.md](references/19-adaptation.md)
- 分集连载（多集）： [references/14-serial-structure.md](references/14-serial-structure.md)
- 分场与序列结构（写场、改场、删场、组织多场段落）： [references/15-scene-architecture.md](references/15-scene-architecture.md)
- 叙事顺序与信息管理（非线性、闪回、观众与角色的知情差）： [references/20-narrative-order-and-information.md](references/20-narrative-order-and-information.md)
- 类型机制（悬疑、喜剧、恐怖、关系、动作、群像或混合类型）： [references/16-genre-mechanics.md](references/16-genre-mechanics.md)
- 受众期待与情绪回报： [references/13-audience-and-payoff.md](references/13-audience-and-payoff.md)
- 对白设计与诊断（含旁白与独白）： [references/04-dialogue-design.md](references/04-dialogue-design.md)
- 正文写法与格式（场标、动作行、对白标注）： [references/17-script-page-and-format.md](references/17-script-page-and-format.md)
- 人物与世界（含修订与影响范围）： [references/11-character-and-worldbuilding.md](references/11-character-and-worldbuilding.md)
- 人物弧线与主题： [references/18-character-arc-and-theme.md](references/18-character-arc-and-theme.md)
- 表演细化： [references/10-physical-acting.md](references/10-physical-acting.md)
- 明确要求 AU，或需要精确区分相似表情时才读取：[FACS 可选参考](references/facs-reference.md)
- 叙事视觉意图： [references/12-visual-style-and-grading.md](references/12-visual-style-and-grading.md)
- 可生成性对剧本的约束（人数、高风险场面、画面内文字）： [references/21-script-generatability.md](references/21-script-generatability.md)
- 只有明确需要简版镜头构想时： [references/06-shotlist-format.md](references/06-shotlist-format.md)、[references/08-continuity-and-report.md](references/08-continuity-and-report.md)

参考文件中的字段、数字和模板均服务于对应任务；除非用户或项目规格明确要求，不得提升为所有剧本的固定交付项。

行为回归见 [人工回归清单](tests/manual-regression.md)。
