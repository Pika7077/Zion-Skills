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

分两种场景：**维护者本机同步**（你自己改完往外镜像）与**分享给他人安装**（对方只取用，不改）。

### 3.1 分享给他人：克隆后安装

仓库地址：`https://gitee.com/ZionZhang/zion-skills.git`

```bash
git clone https://gitee.com/ZionZhang/zion-skills.git
cd zion-skills

# 装到 WorkBuddy（四个技能一起装）
cp -r zion-script zion-assets zion-storyboard zion-qa ~/.workbuddy/skills/

# 或装到 Codex
cp -r zion-script zion-assets zion-storyboard zion-qa ~/.codex/skills/

# 只装其中一个也可以（例如只做分镜）
cp -r zion-storyboard ~/.workbuddy/skills/
```

Windows（PowerShell）：

```powershell
git clone https://gitee.com/ZionZhang/zion-skills.git
Copy-Item -Recurse zion-script,zion-assets,zion-storyboard,zion-qa "$env:USERPROFILE\.workbuddy\skills\"
```

装完**重启对应客户端**（WorkBuddy / Codex），否则新技能不会出现在选择器中。

> 仓库为私有：请在 Gitee 仓库「管理 → 仓库成员管理」把对方加为成员，否则 `clone` 无法通过认证。

**分享出去的包是干净的**：技能目录里的 `_user_meta.json`（本机安装时间戳与来源）已从版本控制移除，对方安装时由客户端自行生成自己的那份。

### 3.2 维护者本机同步

**本工作区是唯一真相源，安装目录只写不改。** 技能改动一律先在工作区完成，再镜像出去。

```bash
python .workbuddy/tools/sync_skills.py --target codex       # 同步到 ~/.codex/skills
python .workbuddy/tools/sync_skills.py --target workbuddy   # 同步到 ~/.workbuddy/skills
python .workbuddy/tools/sync_skills.py --dry                # 只报告差异
```

克隆本仓库后同样可直接跑这个脚本，等价于上面的手工复制。

### 3.3 两条通用规则

- 手工安装等价于把某个技能目录整体复制到安装目录下，例如把 `zion-storyboard/` 复制为 `~/.workbuddy/skills/zion-storyboard/`。
- 单独安装是受支持的用法：跨技能引用只写技能名与档名，不写相对路径；确为单独安装而有意双份的文件已在 `.workbuddy/tools/skill_lint.py` 的 `DECLARED_DUPES` 登记。

### 3.4 后续更新的安装命令

已安装的旧版本**不要覆盖 `SKILL.md` 就完事**——技能是一整个目录（`references/` 会增删、`tests/` 会更新），必须整体同步。推荐两种方式：

```bash
# 方式一：在克隆下来的仓库里拉取更新后重新镜像（推荐，能拿到全部改动）
cd zion-skills
git pull
python .workbuddy/tools/sync_skills.py --target workbuddy   # 缺失补齐、不同覆盖、源删的一并删

# 方式二：没保留仓库时，重新克隆再覆盖（注意先备份自定义改动）
git clone https://gitee.com/ZionZhang/zion-skills.git zion-skills-new
cp -r zion-skills-new/zion-script zion-skills-new/zion-assets \
      zion-skills-new/zion-storyboard zion-skills-new/zion-qa ~/.workbuddy/skills/
```

更新后同样要重启客户端。**不要只 `git pull` 而不跑同步**——仓库更新与安装目录生效是两件事。

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
