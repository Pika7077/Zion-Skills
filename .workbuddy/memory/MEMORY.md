# 工作空间维护约定

**流程唯一来源**：根目录 `AGENTS.md`（标准循环、硬规则、清理纪律）。本文件只记长期约定与事实。

**单一来源地图**：内容归属（风格／色彩／镜头／声音／后期各归哪一档）在 **`.workbuddy/memory/style-single-source.md`**。改动风格与色彩归属时改那份，本文件不复制。

**学习资料的归类法**：外部材料怎么判归属、怎么判该不该吸收，在 **`.workbuddy/memory/material-intake.md`**。用户发学习资料时按它归类，本文件只留提要。

工具三件套（`.workbuddy/tools/`）：

- `skill_lint.py` —— 内容校验：JUNK／ORPHAN／DUPLICATE／DANGLING／SECTION_REF／CROSS／`--meta`。
- `skill_guard.py` —— 并发守卫：写租约 `acquire`／`release`／`status`，基线 `snapshot`／`check`。
- `sync_skills.py` —— 安装目录镜像，`--target codex|workbuddy` 只写自己那份。

调用这三个工具前先读 docstring 确认参数：`sync_skills.py` 曾不识别 `--help`（2026-09-22 已修）——未匹配的参数会被静默忽略，使调用退化成**无参数全量同步（写两处安装目录）**。

## 独立安装口径（2026-09-20 拍板）

四个技能都必须能单独取用，同时保持家族一起装的体验。

- 跨技能引用只写技能名与档名（“`zion-storyboard` 的光影系统档”），**不写相对路径**，单独安装时零断链。由 CROSS 项守护（计入问题，退出码 1）。
- `parse_input.py` 在 `zion-assets` 与 `zion-storyboard` 各存一份完整副本（已登记 DECLARED_DUPES，内容须一致），供各自单独安装。
- 不用“薄壳委托”或跨技能相对路径解决此类问题——会让单独安装功能缺失。

## 安装与安装后验证（2026-09-23 建立）

安装＝`python .workbuddy/tools/sync_skills.py --target workbuddy`（镜像规则：缺失补齐、内容不同则覆盖、源已删的一并移除）。装机后按五项验证，缺一项不算装完：

1. **幂等自检**：紧跟一次 `--dry`，应显示 `added=0 updated=0 removed=0`。
2. **逐技能内容比对**：`diff -r --exclude=__pycache__ <技能> ~/.workbuddy/skills/<技能>`，四个技能都无输出。
3. **安装目录顶层 ≠ 工作区**：那里还有非本家族的技能（`skill-audit`、`init-project-workspace`、`reclaim-code-entropy`）与 `_bm_skillid_migration.json`，**不属于本仓库，不要清理**；`sync_skills.py` 也只处理 `SKILLS` 里的四个目录。
4. **在安装副本上重跑两组回归**（`python -B zion-assets/tests/test_extract_characters.py`、`python -B zion-storyboard/tests/test_storyboard_audit.py`）——工作区绿不等于装机可用，路径与打包差异要在这里暴露。
5. **元数据用 Python 显式 UTF-8 读一次**，确认解码合法、无 BOM、LF。**bash 里 `head`／`grep` 看 SKILL.md 中文会显示乱码，那是 Windows 终端 GBK 显示问题，不是文件损坏**——别据此判定装机失败。

## 对外分发：分享给他人（2026-10-08 建立）

仓库 `https://gitee.com/ZionZhang/zion-skills.git`（**公开**，匿名 `git clone` 实测可用，无需凭据——2026-10-08 实测更正了前一版「私有需加成员」的错误推断）。

- **首选安装方式：归档 zip**（2026-10-08 实测选定）。地址 `https://gitee.com/ZionZhang/zion-skills/repository/archive/main.zip`，**892KB**、HTTP 200、无需 git、无需账号；解压后顶层即四个技能，**不含 `.git` 与 `_user_meta.json`**。对比：浅克隆 3.0M（`.git` 占 808K，四个技能仅 1.1M）。
  - 选它的理由：体积省约 70%；**不依赖对方装 git**（很多 agent 环境能下载但没有 git）；包更干净。
  - 它的代价：升级时要**整体覆盖**，无法精确处理「源已删的文件」——需要精确增删时仍走 git + `sync_skills.py`。
  - **三种方式装出的目录内容完全一致**：script 17／assets 19／storyboard 39／qa 7 文件。
