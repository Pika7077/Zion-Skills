# 工作空间维护约定

**流程唯一来源**：根目录 `AGENTS.md`（标准循环、硬规则、清理纪律）。本文件只记长期约定与事实。

**内容归属**（风格／色彩／镜头／声音等各归哪一档）在 `.workbuddy/memory/style-single-source.md`；**外部材料的归类与吸收规则**在 `.workbuddy/memory/material-intake.md`。改这两类事改那两份，本文件只留提要。

## 工具三件套（`.workbuddy/tools/`）

- `skill_lint.py` —— 内容校验：JUNK／ORPHAN／DUPLICATE／DANGLING／SECTION_REF／CROSS／`--meta`。
- `skill_guard.py` —— 并发守卫：写租约 `acquire`／`release`／`status`，基线 `snapshot`／`check`。
- `sync_skills.py` —— 安装目录镜像，`--target codex|workbuddy` 只写自己那份。

调用前先读 docstring 确认参数：未匹配的参数会被**静默忽略**，可能退化成无参数全量同步（写两处安装目录）。

## 独立安装口径（2026-09-20）

四个技能都要能单独取用，同时保持家族一起装的体验。

- 跨技能引用只写技能名与档名（“`zion-storyboard` 的光影系统档”），**不写相对路径**——单独安装零断链，由 CROSS 项守护。
  - **CROSS 只扫 `](...)` 形式的链接，纯文本路径不在扫描范围**（2026-10-12 踩到：误写成 `../../zion-script/references/x.md` 没被拦下）。改引用后要人工比对既有写法。
- `parse_input.py` 在 `zion-assets` 与 `zion-storyboard` 各留一份完整副本（登记 DECLARED_DUPES，内容须一致）。
- 不用“薄壳委托”或跨技能相对路径解决——会让单独安装功能缺失。

## 安装与安装后验证（2026-09-23）

安装＝`sync_skills.py --target workbuddy`（镜像规则：缺失补齐、不同覆盖、源已删移除）。装机后五项验证，缺一不算装完：

1. **幂等自检**：紧跟 `--dry`，应 `added=0 updated=0 removed=0`。
2. **逐技能比对**：`diff -r --exclude=__pycache__ <技能> ~/.workbuddy/skills/<技能>`，四个都无输出。
3. **安装目录顶层 ≠ 工作区**：那里还有非本家族的技能与 `_bm_skillid_migration.json`，**不属于本仓库、不要清理**。
4. **在安装副本上重跑两组回归**——工作区绿 ≠ 装机可用。
5. **元数据用 Python 显式 UTF-8 读一次**（解码合法、无 BOM、LF）。**bash 里 `head`／`grep` 看 SKILL.md 中文显示乱码是 Windows 终端 GBK 问题，不是文件损坏**。

## 对外分发

仓库 `https://gitee.com/ZionZhang/zion-skills.git`（**公开**，匿名 clone 可用）。

- **首选：归档 zip** `.../repository/archive/main.zip`（892KB，无需 git／账号，不含 `.git` 与 `_user_meta.json`）。代价：升级要整体覆盖，精确增删仍走 git + `sync_skills.py`。
- **归档地址是 302 跳转，不是直链**：302 响应自身的 `Content-Type` 就是 `text/html`（约 46KB），**不跟随跳转的客户端会把这段 HTML 当下载结果存下来**。下载必须跟跳转（`curl -L`；wget 默认跟随）。**「拿到 HTML」≠「仓库不可见」**——干净环境下实测能下到真 zip（`PK` 魔数）、匿名 `ls-remote` 能读 HEAD。**推断仓库可见性要实测，不能反推**。
- **对方安装**：把 `README.md` 第 3.1 节的提示词原样转发即可（已做成品牌无关）。跨 agent 通用，唯一变量是安装目录：Codex `~/.codex/skills/`、Claude Code `~/.claude/skills/`、Cursor `~/.cursor/skills/`、ZCode `~/.zcode/skills/`、DSH `$DSH_HOME/skills`；不确定时用 `~/.agents/skills/` 兜底（公约目录，但非人人认）。装到 claude／codex 会被其他工具顺带认到。
- **`sync_skills.py` 只支持 `--target codex|workbuddy`**（TARGETS 硬编码）。写指令必须写明只覆盖这两个，其他环境走手工复制。
- **更新＝整目录**，不能只覆盖 `SKILL.md`（`references/` 会增删）；**仓库更新 ≠ 安装目录生效**；装完／更新后**重启客户端**。
- **镜像会顺带清掉旧 `_user_meta.json`**（本机状态文件，已 `git rm --cached` + `.gitignore`），由客户端重新生成，属预期。
- **报版本用 commit SHA**，不用 `vX.Y.Z`（技能目录不写版本号，commit 是唯一锚点）。
- 新增仓库级文件先自问：**这是内容还是本机状态**？状态类（安装时间戳、锁、缓存、路径）一律忽略。

