---
name: zion-storyboard
description: 把已有剧本或大纲转成制作级导演分镜、画幅适配、场面调度、镜头时间线和视频生成提示词，并优化既有分镜。剧本创作、人物/场景/道具资产和专项验收分别使用 zion-script、zion-assets、zion-qa。
---

# Zion Storyboard：导演分镜与视频制作

负责“故事如何被拍出来”。先设计事件、调度、信息揭示和连续状态，再选择景别、机位、运动、灯光、转场、声音和生成分组。资产身份与图像提示词由 `zion-assets` 管理。

## 决策边界

**第一原则：分镜服务剧本。** 镜头必须更好地展示时间过程、故事走向、人物情绪、冲突、场景关系、旁白和画外声。镜头数、运镜、长镜头、固定镜头、特写和观察方式均无默认配额；判据见 [导演决策标准](references/directing-policy.md)。

冲突依次服从：用户明确要求与已确认规格；原剧本事实与揭示顺序；已登记资产；连续性与可读性；已核验模型限制；导演选择与风格偏好。

默认可补充不改变剧情的表演、环境互动、普通陈设和物理反馈，并标明补充范围。严格原文任务只调整拍法；改变剧情、对白、人物动机或明确时长前，需用户选择。

分镜不得重新设计资产。已有资产使用稳定 ID 与真实引用；缺失项进入需求清单，不假装已经制作、上传或绑定。

## 需求与交付范围

继承上下文中已有材料、规格和授权，只询问无法合理判断且会改变交付的缺口：输入完成度、交付范围、原文保真程度、平台/画幅/时长、目标视频模型、视觉与声音方向、资产状态和禁改项。

纯导演稿不询问模型。需要视频提示词但未指定模型时，使用 [模型适配](references/10-engine-constraints.md) 中维护的默认模型、版本与单次预算，并在元数据中标明默认来源；不把默认采用说成用户确认或生成验证。

- 粗分镜：事实、空间、事件覆盖与资产缺口。
- 正式导演稿：逐镜拍法、时间、声音和连续状态。
- 视频生成稿：在导演稿上核对模型、预算与真实引用，输出自足生成块。
- 局部优化：只读相关参考并检查受影响的前后状态；除非需要结构化导出，不重走全流程。

纯剧本创作交给 `zion-script`；资产与图像提示词交给 `zion-assets`；独立审计、投喂前检查和结果验收交给 `zion-qa`。相关技能不可用时，完成本技能范围并列明缺口，不声称调用成功。

## 制作流程

### 1. 建立事实与空间

提取对白、行动与结果、场景时间、在场人物、进出场、道具归属、伤情、声源和揭示顺序，区分原文事实与导演补充。建立出入口、人物位置与朝向、行动路径、视线对象、关键物件、光源和轴线的文字空间草图。

新建或重排场次时读 [画面内容设计](references/visual-storytelling.md) 与 [三步引导法](references/27-guidance-three-steps.md)；打斗、追逐和复杂接触读 [动作编排](references/action-choreography-rules.md)。

### 2. 粗分镜与资产需求

按事件、关系和空间设计必要覆盖。核对资产包的 `project_id`、剧本版本、场次 ID、资产 ID、版本、状态、文件和目标入口引用：正式导演稿使用有真实文件的 `approved` 资产；生成提示词只使用已 `uploaded` 且具有入口引用的资产。缺失项写成可交接需求。

### 3. 设计事件、反馈与镜头

先写目标、阻力、尝试、反馈、选择和局势变化，再决定切镜。物理互动写清施力、接触、方向/阻力、材质或身体反馈、声音时点和可继承末态。

按镜头任务选景别与观看位置，再定观察关系、构图和运动。透视由拍摄距离决定，焦段只决定视角宽窄；不得由焦段反推机位距离。镜头选择读 [镜头语言](references/camera-vocabulary.md)，画幅读 [画幅导演](references/aspect-ratio-directing.md)，焦段与质感读 [摄影机与质感词库](references/13-camera-and-texture.md)，画面扁平时读 [层次感](references/28-layered-depth.md)。

灯光读 [光影系统](references/20-lighting-system.md)，多人关系读 [人物关系构图](references/21-relationship-composition.md)，人物与摄影机移动读 [场面调度](references/34-staging-and-blocking.md)，色调读 [色彩与影调](references/23-color-and-tone.md)；只有颜色承担叙事结构时再读 [色彩的结构功能](references/36-color-as-structure.md)。

