# 当前分镜输出契约

以下为当前字段规则，兼容旧字段名；配额、焦段映射和数据自带的 passed 值不作为默认验收依据。

默认 Markdown 顺序：情境概况 → 参数和补充范围 → 场景/资产简表 → 逐镜导演分镜 → 分组生成提示词。

按交付范围保留所需区块。局部修改可直接输出受影响内容；纯导演稿省略生成块。场景分析、节奏地图、风格与摄影参数只在输入有实际内容时导出，不补虚构默认值或空模板。`constraints` 可省略；省略不代表禁止配乐或字幕。

正式导演稿每镜写：时间、景别 `framing`、运镜 `camera_movement`（固定也明写）、光线 `lighting`、画面过程、必要物理反馈、声音/对白、切点与连续状态。`lighting` 写本镜可见的光源方向、主体明暗或阴影结果；同场共享设定可简写，但不能只填“同上”或空值，变化时写出变化。画面中确实无物理互动时不硬填。人物位置与朝向写进各镜的画面过程，不另立空间板块或顶层空间字段。

结构化输入中，`shot_number` 为正整数；`framing`、`camera_movement`、`lighting`、`description` 为非空字符串。`time_range` 包含有限数值 `start` 和 `end`，满足 `0 <= start < end`；布尔值不算镜号或时码。生成提示词字段填写时须为字符串。`--validate` 检查这些类型与必要字段，整组时间连续性和容量仍由 `--audit` 检查。

镜头时间承载从起始状态到可见结果的实际过程：先算动作、反馈、读取与反应哪些并行、哪些串行，再定起止时间。能在同一镜读清的连续过程不因阶段数多而拆镜；切镜须有观察或信息任务。生成提示词保留镜内的关键先后与最终画面，不得把 `description` 和 `physical_feedback` 缩成“推开文件”“物件震动”等标签。

JSON 保留旧字段。下表明确字段用途；`lighting` 在正式导演稿中必填，其他字段遵循各自说明：

