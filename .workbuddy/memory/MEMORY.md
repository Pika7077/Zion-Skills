# 工作空间维护约定

## 流程唯一来源（2026-09-20 设定）

工作区由 **codex 与 WorkBuddy 同时维护**。标准循环、硬规则、清理纪律一律以工作区根目录的 **`AGENTS.md`** 为准，本文件不重复，只记长期约定与事实。

工具三件套（均在 `.workbuddy/tools/`）：

- `skill_lint.py` —— 内容校验：JUNK／ORPHAN／DUPLICATE／DANGLING／**SECTION_REF**／CROSS／`--meta`。
- `skill_guard.py` —— 并发守卫：写租约 `acquire`／`release`／`status`，基线 `snapshot`／`check`。
- `sync_skills.py` —— 安装目录镜像，`--target codex|workbuddy` 只写自己那份。

## 独立安装口径（2026-09-20 拍板）

四个技能都必须能单独取用，同时保持家族一起装的体验。

- 跨技能引用只写技能名与档名（“`zion-storyboard` 的光影系统档”），**不写相对路径**，单独安装时零断链。由 `skill_lint.py` 的 CROSS 项守护（计入问题，退出码 1）。
- `parse_input.py` 在 `zion-assets` 与 `zion-storyboard` 各存一份完整副本（第 2 行注释已声明共用），供各自单独安装；两份内容须一致。
- 不要用“薄壳委托”或“指向另一技能目录的相对路径”解决此类问题——会让单独安装功能缺失。


## 并发写入：已发生的两起事故（2026-09-20）

工作区被两个会话同时写入是**常态**（用户明确要求 codex + WorkBuddy 并行优化）。已实测到：

- `zion-script/references/12-visual-style-and-grading.md` 被另一会话整篇替换（约 170 行词库版 → 35 行“剧本阶段锁定视觉事实”版），我当时的改动被覆盖。
- `05-scene-and-color-bible.md`、`07-prompt-spec.md` 被删除且引用同步清理；`.workbuddy/skills` 中的旧副本已抢救到 `.workbuddy/archive/source-deleted-2026-09-20/`（用户决定不再恢复）。

应对：写租约 + 基线快照（`skill_guard.py`），规则见 `AGENTS.md`。工作习惯上——

- 收工前必跑 `skill_guard.py check`，凡是自己没改过的文件出现在漂移列表里，先对齐再继续。
- 删除类改动先归档；源文件被对方删除时从安装目录抢救副本。

## 风格与色彩：单一来源地图（2026-09-21 核对）

交叉引用只写技能名与档名，不复制内容。维护某一项时改这里，别处只引用：

