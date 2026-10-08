# Zion 技能家族

面向 AIGC 短片／短剧的四段式技能包：**剧本 → 资产 → 分镜 → 校验**。

四个技能可以一起安装使用，也可以各自单独取用。安装后可在 Codex 与 WorkBuddy 两类助手中调用。

## 一、四个技能

| 技能 | 阶段 | 解决什么问题 | 主要交付 |
|---|---|---|---|
| [`zion-script`](zion-script/SKILL.md) | 剧本 | 故事发生什么 | 故事结构、场次式剧本、对白、人物动机与结局 |
| [`zion-assets`](zion-assets/SKILL.md) | 资产 | 画面中有什么、长什么样、如何稳定复用 | 人物／场景／道具资产卡、稳定 ID、版本、参考图需求、图像提示词与登记 |
| [`zion-storyboard`](zion-storyboard/SKILL.md) | 分镜 | 故事如何被拍出来 | 粗分镜、导演分镜、调度、镜头时间线、画幅适配、视频提示词 |
| [`zion-qa`](zion-qa/SKILL.md) | 校验 | 内容是否正确、连续、可生成、可使用 | 分级问题、证据、修改建议、通过项与复验结论 |

快速判断：

- 写故事、改对白、补动机 → `zion-script`
- 做人物、场景、道具、服装变体或图像提示词 → `zion-assets`
- 拆镜、设计运镜灯光转场、制作视频提示词 → `zion-storyboard`
- 检查剧本、资产、分镜、提示词或生成结果 → `zion-qa`

## 二、推荐流程

四个技能是职责分类，不是只能单向执行的流水线。推荐走两轮资产流程：

```text
zion-script          锁定故事事实、人物动机、场次、对白与结局
      ↓
zion-storyboard      粗分镜：判断实际需要哪些人物角度、场景方向、道具状态
      ↓
zion-assets          建立并锁定资产，登记真实文件、版本与可用状态
      ↓
zion-storyboard      正式分镜：挂载真实资产，完成镜头时间线与视频提示词
      ↓
zion-qa              投喂前检查与生成后验收
```

简单项目可以跳过粗分镜回路；只做文字剧本时不必进入资产或分镜阶段。

## 三、安装与同步

分三种场景：**发给对方的 agent 自行安装**（最省事，对方不用敲命令）、**分享给他人手工安装**、**维护者本机同步**（你自己改完往外镜像）。

### 3.1 把仓库发给对方的 agent，让它自己装（推荐）

如果对方也在用 agent，**不用教他敲命令**——把下面这一段原样发过去即可。对方的 agent 会自己下载、找到自己的技能目录、装好并验证。

> 提示词**不限定 agent 品牌**：技能用的是 `SKILL.md` 开放标准（Agent Skills），Claude Code / Codex / Cursor / Gemini CLI / Copilot / DeepSeek Harness / ZCode 等都读同一套格式。差异只在**发现目录**，而这一步交给对方的 agent 自己判断最准。

```text
请帮我安装 Zion 技能家族（AIGC 短片/短剧的四段式技能包：剧本→资产→分镜→校验）。

下载地址（公开，无需账号）：
https://gitee.com/ZionZhang/zion-skills/repository/archive/main.zip

这是标准的 Agent Skills（SKILL.md 开放标准），包含四个技能目录：
zion-script、zion-assets、zion-storyboard、zion-qa

请按以下步骤操作：
1. 下载上面的 zip 并解压到临时目录（约 900KB；若你的环境有 git，
   也可以 git clone https://gitee.com/ZionZhang/zion-skills.git）。
2. 先看你自己的技能目录在哪（常见位置，按你的实际环境判断）：
   - WorkBuddy → ~/.workbuddy/skills/     Codex → ~/.codex/skills/
   - Claude Code → ~/.claude/skills/      Cursor → ~/.cursor/skills/
   - ZCode → ~/.zcode/skills/             DeepSeek Harness → $DSH_HOME/skills
   - 跨工具公约目录（多数工具都扫）→ ~/.agents/skills/
   若你的工具不在上面、或你也不确定，就装到 ~/.agents/skills/，
   或先查你工具的文档确认技能目录再动手；不要猜。
   （Windows 下 ~ 指 %USERPROFILE%）
3. 把四个技能目录整体复制过去；若目标已有同名技能，先备份再覆盖。
4. 整个目录一起装，不要只复制 SKILL.md——技能还包含 references/ 与 tests/ 子目录。
5. 装完告诉我：装到哪个目录、四个技能是否都在、以及需要重启/刷新才能生效。
```

