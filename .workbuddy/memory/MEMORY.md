# 工作空间维护约定

**流程唯一来源**：根目录 `AGENTS.md`（标准循环、硬规则、清理纪律）。本文件只记长期约定与事实。

**内容归属**（风格／色彩／镜头／声音等各归哪一档）在 `.workbuddy/memory/style-single-source.md`；**外部材料的归类与吸收规则**在 `.workbuddy/memory/material-intake.md`。改这两类事改那两份，本文件只留提要。

## 工具的已知限制

工具职责与操作流程见根目录 `AGENTS.md`。`sync_skills.py` 严格校验参数；源目录、技能入口、文件可读性或技能内本地引用检查失败时停止整次同步。目标目录不存在时仍会跳过，不能据退出成功声称首次安装已完成。

## 独立安装口径（2026-09-20）

四个技能都要能单独取用，同时保持家族一起装的体验。

- 跨技能引用只写技能名与档名（“`zion-storyboard` 的光影系统档”），**不写相对路径**——单独安装零断链，由 CROSS 项守护。
  - **CROSS 只扫 `](...)` 形式的链接，纯文本路径不在扫描范围**（2026-10-12 踩到：误写成 `../../zion-script/references/x.md` 没被拦下）。改引用后要人工比对既有写法。
- `parse_input.py` 在 `zion-assets` 与 `zion-storyboard` 各留一份完整副本（登记 DECLARED_DUPES，内容须一致）。
- 不用“薄壳委托”或跨技能相对路径解决——会让单独安装功能缺失。

## 安装与分发

统一见根目录 `README.md` 第三节；本档不重复命令、目标目录或验证清单。

## 并发写入

已发生两起事故（2026-09-20）：`12-visual-style-and-grading.md` 被另一会话整篇替换；`05-scene-and-color-bible.md`、`07-prompt-spec.md` 被删除（旧副本在 `.workbuddy/archive/source-deleted-2026-09-20/`，用户决定不恢复）。

应对：写租约 + 基线快照。操作要求见 `AGENTS.md`；源文件被另一会话删除时，可从安装副本抢救后再核对。

**两个会话使用同一工具名时**：以各自的 `session_id` 区分，不能凭 `owner` 相同认领或释放租约。旧版无会话 ID 的租约迁移要求见 `AGENTS.md`。各自计版本号仍可能撞号，后写的一方让号并在 CHANGELOG 独立成节；当日日志可辅助核对并发。

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
7. **查版本历史先读归档索引**：当前变化在根目录 `CHANGELOG.md`；旧记录已归档，原快照曾混用二级和三级版本标题，检索需同时覆盖两种，不能只搜 `^## v`。

## 版本管理

版本规则与规模快照统一见根目录 `CHANGELOG.md`；技能正文不写版本号。

## 外部来源的吸收口径

完整规则见 `.workbuddy/memory/material-intake.md`。提要：只吸收**判据、结构与流程**；数量配额、硬禁令与未核验的语法主张**不吸收**（配额改写成可答性判据）。吸收后必做三件事：**接线、登记单一来源地图、补回归用例**。

三条最易忘的：① **先 grep 材料的结构词，再读知识点**——真缺口通常在材料独有的形态上，逐条比知识点会得出“全都有”的假结论；② **防回退**——材料可能带本库已废止的旧口径，要对照 `CHANGELOG.md` 历史条目（实证：声音材料主张“对白混音音量最大”，正是 `v4.2.0` 已改掉的）；③ **追加回归前先取全文件最大编号**。

## Git 与换行符

- 原维护工作区使用 `main`；提交与推送条件统一见根目录 `AGENTS.md`，本档不另设收工提交要求。
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