## 并发写入

已发生两起事故（2026-09-20）：`12-visual-style-and-grading.md` 被另一会话整篇替换；`05-scene-and-color-bible.md`、`07-prompt-spec.md` 被删除（旧副本在 `.workbuddy/archive/source-deleted-2026-09-20/`，用户决定不恢复）。

应对：写租约 + 基线快照。收工前必跑 `skill_guard.py check`；自己没改过的文件出现在漂移列表里先对齐；删除类改动先归档；源文件被对方删除时从安装目录抢救。

**两会话同名（都写 `workbuddy`）时**：`--owner` 无法区分谁持有——遇到「自己没领却显示被占」**不要 `--force`**，先看当日日志与 `git status`；各自计版本号会撞号，后写的一方让号并在 CHANGELOG 独立成节；**对方的当日日志会记下你的动作，是核对并发的主要线索**。

## 正文 §x 引用（2026-09-21）

SECTION_REF 校验正文里裸写的 `§x` 在本档是否有对应标题。

- `见本档 §三`／`本文件 §五` → 归属本档。
- `见 [某档](某档.md) §三` → 归属某档。
- **同句先提了别的档名、再说 `见 §x` 会被判跨档引用**——真歧义所在。要指本档写「**本档** §x」；要指别档，让**档名落在 `§` 前 60 字符内**。

三条硬经验：① 写「同档 §九」「该档 §十二」这类指代**不通过**（窗口里既无档名也无「本档」）；② **给一档加节／改编号后，必须全库搜指向该档的 `§x` 并同步改**（搜法：`档名.md)` 后跟 `§`）；③ `tests/` 里的链接要写 `../references/xxx.md`。
另：SECTION_REF **只校验编号是否存在**，指错章节抓不到（只能人工比对）。

## 自然语言计数没有工具守护（2026-09-21）

lint 不查「八种／九种」「共 N 档」这类计数。已实证真 bug：`23-color-and-tone.md` 表头写「色系（八种）」却列九个，「在哪节」列也指错。

规矩：标题、表头与检查清单的计数必须同步核对；改章节编号后同档「在哪节」列一并复查。工具抓不到，只能人工。

## 全文件审验清单（2026-09-22；用户说“审验全文件／同步版本号”时跑）

七步缺一不可：

1. `skill_lint.py --meta`（七项全空）+ 两组自动回归。
2. **实测规模对照 CHANGELOG 规模表**：各技能 `references/*.md` 档数，与各 `tests/manual-regression.md` 的**最大编号与连续性**。
3. **技能文件内不该有版本号**：grep `v[0-9]\.[0-9]` 全库技能目录。
4. **SKILL.md 直链覆盖率**：逐技能算链接集合 vs 实际档集合。
5. **单一来源地图未登记项分类核对**（内容档必须登记；契约／格式／检查表／工具档不登记，清单在该档末尾）。
6. **自然语言计数交叉核对** + **记录里的能力声明是否真的存在**（曾发现 CHANGELOG 声称的 `quick_validate.py` 从未存在）。
7. **CHANGELOG 分两个区块**：上卷 `## vX.Y.Z`，**现行最新条目在 `## 变更记录` 区用 `### vX.Y.Z`**。查“哪些版本没记”要 `grep -nE '^#{2,3} '` 提取两区标题再比——2026-10-10 曾因只 grep `^## v` 误判 v5.6.1–v5.8.0 缺失。

## 版本管理（2026-09-21）

- 版本号与变更记录外置在 `CHANGELOG.md`，**不写进技能文件**；**V2 自「四技能定名」起算**（`v2.0.0`）。
- 三个数字：**第一位＝结构性大更新**（拆分／合并／职责重划、成体系吸收外部来源）；**第二位＝新增参考档（补档不跳主版本）或同时好几个小改动**（本工作区最常见形态）；**第三位＝小改动**（措辞、错字、计数与节号、单条判据、规模表）。顺序：先看结构调整／成体系吸收 → 再看新档或多个小改同时 → 其余动第三位。
- 规模快照随版本记录，收工后更新（已写入 `AGENTS.md` 维护契约）。

