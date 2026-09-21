# 协作规程（codex + WorkBuddy 共用）

本工作区由 codex 与 WorkBuddy 两个会话同时维护同一套技能。以下是**唯一流程来源**，两边都按它执行。

一句话：**同一个技能同时只让一个会话写；动手前领租约、拍基线，收工前校验、同步、还租约。**

## 坐标

| 项 | 位置 |
|---|---|
| 技能源（唯一真相） | `zion-assets` / `zion-qa` / `zion-script` / `zion-storyboard` |
| 维护工具 | `.workbuddy/tools/`：`skill_lint.py`、`skill_guard.py`、`sync_skills.py` |
| 归档 | `.workbuddy/archive/` |
| 手册 | `Zion技能使用手册.md` |
| 版本与变更记录 | `CHANGELOG.md` |
| Git 仓库 | 工作区根目录，`main` 分支，纯本地无远端；`.workbuddy/locks`、`.workbuddy/state` 与嵌套仓库 `codex-skills/` 不入库 |
| 长期约定与单一来源地图 | `.workbuddy/memory/MEMORY.md` |

## Git 跟踪边界

- 根目录 Git 仓库跟踪四个技能源、根级文档、`.workbuddy/tools/`、`.workbuddy/memory/` 与 `.workbuddy/archive/`。
- `codex-skills/` 是独立的嵌套仓库，由父仓库忽略，不登记成 submodule，也不混入本仓库提交。
- `.workbuddy/state/`、`.workbuddy/locks/`、Python 缓存、本地虚拟环境、密钥与临时文件不提交；具体规则见根目录 `.gitignore`。
- 提交前执行本文件的收工校验；未经用户明确要求，不代为创建提交、推送或改写远端历史。

## 标准循环

```text
1  python .workbuddy/tools/skill_guard.py status
2  python .workbuddy/tools/skill_guard.py acquire <skill> --owner <codex|workbuddy> --intent "<要做什么>"
3  python .workbuddy/tools/skill_guard.py snapshot --by <会话名>
4  …改文件…
5  python .workbuddy/tools/skill_lint.py                      # 必须 0 问题
6  python -B zion-assets/tests/test_extract_characters.py
   python -B zion-storyboard/tests/test_storyboard_audit.py    # 必须全绿
7  python .workbuddy/tools/skill_guard.py check                # 看这段时间有没有别人也在写
8  python .workbuddy/tools/sync_skills.py --target <codex|workbuddy>
9  更新 CHANGELOG.md 的版本号与条目
10 python .workbuddy/tools/skill_guard.py release <skill> --owner <会话名>
11 git add -A && git commit -m "<技能>: <改了什么>（vX.Y.Z）"
```

对照各技能 `tests/manual-regression.md` 人工复核，是同一步收工动作的一部分。

第 11 步的提交是收工的最后一环：**一次逻辑改动一次提交**，提交信息写清技能、改动与版本号（版本号见 `CHANGELOG.md`）。

## 硬规则

- **不写别人持有租约的技能**。确实需要抢占就 `--force`，并在当日日志记一笔。
- 建议分工（非强制，只为少撞车）：codex 主写 `zion-script` 与 `zion-qa`，WorkBuddy 主写 `zion-assets` 与 `zion-storyboard`；跨到非主写技能时先看 `status`。
- 租约默认 180 分钟；过期视为失效，可被接管（会写进 `history`）。
- **跨技能改动逐个领租约**，不要一次抓四个；做完一个释放一个。
- 工作区是唯一源，**安装目录只写不改**：codex → `~/.codex/skills`，WorkBuddy → `~/.workbuddy/skills`。用 `sync_skills.py --target` 只同步自己那份。
- 删除文件先归档到 `.workbuddy/archive/`，再同步；不直接删安装目录里的文件。
- 内容相同的文件只留一份；确为单独安装而有意双份的，登记到 `skill_lint.py` 的 `DECLARED_DUPES`。
- 交叉引用只写技能名与档名，不写相对路径（`skill_lint.py` 的 CROSS 项会拦住）。
- **正文 `§x` 章节引用要么写「本档 §x」，要么在 `§x` 前 60 字符内写出被引档名**；同句先提了别的档再写 `见 §x` 会被 `SECTION_REF` 判为跨档引用。
- 发现文件数目、行数或时间戳与预期不符时**停下来核对**，不默认是自己的改动。
- 技能改动只在工作区做；`.workbuddy/state`、`.workbuddy/locks` 不随技能分发。
- **换行符一律 LF**：仓库由 `.gitattributes` 统一 `eol=lf`。Windows 上的写入工具可能默认落 CRLF，新写或改写文件后要确认是 LF。混合换行会让 git 在 checkout 时改写文件，并可能触发 `skill_guard.py check` 的假漂移告警。
  - 自查：`git ls-files -z | xargs -0 file | grep CRLF`（或按扩展名逐类抽查），发现即转换。
- **提交只含自己的改动范围**：发现工作区有对方未提交的改动时先说明再决定，不把对方的半成品一起提交。提交前确保 lint 为 0、回归全绿、CHANGELOG 已更新。

## 清理纪律

- 没有入站引用的文件不留：有价值就先接线到 SKILL.md，否则删除。
- 来源沿革、与旧档的对比脚手架、自述定位等不驱动行为的文本不写。
- 说明性文本与内容重复由 `skill_lint.py`（`--meta`）提示，人工判定。

## 维护契约

- 本文件是流程唯一来源；`.workbuddy/memory/MEMORY.md` 只记长期约定与单一来源地图，手册只做入口与使用说明，都不重复流程。
- 改流程 → 改本文件。
- 改风格与色彩的归属 → 改 `MEMORY.md` 的单一来源地图。
- 技能内容改动收工后 → 更新 `CHANGELOG.md` 的当前版本号与变更记录；版本号只在该文件与对话中声明，**不写进技能文件**。