| 字段 | 用途 |
|---|---|
| meta.handoff_schema_version | 跨 Skill 交接契约版本；新项目使用 `1.0` |
| meta.project_id | 继承剧本的稳定项目 ID |
| meta.source_script_version | 本分镜所依据的剧本版本 |
| meta.source_scene_ids | 本生成组覆盖的稳定场次 ID 列表 |
| meta.target_model | 目标视频模型与版本；用户未指定时从 [模型适配](10-engine-constraints.md) 读取当前默认值，用户指定 MiniMax H3 时按 [MiniMax H3 适配](16-minimax-h3-adapter.md) 输出生成块。只做导演分镜时可为空 |
| meta.image_engine | 旧数据兼容字段；新分镜不负责选择图像引擎，资产图像引擎记录在 `zion-assets` 交接包中 |
| meta.pacing_profile | narrative（默认）/ high_energy / legacy_quota |
| meta.generation_limit_seconds | 包含生成提示词时，填本项目采用的单次预算；用户给定值优先，否则从 [模型适配](10-engine-constraints.md) 读取当前默认模型的已核验上限并说明来源。纯导演稿可空 |
| shots[].shot_function | 镜头带来的叙事作用 |
| shots[].source_scene_id | 当前镜头回指的剧本场次 ID；必须存在于 `meta.source_scene_ids` |
| shots[].asset_refs / character_refs / scene_refs / prop_refs | 当前镜头实际使用的资产引用；每项必须唯一命中 `meta.asset_mode` 中保留 ID、版本、状态和文件映射的交接项 |
| shots[].pov_family | 观察关系，直接写名称：客观正面 / 过肩 / 正侧面 / 侧背 / 正背 / 主观视角 / 反射中介 / 前景遮挡 / 插入细节 / 弧线观察。不使用 V 编号，不在此字段写高/低角度 |
| shots[].camera_height | 机位物理高度：贴地 / 略低 / 眼平 / 略高 / 高位 / 正上方等 |
| shots[].camera_angle | 镜头朝向或滚转：平拍 / 仰拍 / 俯拍 / 鸟瞰 / 虫视 / 斜角（荷兰角）等；与高度分开记录 |
| shots[].lighting | 本镜可见光线：主导光源与方向、主体明暗或阴影结果；沿用场次灯光时简述实际效果，不能只写“同上” |
| shots[].new_feedback | 可见变化、新信息或有意义的等待；每镜填写并人工评审 |
| shots[].physical_feedback | 具体物理因果、反馈与末态；受力时记录支点、接触部位与方向、可见失衡/位移/形变及停止原因，按景别与动作强度取舍 |
| shots[].continuity_in / continuity_out | 位置、持物、动作阶段等入/出状态；本组末镜的 `continuity_out` 即下一组的起手依据，跨组接缝见 [跨生成组的接缝](30-segment-joining.md) |
| shots[].cut_motivation | 切换观察对象的理由；单镜可写“持续观察” |
| shots[].transition_out | 可选；写向下一镜的切换机制、触发时点及 A 末帧/B 首帧锚点。镜内揭示不填成跨镜转场；规则见 [剪辑与转场](22-editing-and-transitions.md) |
| shots[].addition_note | 原文依据或导演补充说明，不进入生成块 |
| shots[].camera_move_triplet | 主动运镜的 origin/direction/stop_result；固定可省略 |
| shots[].internal_beats | 可选；一镜到底或复杂长镜头的内部时间阶段。阶段共享同一 `shot_number`，记录时间、主体/焦点、摄影机路径和新增信息，不作为独立切镜 |
| shots[].generation_prompt | 目标模型的生成指令；独立写出本镜起始空间关系、关键动作及物理反馈的可见先后、落幅与必要声音；有情绪任务时写出造成情绪的空间/关系变化，细节随风险增减。纯导演稿可空，旧数据的 `seedance_prompt` 仍可读取 |
| shots[].post_plan | 可选；需要后期时记录具体目的、所需层、可替换区域、余量和降级路径，不写泛泛“后期优化” |
| shots[].deliverable_variants | 可选；当前镜头涉及的画幅、语言、字幕、声音或内容版本及差异 |
| shots[].accessibility_notes | 可选；无声理解、非颜色单通道、闪烁风险或字幕可读性的项目级处理与待验证项 |
| scenario_brief | 生成组级情境概况：本组在讲什么——场景与时间状态、在场人物、各自正在做的事、彼此关系与当前互动。写给人读、供项目上下文，**不进入生成块** |
| voice_profiles[] | 角色音色设定；每项 `{ref, voice}`，`ref` 指向人物资产，`voice` 写跨台词稳定的音色特征。写法见 [声音设计、对白与音画关系](15-audio-and-lipsync.md) |

物理反馈等新字段为兼容旧数据保持可选，不代表创作可忽略。需要时必须在画面正文和模型提示词里体现，不能只写在分析字段。

台词与声音字段：`shots[].dialogue` 装画内开口的对白，写成 `角色名（语气）："台词原文"`。语气是“怎么说”，与“谁在说”“说了什么”同为对白的必要项，不是可选润色；语气词只写在这一处，不混入画面描述（写进画面会被当作画出来的样子）。无台词写空。画外声（内心独白、旁白）不写入该字段，写进声音描述并标明来源与音色，画面段给出闭口证据。规则见 [音频与对白](15-audio-and-lipsync.md)。

`scenario_brief` 是**概括，不是新增**：只描述本组正在发生的事，不得添加原文没有的人物、事件或结果（与剧本保真的事实锚点一致）。它**不替代**镜行与声音层——写进概况的信息仍须在对应字段出现；也**不进入** `generation_prompt`，生成块保持自足。无需要时可不填，不补空模板。

`voice_profiles` 按角色登记音色，一项一个 `ref`。`voice` 只写跨台词稳定的特征（音域明暗、可听质感、语速范围、停顿与重音习惯、句尾趋势、呼吸习惯、情绪变化时仍保持的锚点），取自 `zion-assets` 的声音身份登记。当前语气与具体台词写在台词语气位，**不写进音色**；没有真实音频文件时只交设计描述，不声称已批准。