## 外部来源的吸收口径

完整规则见 `.workbuddy/memory/material-intake.md`。提要：只吸收**判据、结构与流程**；数量配额、硬禁令与未核验的语法主张**不吸收**（配额改写成可答性判据）。吸收后必做三件事：**接线、登记单一来源地图、补回归用例**。

三条最易忘的：① **先 grep 材料的结构词，再读知识点**——真缺口通常在材料独有的形态上，逐条比知识点会得出“全都有”的假结论；② **防回退**——材料可能带本库已废止的旧口径，要对照 `CHANGELOG.md` 历史条目（实证：声音材料主张“对白混音音量最大”，正是 `v4.2.0` 已改掉的）；③ **追加回归前先取全文件最大编号**。

## Git 与换行符

- 工作区是 Git 仓库（`main`）；**收工最后一步提交**（标准循环第 11 步），提交信息写清技能、改动与版本号。
- 远端 Gitee `origin`（HTTPS）。推送需 `env -u https_proxy -u http_proxy -u HTTPS_PROXY -u HTTP_PROXY`（沙箱代理会中断传输）+ `GIT_CONFIG_NOSYSTEM=1` + `GIT_TERMINAL_PROMPT=0`；用户名填 **Gitee 用户名**，密码用私人令牌；仓库级 `http.version HTTP/1.1`。
- **`GIT_CONFIG_NOSYSTEM=1` 是必需的**（2026-09-22）：系统级 `etc/gitconfig` 设了 `credential.helper=helper-selector`，认证前要跑约 40 秒内部 `git config` 查询，常在传输前被超时杀掉，表现为 **push 无输出挂死**。
- **凭据助手路径随 PortableGit 版本走**（2026-10-12 实测）：全局 `~/.gitconfig` 的 `credential.helper` 是**绝对路径**，PortableGit 由 1.2.0 升到 1.3.0 后旧路径失效，push 报 `could not read Username`。修法：`git config --global credential.helper '!<...>/versions/1.3.0/mingw64/bin/git-credential-manager.exe'`；临时可用 `-c credential.helper= -c credential.helper='!<新路径>'` 覆盖。**每次 PortableGit 升级后要复查这条**（版本号见 `.../versions/current`）。
- **1.3.0 起 `git` 与 coreutils 已在默认 PATH**（`/mingw64/bin`、`/usr/bin`），不再需要手动 export。若报 command not found，按 `versions/current` 拼路径：`git` 在 `mingw64/bin`，`ls`／`tail`／`diff`／`wc` 在 **`usr/bin`**（两处都要加）。
- **推送后确认用本地命令**（`git status -sb`／`git log --oneline`），不要 `git ls-remote`。`branch -vv` 报 `origin/main: gone` 只是本地引用过期。
- **两会话交替推送时「本地落后」是常态**：先 `git fetch` + `rev-parse` 比对；快进前确认三项——是否直接父提交（能否 `--ff-only`）、工作区是否干净、租约是否空闲。
- **换行符一律 LF**（`.gitattributes` `eol=lf`、`core.autocrlf=false`）；混合换行会触发假漂移告警。
- `.gitignore` 忽略 `.workbuddy/locks`、`.workbuddy/state` 与嵌套仓库 `/codex-skills/`。

## 目录约定

工作区为唯一源：`zion-script` / `zion-assets` / `zion-storyboard` / `zion-qa` + `Zion技能使用手册.md`。工具在 `.workbuddy/tools/`，归档在 `.workbuddy/archive/`，记忆在 `.workbuddy/memory/`。不提交 `__pycache__` 与 `.pyc`。

## 本项目分镜交付规格（2026-10-10）

**项目取向，不是通用规则**：只对本项目生效，不覆盖技能判据，随时可撤。

- **时长两层**：**单段 ≤30 秒**（单次生成上限）；**一集 55–70 秒**。用户原话：“30s 以内是**段落**；一集 1 分钟或 20 分钟短片，你要**自行分配每个段落**”。
- **交付稿不出现逐镜秒数**，只给每段与整集总时长；逐镜时间仍写在 JSON `time_range`（结构校验需要）。工具已支持：`export_output.py --no-shot-time`。
- **允许在守住剧情逻辑的前提下增写台词**：口语化、有情感；不得改原意、不得造成逻辑混乱。
- 另两条**技能本就要求**，不另记：表情写到肌肉／眼神层；每镜给画外音／环境音提示词；人物音色按 `voice_profiles`。