| 内容 | 唯一来源 |
|---|---|
| 题材美术（形制／材质／器物／色板／锁定项） | `zion-assets/references/19-genre-style-profiles.md` |
| 场景一致性与状态阶梯（场景闸门／竖屏动线／S0–S5／跨 View 光线／空场政策／环境叙事／视频可用性预检／**取舍顺序与三项核心质感／俯视空间位置图**） | `zion-assets/references/26-scene-consistency.md` |
| 视觉语言（构图／镜头／调度／光色气质，含影人拆解） | `zion-assets/references/director-vision-language.md` |
| 成像响应（胶片颗粒／宽容度／印片黑位与色彩密度） | `zion-assets/references/film-and-print-stocks.md` |
| 数字机身与焦段（ARRI ALEXA 家族／焦段透视逻辑／镜头／光圈） | `zion-storyboard/references/13-camera-and-texture.md` §二 |
| **镜头语言：景别与观看位置、建立镜的空间任务、深焦/选择性焦点、短长镜头、具名运镜的可执行路径** | `zion-storyboard/references/camera-vocabulary.md` |
| 调色词库、八种调色预设、可选 60:30:10 配色、风格锚点、**Anti-Slop 替换表、Register Poles** | `zion-storyboard/references/13-camera-and-texture.md` §六 |
| 色系（冷/暖/对比/高饱和/低饱和/暗黑/霓虹/糖果/小清新）、影调档（明度×饱和七色调）、**场景与剧情的色调一致性**、共同色偏、**全片影调弧线**、色彩叙事推进 | `zion-storyboard/references/23-color-and-tone.md` |
| 视觉母题三类与母题表、复现四手法 | `zion-storyboard/references/24-visual-motifs.md` |
| 开场五式、收束四式、首尾呼应、分集结尾切口、**特写起手与后续释义、钩子四类型索引与克制原则、小屏取向、开篇四项功能与避坑（不交代设定／反常反应／苛刻条件）** | `zion-storyboard/references/25-opening-and-ending.md` |
| **场次内的重点分配（记忆锚）、期待节奏与信息时序、关系预埋与危险暗示** | `zion-storyboard/references/27-guidance-three-steps.md` |
| **层次感四维（空间纵深与偷空间／主体-背景分离与渐变光／颜色抠主体／表演与叙事层次）** | `zion-storyboard/references/28-layered-depth.md` |
| 光位／光比／配光层级／色温／灯光律／**机身宽容度与光比的可用性**／**光的演变（四轴+三速）** | `zion-storyboard/references/20-lighting-system.md` |
| **剪辑进度与关系：30°/180°、视觉变化量三测、极端两级跳档的重新定位、动势匹配、不匹配素材的调和/桥接/注意力转移/重做、水平翻转闸门、单镜读取时长、心理时间、切点与动作阶段、3:7 出接动作、跳剪、判断权次序、视线落点承接、反应镜头** | `zion-storyboard/references/29-cut-logic-and-timing.md` |
| **跨生成组接缝：末态具体化、接缝换机位、空镜三用法** | `zion-storyboard/references/30-segment-joining.md` |
| **跨时空转场：镜内／镜间两族、时间关系三分、切换可察觉性判据、可生成性分级** | `zion-storyboard/references/31-cross-time-transition.md` |
| **蒙太奇段落：两种目的、意义来自组合与顺序（换序判据）、减法/加法、四种功能 × 四种关系、分屏同时信息、闪切与实现路径、隐喻陷阱** | `zion-storyboard/references/32-montage-sequences.md` |
| **主观性与 POV：视点归属与漂移、身体局部入画与位置稳定、在场感三件套（防悬浮）、提示词写法（按可见事实而非术语）、情感物、与客观镜头交替、人称选择、声音次序、主观状态标记、不可靠叙述的公平条件** | `zion-storyboard/references/33-subjectivity-and-pov.md` |
| **生成粒度：一段多镜 vs 逐镜独立生成（判据＝同一连续世界内的切换 vs 跨越时间/空间/概念）** | `zion-storyboard/references/10-engine-constraints.md` §生成粒度 |
| **色彩的结构功能：含义由作品自己建立（不套色义表）、互补色对只留一对、结构功能一色一义、色彩脚本、服装色彩、前后期分工** | `zion-storyboard/references/36-color-as-structure.md` |
| **梦境与幻觉：四类视觉标签与优先级、识别窗口判据、恐惧/愿望/秘密三选一、抽离四方式与时长、四步节奏、AI 不混装两套美术** | `zion-storyboard/references/35-dream-and-hallucination.md` |
| **场面调度：三段结构、调度还是切镜、摄影机与主体的四种关系（跟/等/迎/让）、走位四变量、调度因果、AI 落地**（另含调度素材的跨档索引） | `zion-storyboard/references/34-staging-and-blocking.md` |
| **声音设计：逐轨录音/生成路径、场景声景、动态听觉前后景、客观/心理声场、J-cut/L-cut、对白语气位与画外声** | `zion-storyboard/references/15-audio-and-lipsync.md` |
| **提示词可执行性：主体锚定与单主体句、指代归属、具象判据、正向优先于否定、示例句来源纪律** | `zion-storyboard/references/12-prompt-hygiene.md` |
| **可选视频模型 MiniMax H3（字段集、时长、素材上限、映射与边界）** | `zion-storyboard/references/16-minimax-h3-adapter.md` |
| **动作强度分档 R1/R2/R3** | `zion-storyboard/references/action-choreography-rules.md` |
| **对白设计与诊断：语言指纹、潜台词、推进力、信息效率、节奏、记忆点** | `zion-script/references/04-dialogue-design.md` |
| **受众期待与情绪回报：情绪经验、期待来源、六类回报及其铺垫、爆点双条件、大小情绪点层次、情绪自嗨** | `zion-script/references/13-audience-and-payoff.md` |
| **分集连载结构：两条曲线、一集四件事、五种结尾切口、集与集三关系、长线三张表、钩子分布与常见问题** | `zion-script/references/14-serial-structure.md` |
| **镜头—场—序列—幕层级与分场结构：边界判据、进入/退出差值、目标—策略—阻力、升级与转向、跨场因果、删并改** | `zion-script/references/15-scene-architecture.md` |
| **类型机制：悬疑公平、喜剧前提与偏差、恐怖规则、关系推进、动作胜负、群像与混合类型** | `zion-script/references/16-genre-mechanics.md` |
| **表情强度三档、起—hold—落时序、遮挡改写与单侧指定** | `zion-script/references/10-physical-acting.md` §八 |
| **张力分布检查（波峰波谷，不用分值模型）／冲突的构造（四要素、去台词检验、升级、立场、空间参与）** | `zion-script/references/03-story-requirements.md` |
| **改动后复验：局部验证／联动检查／全量复核** | `zion-qa/references/qa-change-reverification.md` |
| **非人物/场景资产：生物、载具、武器、图形文字、特效、声音身份的结构与交接** | `zion-assets/references/other-asset-design.md` |
| **外部素材来源、权利状态与允许用途登记**（只追踪证据，不作法律结论） | `zion-assets/references/source-and-rights.md` |
| **后期可救性与合成交接：有效覆盖、余量、clean plate、分层、组接修复边界、替换与降级路径** | `zion-storyboard/references/37-post-and-recovery.md` |
| **无障碍、本地化与最终交付的前期设计** | `zion-storyboard/references/38-accessibility-localization-delivery.md` |
| **按交付物选择的验收矩阵与技术/声音/来源证据检查** | `zion-qa/references/qa-artifact-rubrics.md` |
| **场景地理、竖屏动线、场景状态阶梯 S0–S5、跨观察方向光线对齐、空场政策、环境叙事分层、场景视频可用性预检** | `zion-assets/references/26-scene-consistency.md` |
| Style Sheet（按需视觉维度与精确色板）与 Forbidden List | `zion-script/references/11-character-and-worldbuilding.md` §四 |