- **把提示词直接发给对方的 agent**，让它自己装。模板在 `README.md` 第 3.1 节，可原样转发。
- **手工安装**＝解压或克隆后把技能目录整体复制到安装目录（`~/.workbuddy/skills/` 或 `~/.codex/skills/`）。可四个一起装，也可只装一个（单独安装是受支持用法）。
- **`sync_skills.py` 只支持 `--target codex|workbuddy`**（`TARGETS` 字典硬编码这两个）。写成 `--target <环境>` 这种泛化说法会让 Claude Code 用户报「未知目标」——**写指令时必须写明只覆盖这两个**，其他环境走手工复制。
- **更新＝不要只覆盖 `SKILL.md`**。技能是一整个目录，`references/` 会增删。**仓库更新 ≠ 安装目录生效**，必须重新拷贝或跑同步。
- **装完／更新后必须重启客户端**（WorkBuddy / Codex），否则新技能不进选择器。
- **镜像规则会顺带清掉旧元数据**：工作区已无 `_user_meta.json`，所以对方安装时该文件会被一并移除（`--dry` 会显示在 `removed` 里），由客户端重新生成——这是预期行为。

### `_user_meta.json` 不随仓库分发（2026-10-08 修正）

它是**客户端在本机安装时生成**的元数据：`{name, installedAt, source}`（`installedAt` 为时间戳，`source=userImport`），随机器而异。此前被纳入版本控制（四技能各 1 + 归档副本 4 = 8 份），已 `git rm --cached` 移除并加入 `.gitignore`（规则 `_user_meta.json` 与 `zion-*/_user_meta.json`），**本地文件保留**。对方克隆后由客户端自行生成自己的那份。

新增仓库级文件时先自问：**这是内容还是本机状态**？状态类（安装时间戳、锁、缓存、路径）一律忽略，不进分发包。

## 并发写入：已发生的两起事故（2026-09-20）

- `zion-script/references/12-visual-style-and-grading.md` 被另一会话整篇替换（170 行词库版 → 35 行“剧本阶段锁定视觉事实”版），我的改动被覆盖。
- `05-scene-and-color-bible.md`、`07-prompt-spec.md` 被删除并清理引用；旧副本已抢救到 `.workbuddy/archive/source-deleted-2026-09-20/`（用户决定不再恢复）。

应对：写租约 + 基线快照。工作习惯：收工前必跑 `skill_guard.py check`，自己没改过的文件出现在漂移列表里先对齐再继续；删除类改动先归档；源文件被对方删除时从安装目录抢救副本。

**两个会话同名（都写 `workbuddy`）时的三点（2026-09-22 实证）**：

- 租约的 `--owner` 两边同名，**无法区分谁持有**；遇到「自己没领却显示被占」不要 `--force`，先看当日日志与 `git status`。
- 各自计版本号会**撞号**（同日都从 `v4.24.0` 起算）。后写的一方让号，并在 CHANGELOG 独立成节，不覆盖对方条目。
- 对方的当日日志会记下你的动作（v4.25.0 那轮，codex 的日志记了我的租约与改动）——**当日日志是核对并发的主要线索**。

## 正文 §x 引用的写法纪律（2026-09-21）

`skill_lint.py` 的 **SECTION_REF** 项校验正文里裸写的 `§x` 在本档是否有对应标题。归属判定：

1. `见本档 §三`、`本文件 §五` → 归属**本档**。
2. `见 [某档](某档.md) §三` → 归属**某档**，由该档校验。
3. **同句先提了别的档名、再说 `见 §x`，会被判为跨档引用**——真歧义所在。要指向本档就写「**本档** §x」；要指向别档，就在 `§x` 前 60 字符内写出档名。

已知坑：`§三` 这类中文编号最常见的是跨档引用（如 20 号档写“见 [13 号档] §三”），不能一律按本档标题校验。

配套三条硬经验（2026-09-22 反复踩到，写引用前先看）：

