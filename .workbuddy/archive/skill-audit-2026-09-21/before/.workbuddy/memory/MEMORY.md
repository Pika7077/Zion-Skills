# 工作空间维护约定

## 流程唯一来源（2026-09-20 设定）

工作区由 **codex 与 WorkBuddy 同时维护**。标准循环、硬规则、清理纪律一律以工作区根目录的 **`AGENTS.md`** 为准，本文件不重复，只记长期约定与事实。

工具三件套（均在 `.workbuddy/tools/`）：

- `skill_lint.py` —— 内容校验：JUNK／ORPHAN／DUPLICATE／DANGLING／CROSS／`--meta`。
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

## 风格与色彩：单一来源地图（2026-09-20 核对）

交叉引用只写技能名与档名，不复制内容。维护某一项时改这里，别处只引用：

| 内容 | 唯一来源 |
|---|---|
| 题材美术（形制／材质／器物／色板／锁定项） | `zion-assets/references/19-genre-style-profiles.md` |
| 视觉语言（构图／镜头／调度／光色气质，含影人拆解） | `zion-assets/references/director-vision-language.md` |
| 成像响应（胶片颗粒／宽容度／印片黑位与色彩密度） | `zion-assets/references/film-and-print-stocks.md` |
| 调色词库、八种调色预设、60:30:10、一个风格锚点、**Anti-Slop 替换表、Register Poles** | `zion-storyboard/references/13-camera-and-texture.md` §六 |
| 光位／光比／配光层级／色温／灯光律 | `zion-storyboard/references/20-lighting-system.md` |
| Style Sheet（hex 调色板六项常量）与 Forbidden List | `zion-script/references/11-character-and-worldbuilding.md` §四 |

已删除且不再恢复：`zion-script/references/05-scene-and-color-bible.md`、`07-prompt-spec.md`（外部会话删除并清理引用；副本存 `.workbuddy/archive/source-deleted-2026-09-20/`）。

## 目录约定

- 工作区为唯一源：`zion-script` / `zion-assets` / `zion-storyboard` / `zion-qa` + `Zion技能使用手册.md`。
- 维护工具在 `.workbuddy/tools/`；归档在 `.workbuddy/archive/`。
- 不提交 `__pycache__` 与 `.pyc`。
