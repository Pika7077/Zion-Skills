# 工作空间维护约定

**流程唯一来源**：根目录 `AGENTS.md`（标准循环、硬规则、清理纪律）。本文件只记长期约定与事实。

**单一来源地图**：内容归属（风格／色彩／镜头／声音／后期各归哪一档）在 **`.workbuddy/memory/style-single-source.md`**。改动风格与色彩归属时改那份，本文件不复制。

工具三件套（`.workbuddy/tools/`）：

- `skill_lint.py` —— 内容校验：JUNK／ORPHAN／DUPLICATE／DANGLING／SECTION_REF／CROSS／`--meta`。
- `skill_guard.py` —— 并发守卫：写租约 `acquire`／`release`／`status`，基线 `snapshot`／`check`。
- `sync_skills.py` —— 安装目录镜像，`--target codex|workbuddy` 只写自己那份。

## 独立安装口径（2026-09-20 拍板）

四个技能都必须能单独取用，同时保持家族一起装的体验。

- 跨技能引用只写技能名与档名（“`zion-storyboard` 的光影系统档”），**不写相对路径**，单独安装时零断链。由 CROSS 项守护（计入问题，退出码 1）。
- `parse_input.py` 在 `zion-assets` 与 `zion-storyboard` 各存一份完整副本（已登记 DECLARED_DUPES，内容须一致），供各自单独安装。
- 不用“薄壳委托”或跨技能相对路径解决此类问题——会让单独安装功能缺失。

## 并发写入：已发生的两起事故（2026-09-20）

- `zion-script/references/12-visual-style-and-grading.md` 被另一会话整篇替换（170 行词库版 → 35 行“剧本阶段锁定视觉事实”版），我的改动被覆盖。
- `05-scene-and-color-bible.md`、`07-prompt-spec.md` 被删除并清理引用；旧副本已抢救到 `.workbuddy/archive/source-deleted-2026-09-20/`（用户决定不再恢复）。

应对：写租约 + 基线快照。工作习惯：收工前必跑 `skill_guard.py check`，自己没改过的文件出现在漂移列表里先对齐再继续；删除类改动先归档；源文件被对方删除时从安装目录抢救副本。

## 正文 §x 引用的写法纪律（2026-09-21）

`skill_lint.py` 的 **SECTION_REF** 项校验正文里裸写的 `§x` 在本档是否有对应标题。归属判定：

1. `见本档 §三`、`本文件 §五` → 归属**本档**。
2. `见 [某档](某档.md) §三` → 归属**某档**，由该档校验。
3. **同句先提了别的档名、再说 `见 §x`，会被判为跨档引用**——真歧义所在。要指向本档就写「**本档** §x」；要指向别档，就在 `§x` 前 60 字符内写出档名。

已知坑：`§三` 这类中文编号最常见的是跨档引用（如 20 号档写“见 [13 号档] §三”），不能一律按本档标题校验。

## 自然语言计数没有工具守护（2026-09-21 发现）

lint 只查 Markdown 链接、标题锚点与 `§x` 引用，**不查「八种／九种」「共 N 档」这类计数**。已实证真 bug：`23-color-and-tone.md` 表头写「色系（八种）」却列出九个，同表「在哪节」列还把色系指向 §二、影调档指向 §三（实为 §一／§四）。

规矩：列出条目时，标题、表头与检查清单的计数必须同步核对；改章节编号后，同档内「在哪节」列一并复查。工具抓不到，只能人工。**CHANGELOG 的「当前规模」表同类**——每次版本跃升后按实测更新。

## 版本管理（2026-09-21 建立）

- 版本号与变更记录外置在根目录 **`CHANGELOG.md`**（含当前版本、规模快照、沿革），**不写进技能文件**（SKILL.md 与参考档都不带版本号）。
- **V2 自「四技能定名」起算**（`v2.0.0`）；V1 不设沿革、不留归档。
- 编号（2026-09-22 按用户要求改写，总三个数字）：**第一位＝文件大更新**（新增参考档、拆分／合并／职责重划、成体系吸收外部来源）；**第二位＝同时好几个小改动**（一次改动里扩档＋接线＋补回归＋跨档修正一起做，本工作区最常见形态）；**第三位＝小更新**（只改一处：措辞、错字、计数与节号、单条判据、规模表）。判断顺序：先看有无新增档／结构调整 → 再看是否多个小改动同时 → 其余动第三位。
- 规模快照随版本记录（各技能参考档数 + 回归用例数）；收工后更新 CHANGELOG 已写入 `AGENTS.md` 维护契约。

## 外部来源的吸收口径（2026-09-21 拍板）

从外部 skill pack（manju-laoli、Higgsfield 等）学习时，只吸收**判据、结构与流程**，不吸收三类：

1. **数量配额**（“每 15 秒 5~8 次切换”“单集空镜 ≤3 处”“必含肘击”）。改写成“必须能说出它的任务／作用”，用可答性替代计数。
2. **硬禁令与一票否决**（“严禁／必须／一律”）。改写成判据式倾向，并写明例外与边界。
3. **未核验的官方语法主张**。只写“外部资料转述，本工作区未独立核验，投喂前按当前入口复核”。

吸收后必须做三件事，缺一即视为半成品：**接线**（SKILL.md 与相关档的入站引用）、**登记单一来源地图**（style-single-source 档）、**补回归用例**。

高价值可迁移项通常长这样：一个能一句话说清的判据（“麦克风能录到的进语气位，摄像机拍得到的进画面段”／“每个词都能画出来吗”），而不是一串数值。

## Git 与换行符（2026-09-21 建立）

- 工作区是 Git 仓库（`main` 分支）；**收工最后一步提交**（`AGENTS.md` 标准循环第 11 步），提交信息写清技能、改动与版本号。
- 远端 Gitee `origin`（HTTPS）。推送需 `env -u https_proxy -u http_proxy -u HTTPS_PROXY -u HTTP_PROXY`（沙箱注入的代理会中断传输），仓库级 `http.version HTTP/1.1`；用户名填 **Gitee 用户名**而非邮箱，密码用私人令牌。
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