### 场景相关的分工边界（2026-09-21 新增）

| 事项 | 归属 |
|---|---|
| 场景地理、动线、场景状态阶梯、叙事物件、视频可用性预检 | `zion-assets`（26 号档） |
| 同一地点**跨观察方向**的板间光线对齐 | `zion-assets`（26 号档） |
| 同场景内**跨镜**光源继承、反向机位、光的演变 | `zion-storyboard`（20 号档） |
| 场景状态的**继承**与切换时点 | `zion-storyboard`（17 号档检查项） |
| 转场的**叙事层级、边界任务、连贯/分隔功能、手段与两端锚点**（镜内揭示／匹配／遮挡／声音桥／溶解） | `zion-storyboard`（22 号档） |
| 转场的**变化量、时长与切点阶段**（30°／动势／读取时长／3:7／跳剪） | `zion-storyboard`（29 号档） |
| **跨生成组**的接缝（末态具体化／换机位硬切／空镜过渡） | `zion-storyboard`（30 号档） |
| 对白**文字**（语言指纹／潜台词／推进力） | `zion-script`（04 号档） |
| 对白**声音层**（语气位／语速档／画外声／电平） | `zion-storyboard`（15 号档） |
| 改动后的**复验方式**（局部→联动→全量三步） | `zion-qa`（qa-change-reverification 档） |

两侧的 S 状态编号必须指向同一状态定义。

已删除且不再恢复：`zion-script/references/05-scene-and-color-bible.md`、`07-prompt-spec.md`（外部会话删除并清理引用；副本存 `.workbuddy/archive/source-deleted-2026-09-20/`）。

## 正文 §x 引用的写法纪律（2026-09-21）

`skill_lint.py` 新增 **SECTION_REF** 项：校验正文里裸写的 `§x` 在本档是否有对应标题。

归属判定规则（写引用时按它写，否则会误报或产生真歧义）：

1. `见本档 §三`、`本文件 §五` → 归属**本档**。
2. `见 [某档](某档.md) §三` → 归属**某档**，由该档校验。
3. **同句先提了别的档名、再说 `见 §x`，会被判为跨档引用**——这正是真歧义所在。要让引用指向本档，就写「**本档** §x」；要指向别档，就在 `§x` 前 60 字符内写出档名。

已知坑：`§三` 这类中文编号最常见的是跨档引用（如 20 号档写“见 [13 号档] §三”），不能一律按本档标题校验。

## 自然语言计数没有工具守护（2026-09-21 发现）

lint 只查 Markdown 链接、标题锚点与 `§x` 引用，**不查「八种／九种」「共 N 档」这类自然语言计数**。已实证一次真 bug：`23-color-and-tone.md` 表头写「色系（八种）」并列出九个，而手册与 SKILL.md 写「九种」；同表「在哪节」列还把色系指向 §二、影调档指向 §三（实际为 §一 与 §四）。