时间允许小数秒。正反打是合法独立镜头，焦段与景别不按固定表对应。`focal_length` / `aperture` 为可选字段；旧数据的“未指定”仍可读，不要求新稿填占位值。

`time_range` 参与结构校验与配平，必须保留；但它**不必出现在交付稿里**——按项目要求隐藏逐镜时间时，导出加 `--no-shot-time`，只在段首给出整段/整组时长（见 [SKILL.md](../SKILL.md) 的导出命令）。隐藏的是呈现，不是配平：对白容量、切点与整段预算的判断照做。

详细分镜的新增字段与模型提示词分别导出，不把导演目的放入生成指令。variety_check 是诊断统计；不能由数据自带 passed=true 跳过重新检查。脚本结果不等于源文保真、物理合理性或实际生成验收。


## JSON 最小完整样例

以下为 Seedance 2.5、9:16、单次预算 30 秒的字段示例；30 秒可来自模型默认上限，画幅、人物与内容只是示例，不能推广为项目默认。示例未含资产交接项，使用已登记资产时需另附真实引用映射。

```json
{
  "meta": {
    "source": "script",
    "source_file": "桌前停顿",
    "handoff_schema_version": "1.0",
    "project_id": "PRJ_desk_pause",
    "source_script_version": "script_v1",
    "source_scene_ids": ["SC001"],
    "scene_type": "dialogue",
    "total_duration_seconds": 6,
    "generation_limit_seconds": 30,
    "pacing_profile": "narrative",
    "target_model": "Seedance 2.5",
    "aspect_ratio": "9:16"
  },
  "shots": [{
    "shot_number": 1,
    "source_scene_id": "SC001",
    "time_range": {"start": 0, "end": 6},
    "duration_seconds": 6,
    "framing": "双人中景",
    "camera_height": "眼平",
    "camera_angle": "平拍",
    "pov_family": "正侧面",
    "composition": "桌沿引导视线，手和文件清楚可见",
    "camera_movement": "固定",
    "lighting": "左侧窗光照亮周衡推文件的手，林岚面部右侧留有柔和阴影，两人仍可辨认",
    "description": "桌子左侧是林岚，右侧是周衡，摄影机在桌前一侧；周衡把文件推回林岚面前，林岚收回停在桌面的手。纸张停住后，两人隔桌静默。",
    "physical_feedback": "纸张沿桌面滑移，施力结束后因摩擦停住；摩擦声随滑移停止。",
    "shot_function": "让拒绝通过文件归还和未接取显现",
    "new_feedback": "文件回到林岚面前，林岚没有再次递出",
    "continuity_out": "文件停在桌面，双方手均不接触纸张",
    "cut_motivation": "持续观察拒绝落定后的关系",
    "dialogue": "",
    "generation_prompt": "镜头1（0–6秒）：桌侧双人中景，平视固定，左侧窗光照亮手和文件，人物背光侧保留面部细节。周衡沿桌面将文件推回林岚面前，林岚收回停在桌面的手；纸张滑移后停住，摩擦声停止，两人保持静默。"
  }],
  "ending_state": "文件停在林岚面前，两人隔桌，没有触碰文件",
  "constraints": "保留纸张摩擦声及室内底噪，无新增台词、配乐或字幕"
}
```

一个对象表示一个生成组。多组使用列表，每组独立 meta、时间从零计、完整上下文和末态；批量包装沿用 `results[].data`。整片绝对时间可另记，不能混入组内时间码。

如提供 `fidelity_gate.dialogue_capacity.total_min_seconds`，值为本组实际时间规划占用，并在导演稿说明并行/串行安排。不提供时脚本只做保守估计。新数据不能伪填容量零值以绕过对白规划。

物理反馈在详细稿中可分栏解释，在生成提示词中要回写为实际可见过程。source/addition_note 不自动进入模型提示词。