1. **SKILL.md 里写 `§x` 必须让 `档名.md` 落在 `§` 前 60 字符内**（或写「本档」）。写「同档 §九」「该档 §十二」这类指代**不通过**——窗口里既没有档名也没有「本档」，会被按本档标题校验。正确写法：`见 [蒙太奇段落](references/32-montage-sequences.md) §九`。
2. **给一档加节／改编号后，必须全库搜指向该档的 `§x` 引用并同步改**。A 档插入一节会把 B 档原本指向 §三 的引用变成错的（本轮已发生两次：visual-storytelling、27 号档）。搜法：`档名.md)` 后跟 `§`。
3. **`tests/` 目录里的链接要写 `../references/xxx.md`**，直接写档名会被 DANGLING 判为文件缺失。

另外，SECTION_REF **只校验编号是否存在**，编号指错章节（§五与§四都存在时）抓不到——这类只能人工比对。

## 自然语言计数没有工具守护（2026-09-21 发现）

lint 只查 Markdown 链接、标题锚点与 `§x` 引用，**不查「八种／九种」「共 N 档」这类计数**。已实证真 bug：`23-color-and-tone.md` 表头写「色系（八种）」却列出九个，同表「在哪节」列还把色系指向 §二、影调档指向 §三（实为 §一／§四）。

规矩：列出条目时，标题、表头与检查清单的计数必须同步核对；改章节编号后，同档内「在哪节」列一并复查。工具抓不到，只能人工。**CHANGELOG 的「当前规模」表同类**——每次版本跃升后按实测更新。

## 全文件审验清单（2026-09-22 建立）

用户说"审验全文件／同步版本号"时按此跑，六步缺一不可：

1. `skill_lint.py --meta`（七项全空）+ 两组自动回归（assets 5 / storyboard 26）。
2. **实测规模对照 CHANGELOG 规模表**：各技能 `references/*.md` 档数、`tests/manual-regression.md` 的**最大编号与连续性**。
3. **技能文件内不该有版本号**：grep `v[0-9]\.[0-9]` 全库技能目录，命中即问题。
4. **SKILL.md 直链覆盖率**：逐技能算 `(references/xxx.md)` 链接集合 vs 实际档集合，未直链的档是发现性问题。
5. **单一来源地图未登记项分类核对**：内容档必须登记；契约／输出格式／检查表／工具档不登记（清单写在 `style-single-source.md` 末尾）。
6. **手册与来源档的自然语言计数交叉核对**（如「色系（九种）」「七色调」两边必须一致），以及**记录里的能力声明是否真的存在**（曾发现 CHANGELOG 声称的 `quick_validate.py` 从未存在）。

## 版本管理（2026-09-21 建立）

- 版本号与变更记录外置在根目录 **`CHANGELOG.md`**（含当前版本、规模快照、沿革），**不写进技能文件**（SKILL.md 与参考档都不带版本号）。
- **V2 自「四技能定名」起算**（`v2.0.0`）；V1 不设沿革、不留归档。
- 编号（2026-09-22 用户两次拍板，总三个数字）：**第一位＝结构性大更新**（拆分／合并／职责重划、成体系吸收外部来源）；**第二位＝新增参考档**（**补档不跳主版本**）**或同时好几个小改动**（一次改动里扩档＋接线＋补回归＋跨档修正一起做，本工作区最常见形态）；**第三位＝小更新**（只改一处：措辞、错字、计数与节号、单条判据、规模表）。判断顺序：先看有无结构调整／成体系吸收 → 再看是否新增参考档或多个小改动同时 → 其余动第三位。
- 规模快照随版本记录（各技能参考档数 + 回归用例数）；收工后更新 CHANGELOG 已写入 `AGENTS.md` 维护契约。

## 外部来源的吸收口径

**完整规则见 `.workbuddy/memory/material-intake.md`**（学习资料归类与吸收）——材料形态判定、四类内容的归属落点、四项判定（已覆盖／真增量／张力点／不吸收）、防回退三步、落地三件事、附加检查。本文件只留提要。

从外部材料学习时，只吸收**判据、结构与流程**；数量配额、硬禁令与未核验的语法主张三类**不吸收**（配额改写成可答性判据）。吸收后必做三件事：**接线**、**登记单一来源地图**、**补回归用例**。