规矩：**列出条目时，标题、表头与检查清单的计数必须同步核对**；改章节编号后，同档内所有指向该节的「在哪节」列一并复查。这类不一致工具抓不到，只能靠人工。

## 版本管理（2026-09-21 建立）

- 版本号与变更记录外置在根目录 **`CHANGELOG.md`**，**不写进技能文件**（SKILL.md 与参考档都不带版本号）。
- **V2 自「四技能定名」起算**（`v2.0.0`，早于 2026-09-20）；V1 不设沿革、不留归档。
- 编号：**主版本＝系统性能力扩展**（一次改动横跨多个技能、成体系吸收外部来源或新增一组判据）与技能结构变化；次版本＝单档新增、单点判据补充、局部吸收；**修订号＝小改动（措辞、错字、计数与节号、单点修复、补用例）**。
- `v3.0.0` 由 manju-laoli 6.9.8 吸收触发主版本跃升，`v3.1`–`v3.14` 为随后的导演／编导知识面补强（新增 12 档、storyboard 回归用例 116→198）；当前版本只在 CHANGELOG 与对话中声明，速览见 CHANGELOG 的「v3 系列速览」。
- 收工后更新 CHANGELOG 已写入 `AGENTS.md` 的维护契约；`AGENTS.md` 坐标表含 CHANGELOG 指针，codex 读 AGENTS.md 即可看到。
- 规模快照随版本记录（各技能参考档数 + 回归用例数），便于对比。

## 外部来源的吸收口径（2026-09-21 拍板）

从外部 skill pack（manju-laoli、Higgsfield 等）学习时，只吸收**判据、结构与流程**，不吸收三类：

1. **数量配额**（“每 15 秒 5~8 次切换”“单集空镜 ≤3 处”“必含肘击”）。family 不设配额；确需保留时改写成“必须能说出它的任务／作用”，用可答性替代计数。
2. **硬禁令与一票否决**（“严禁／必须／一律”）。改写成判据式倾向，并写明例外与边界。
3. **未核验的官方语法主张**（把 `{}`／`<>` 说成官方专用字符、把某条称作“官方红线”、以“已实测”代替来源）。只写“外部资料转述，本工作区未独立核验，投喂前按当前入口复核”。

吸收后必须做三件事，缺一即视为半成品：**接线**（加 SKILL.md 与相关档的入站引用）、**登记单一来源地图**（本文件）、**补回归用例**（判据可复跑）。

高价值可迁移项通常长这样：一个能一句话说清的判据（“麦克风能录到的进语气位，摄像机拍得到的进画面段”／“每个词都能画出来吗”），而不是一串数值。

## Git 与换行符（2026-09-21 建立）

- 工作区是 Git 仓库（`main` 分支，**纯本地无远端**）；**收工最后一步提交**，见 `AGENTS.md` 标准循环第 11 步。提交信息写清技能、改动与版本号。
- `.gitignore` 忽略 `.workbuddy/locks`、`.workbuddy/state`（运行时状态）与 `/codex-skills/`（独立嵌套仓库）。`archive/`、`memory/`、`tools/` 入库。
- **换行符一律 LF**：`.gitattributes` 配 `eol=lf`，`core.autocrlf=false`（不做自动转换）。**Windows 上的写入工具可能默认落 CRLF**——新写或改写文件后要核对；混合换行会让 git 在 checkout 时改写文件，并可能触发 `skill_guard.py check` 的假漂移告警。
- 里程碑：`539f4b7` 基线（v3.14.0，160 文件）；`1c9afa6` 规程加入 Git 步骤与换行符纪律（含 15 个文件的 CRLF→LF 转换）；`411ca60` 收尾记录。
- **shell 里 `git` 不在默认 PATH**：报 `git: command not found` 时先加
  `export PATH="/c/Users/Zhang/.workbuddy/binaries/PortableGit/versions/1.2.0/mingw64/bin:$PATH"`
  注意是 `mingw64/bin`，不是 `bin`（`bin` 下没有 git.exe）。

## 目录约定

- 工作区为唯一源：`zion-script` / `zion-assets` / `zion-storyboard` / `zion-qa` + `Zion技能使用手册.md`。
- 维护工具在 `.workbuddy/tools/`；归档在 `.workbuddy/archive/`。
- 不提交 `__pycache__` 与 `.pyc`。