对方回执后，**提醒他重启（或刷新）客户端**，技能才会出现在选择器里。

**为什么用 zip 而不是 git**：归档包 892KB，浅克隆 3.0M（其中 808K 是 `.git`）；归档不含版本历史，也**不含 `_user_meta.json` 等本机元数据**；而且不依赖对方装 git——很多 agent 环境有网络下载能力但没有 git。

**实测过的三种取包方式**（可直接转述给对方）：

| 方式 | 体积 | 需要 git | 说明 |
|---|---:|---|---|
| **zip 归档**（推荐） | 892KB | 否 | `curl -sL -o zion.zip <归档地址>` 后解压，顶层即四个技能 |
| 浅克隆 | 3.0M | 是 | `git clone --depth 1`，要长期跟随更新时用 |
| 全量克隆 | — | 是 | 维护者用；含完整历史 |

三种方式装出来的 skill 目录**内容完全一致**（`zion-script` 17 文件／`zion-assets` 19／`zion-storyboard` 39／`zion-qa` 7）。

机器可读的极简形态（供脚本调用，把 `<目标>` 换成实际安装目录）：

```bash
curl -sL -o zion.zip https://gitee.com/ZionZhang/zion-skills/repository/archive/main.zip \
  && unzip -q zion.zip \
  && cp -r zion-skills-main/zion-script zion-skills-main/zion-assets \
            zion-skills-main/zion-storyboard zion-skills-main/zion-qa <目标>/
```

若环境是 WorkBuddy 或 Codex，也可在解压后的仓库里跑脚本（自动解析安装路径）：

```bash
python .workbuddy/tools/sync_skills.py --target workbuddy   # 或 --target codex
```

该脚本只支持这两个目标，其他环境走上面的手工复制。

### 3.1.1 跨 agent 通用性

技能本身**跨 agent 通用**，因为 `SKILL.md` 已是开放标准（Agent Skills，源自 Anthropic，现被 OpenAI、Microsoft、Cursor 等采纳）。**唯一需要按 agent 调整的是安装目录。** 已核实的目录：

| Agent | 用户级技能目录 | 备注 |
|---|---|---|
| WorkBuddy | `~/.workbuddy/skills/` | 本项目维护者环境 |
| Codex CLI | `~/.codex/skills/` | |
| Claude Code | `~/.claude/skills/` | SKILL.md 标准的发源地 |
| Cursor | `~/.cursor/skills/`、`~/.agents/skills/` | **兼容读取** `.claude/skills/` 与 `.codex/skills/` |
| ZCode | `~/.zcode/skills/`、`~/.agents/skills/` | 内置「从外部 Agent 导入」，可直接扫 Claude Code / Codex 等目录 |
| DeepSeek Harness | `$DSH_HOME/skills`、`~/.agents/skills/` | 也接受扁平 `<name>.md` 布局；支持 `references/`、`scripts/` |
| Gemini CLI / Copilot 等 | 见各自文档 | 同属 Agent Skills 标准 |

两条实用结论：