高价值可迁移项通常长这样：一个能一句话说清的判据（“麦克风能录到的进语气位，摄像机拍得到的进画面段”／“每个词都能画出来吗”），而不是一串数值。

三条最易忘的（细节查 material-intake）：

- **先 grep 材料的结构词，再读知识点**——真缺口通常在材料独有的形态或组织方式上；逐条比知识点会得出“全都有”的错误结论。
- **防回退**：材料可能带着本库已废止的旧口径，要对照 `CHANGELOG.md` 的历史条目，不能只比现档正文。实证：声音三层材料主张“对白混音音量最大”，正是 `v4.2.0` 已改掉的口径。
- **追加回归前先取全文件最大编号**（2026-09-22 撞号实录）；**「当前规模」表每次版本跃升必更新**。

## Git 与换行符（2026-09-21 建立）

- 工作区是 Git 仓库（`main` 分支）；**收工最后一步提交**（`AGENTS.md` 标准循环第 11 步），提交信息写清技能、改动与版本号。
- 远端 Gitee `origin`（HTTPS）。推送需 `env -u https_proxy -u http_proxy -u HTTPS_PROXY -u HTTP_PROXY`（沙箱注入的代理会中断传输），仓库级 `http.version HTTP/1.1`；用户名填 **Gitee 用户名**而非邮箱，密码用私人令牌。非交互环境加 `GIT_TERMINAL_PROMPT=0` 防挂起。
- **推送必须加 `GIT_CONFIG_NOSYSTEM=1`**（2026-09-22 实测；写这条前连着失败三次）。PortableGit 的**系统级** `etc/gitconfig` 设了 `credential.helper=helper-selector`，它每次认证要跑约 **40 秒**——内部连做 `git config helperselector.selected`、`--show-origin credential.helper`、`--system -e` 数次查询，中间约 36 秒无动作，常在真正传输前就被超时杀掉，表现为 **push 无输出挂死**（`git push -v` 停在 `Pushing to ...`）。加 `GIT_CONFIG_NOSYSTEM=1` 忽略系统配置后直接走 global 的 GCM，秒成。**这也是本机反复出现 credential helper 活动的原因**（`GIT_TRACE=1` 可直接看到那一串 `git config` 调用）。
- **推送后的确认用本地命令**（`git status -sb` / `git log --oneline`），不要用 `git ls-remote`——后者是多余的网络往返（仓库虽为公开，但本地命令已足够）。push 自身的输出已含 `旧..新 branch -> branch`，足够判断结果。
- `git branch -vv` 报 `origin/main: gone` **只是本地 remote-tracking 引用过期**，不代表远端被删。
- **换行符一律 LF**：`.gitattributes` 配 `eol=lf`，`core.autocrlf=false`。Windows 写入工具可能默认落 CRLF——新写或改写文件后要核对；混合换行会触发 `skill_guard.py check` 的假漂移告警。
- `.gitignore` 忽略 `.workbuddy/locks`、`.workbuddy/state` 与嵌套仓库 `/codex-skills/`。
- **shell 里 `git` 与 coreutils 都不在默认 PATH**（shim 的 `shell-runtime-bash-env.sh` 在 `dirname` 处失败）。每个 Bash 调用需自带：

  ```bash
  export PATH="/c/Users/Zhang/.workbuddy/binaries/PortableGit/versions/1.2.0/mingw64/bin:/c/Users/Zhang/.workbuddy/binaries/PortableGit/versions/1.2.0/usr/bin:$PATH"
  ```

  `git` 在 `mingw64/bin`；`ls`／`tail`／`head`／`diff`／`wc` 在 **`usr/bin`**——两处都要加，只加前者会使 coreutils 报 command not found。

## 目录约定

- 工作区为唯一源：`zion-script` / `zion-assets` / `zion-storyboard` / `zion-qa` + `Zion技能使用手册.md`。
- 维护工具在 `.workbuddy/tools/`；归档在 `.workbuddy/archive/`；记忆在 `.workbuddy/memory/`。不提交 `__pycache__` 与 `.pyc`。