### 4. 配平时长与生成组

按 [剧本保真与时长](references/script-fidelity-gates.md) 先安排对白、声音、必要读取和动作过程，再确定组长。生成组按目标模型在 [模型适配](references/10-engine-constraints.md) 中的已核验上限与项目预算拆分，落在可继承状态；生成组不等于叙事段落。

同一连续世界内的切换可组内写切点；跨时间、空间或概念则逐镜生成并在后期组接。跨组时读 [跨生成组的接缝](references/30-segment-joining.md)。

### 5. 设计剪辑、视点与段落

- 同场切镜、场次转场和序列分隔：[剪辑与转场](references/22-editing-and-transitions.md)。
- 相邻镜关系、时长、动作切点和已有素材不匹配：[剪辑逻辑、时长与切点](references/29-cut-logic-and-timing.md)。
- 时间、情绪、概念、交叉剪辑、分屏、替代画面或重复段落：[蒙太奇段落](references/32-montage-sequences.md)。
- 时间跳跃、双线并行、倒叙插叙：[跨时空转场](references/31-cross-time-transition.md)。
- POV、不可靠叙述与主客观组合：[主观性与 POV](references/33-subjectivity-and-pov.md)；梦境和幻觉另读 [梦境与幻觉](references/35-dream-and-hallucination.md)。
- 跨镜复现意象：[视觉母题与呼应](references/24-visual-motifs.md)；第一镜、最后一镜和人物首次出现：[开场与结尾设计](references/25-opening-and-ending.md)。

每次真实剪辑独立编号；长镜头内部使用时间阶段。焦段、光圈和摄影参数只在影响画面或制作时写；机身与镜头不进入生成提示词的硬参数位。

### 6. 视频提示词

所有模型共用 [视频提示词卫生](references/12-prompt-hygiene.md) 与 [声音设计、对白与音画关系](references/15-audio-and-lipsync.md)。目标为默认模型时读取 [Seedance 渲染器](references/seedance-prompt-renderer.md)；目标为 MiniMax H3 时读取 [MiniMax H3 适配](references/16-minimax-h3-adapter.md)；其他模型只使用已核验规格。结构化字段见 [输出契约](references/output-schema.md)。

保留详细导演稿；生成块只写目标模型需要的可见、可听指令。资产使用真实入口映射，已锁定身份时不重复外观。复杂反射、多人、文字、连续接触和时空变化按风险给替代拍法或后期方案。

### 7. 检查与交付

按 [交付前检查](references/17-stage5-checklist.md) 先过常开门槛，再只读取命中的条件检查。已有失败样本时读 [失败模式](references/11-failure-modes.md)；关键镜头、组接故障、合成或精确文字读 [后期可救性与合成交接](references/37-post-and-recovery.md)；字幕、多语言、无声观看、色觉、闪烁或多平台版本读 [无障碍、本地化与最终交付](references/38-accessibility-localization-delivery.md)。

完整 JSON 可运行：

```text
python scripts/export_output.py input.json --validate
python scripts/export_output.py input.json --audit
python scripts/export_output.py input.json --format markdown --output output.md
```

脚本通过只代表结构检查通过，不等于艺术质量或生成验证。输入文档或视频需要预处理时可运行 `python scripts/parse_input.py <file>`。

## 交付契约

| 请求 | 默认交付 |
|---|---|
| 粗分镜 | 参数摘要 + 空间草图 + 事件覆盖 + 资产需求清单 |
| 正式导演分镜 | 参数与补充范围 + 资产引用表 + 逐镜导演分镜 + 连续状态 |
| 分镜加视频提示词 | 正式导演分镜 + 按模型预算拆分的自足生成块 |
| 局部优化 | 指定镜头/字段的修改结果 + 受影响连续链 |

每镜写 `source_scene_id`、时间、拍法、完整画面过程、真实资产引用、必要物理反馈、对白/声音、切点和承接状态。禁止用“同上”省略独立生成块所需信息；项目级公共参数不在每镜机械重复。

可复跑的行为判据见 [人工案例](tests/manual-regression.md)；自动结构与导出行为见 [脚本回归](tests/test_storyboard_audit.py)。