- **`~/.agents/skills/` 是事实上的跨工具公约目录**（Cursor、ZCode、DeepSeek Harness 都扫它）。不确定装哪时，装这里命中率最高；但它**不是每个工具都认**，能确认真实目录时优先装真实目录。
- **装到 `~/.claude/skills/` 或 `~/.codex/skills/`，不少其他工具会顺带认到**（Cursor 明确兼容读取这两处）。若对方同时用多个工具，这是"装一处、多处可用"的省事选择。

技能内部对 agent 的**假设很轻**：不依赖特定工具名、不依赖子代理、不依赖特定权限模型；引用的脚本是标准 Python。因此跨 agent 迁移通常只需换目录，不需改内容。

### 3.2 手工安装（不给 agent 时）

仓库地址：`https://gitee.com/ZionZhang/zion-skills.git`（公开，无需账号）

不用 git 也行——下 zip 解压后的目录结构与克隆完全相同：

```bash
curl -sL -o zion.zip https://gitee.com/ZionZhang/zion-skills/repository/archive/main.zip
unzip -q zion.zip && cd zion-skills-main
```

```bash
# 装到 WorkBuddy（四个技能一起装）
cp -r zion-script zion-assets zion-storyboard zion-qa ~/.workbuddy/skills/

# 或装到 Codex
cp -r zion-script zion-assets zion-storyboard zion-qa ~/.codex/skills/

# 只装其中一个也可以（例如只做分镜）
cp -r zion-storyboard ~/.workbuddy/skills/
```

习惯用 git 的话，用 `git clone https://gitee.com/ZionZhang/zion-skills.git` 替代前两行即可（想省体积可加 `--depth 1`）。

Windows（PowerShell）：

```powershell
Copy-Item -Recurse zion-script,zion-assets,zion-storyboard,zion-qa "$env:USERPROFILE\.workbuddy\skills\"
```

装完**重启对应客户端**（WorkBuddy / Codex），否则新技能不会出现在选择器中。

**分享出去的包是干净的**：技能目录里的 `_user_meta.json`（本机安装时间戳与来源）已从版本控制移除，归档与克隆副本都不含它，对方安装时由客户端自行生成自己的那份。

### 3.3 维护者本机同步

**本工作区是唯一真相源，安装目录只写不改。** 技能改动一律先在工作区完成，再镜像出去。

```bash
python .workbuddy/tools/sync_skills.py --target codex       # 同步到 ~/.codex/skills
python .workbuddy/tools/sync_skills.py --target workbuddy   # 同步到 ~/.workbuddy/skills
python .workbuddy/tools/sync_skills.py --dry                # 只报告差异
```

克隆本仓库后同样可直接跑这个脚本，等价于上面的手工复制。

### 3.4 两条通用规则

- 手工安装等价于把某个技能目录整体复制到安装目录下，例如把 `zion-storyboard/` 复制为 `~/.workbuddy/skills/zion-storyboard/`。
- 单独安装是受支持的用法：跨技能引用只写技能名与档名，不写相对路径；确为单独安装而有意双份的文件已在 `.workbuddy/tools/skill_lint.py` 的 `DECLARED_DUPES` 登记。

### 3.5 后续更新

已安装的旧版本**不要覆盖 `SKILL.md` 就完事**——技能是一整个目录（`references/` 会增删、`tests/` 会更新），必须整体同步。

**没有 git 的环境（zip 路子）**——重新下载覆盖即可：

```bash
curl -sL -o zion.zip https://gitee.com/ZionZhang/zion-skills/repository/archive/main.zip \
  && unzip -q -o zion.zip \
  && cp -r zion-skills-main/zion-script zion-skills-main/zion-assets \
            zion-skills-main/zion-storyboard zion-skills-main/zion-qa <目标>/
```

**有 git 的环境**——拉取后重新镜像（能精确处理增删）：

```bash
cd zion-skills
git pull
python .workbuddy/tools/sync_skills.py --target workbuddy   # 缺失补齐、不同覆盖、源删的一并删
```

也可以直接让对方的 agent 重跑 3.1 的提示词——它自带「已克隆过则更新」的分支。

更新后同样要重启客户端。两个要点：**仓库更新 ≠ 安装目录生效**（必须重新拷贝或跑同步）；归档地址末尾是 `main`，若日后改用分支或标签，把这段换掉即可。

## 四、目录结构

```text
.
├── zion-script/            # 剧本技能
│   ├── SKILL.md            #   入口：职责边界、流程、参考档路由
│   ├── references/         #   参考档（按需加载）
│   └── tests/              #   人工回归用例
├── zion-assets/            # 资产技能（另有 scripts/ 提取脚本）
├── zion-storyboard/        # 分镜技能（另有 scripts/ 解析与审计脚本）
├── zion-qa/                # 校验技能
├── Zion技能使用手册.md      # 用法：各技能适合做什么、怎么调用
├── AGENTS.md               # 协作与维护流程（流程唯一来源）
├── CHANGELOG.md            # 版本号、变更沿革与当前规模
└── .workbuddy/
    ├── tools/              # skill_lint.py / skill_guard.py / sync_skills.py
    ├── memory/             # 长期约定、内容归属地图、材料吸收规则
    └── archive/            # 删除与替换前的归档
```

每个技能的 `SKILL.md` 是入口，参考档按需加载；`references/` 内的档名编号只用于路由，不代表阅读顺序。

## 五、维护工具

改动技能前后用这三件套（用法见各自 docstring）：

| 工具 | 作用 | 常用命令 |
|---|---|---|
| `skill_lint.py` | 内容校验：JUNK／ORPHAN／DUPLICATE／DANGLING／SECTION_REF／CROSS | `python .workbuddy/tools/skill_lint.py`（须 0 问题） |
| `skill_guard.py` | 并发守卫：写租约与基线快照 | `status` / `acquire` / `snapshot` / `check` / `release` |
| `sync_skills.py` | 镜像到安装目录 | `--target codex\|workbuddy`、`--dry` |

收工校验（完整循环见 [AGENTS.md](AGENTS.md)）：

```bash
python .workbuddy/tools/skill_lint.py
python -B zion-assets/tests/test_extract_characters.py
python -B zion-storyboard/tests/test_storyboard_audit.py
python .workbuddy/tools/skill_guard.py check
```

各技能的 `tests/manual-regression.md` 记录需要人工复核的用例，与上面两个脚本同属收工动作。

## 六、协作约定

本仓库由 codex 与 WorkBuddy 两个会话同时维护：

- 同一技能同时只让一个会话写。动手前 `skill_guard.py acquire` 领租约、`snapshot` 拍基线，收工前 `check` 看有无他人改动，最后 `release`。
- 工作区是唯一源；codex 只同步 `~/.codex/skills`，WorkBuddy 只同步 `~/.workbuddy/skills`。
- 删除文件先归档到 `.workbuddy/archive/`，再同步。
- 换行符一律 LF（由 `.gitattributes` 统一，`core.autocrlf=false`）；新写或改写文件后须确认，混合换行会造成假漂移告警。
- 一次逻辑改动一次提交，提交信息写清技能、改动与版本号。

## 七、文档

| 文档 | 内容 |
|---|---|
| [Zion技能使用手册.md](Zion技能使用手册.md) | 每个技能适合做什么、如何调用、常见任务怎么走 |
| [AGENTS.md](AGENTS.md) | 标准循环、硬规则、清理纪律与维护契约 |
| [CHANGELOG.md](CHANGELOG.md) | 当前版本、变更沿革、规模快照 |
| `.workbuddy/memory/style-single-source.md` | 风格／色彩／镜头／声音等内容各归哪一档 |
| `.workbuddy/memory/material-intake.md` | 外部学习材料如何判归属、如何判该不该吸收 |

版本号只在 `CHANGELOG.md` 与对话中声明，不写进技能文件。
