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

安装、更新、目标目录和验证步骤统一在本节维护。四个技能可一起安装，也可单独取用；始终复制完整技能目录。

### 3.1 交给 agent 安装

把下面的提示词发给使用者的 agent：

```text
请安装 Zion 技能家族：zion-script、zion-assets、zion-storyboard、zion-qa。
仓库：https://gitee.com/ZionZhang/zion-skills

先检查当前环境、实际技能目录和已有安装。若这是开发工作区（有
.workbuddy/tools/ 和 CHANGELOG.md），不要用下载副本覆盖本地源文件。
已安装且与源一致时只验证；有差异时先备份，再更新安装副本。

取包到临时目录，任选一种：
  curl -fL -o zion.zip https://gitee.com/ZionZhang/zion-skills/repository/archive/main.zip
  git clone --depth 1 https://gitee.com/ZionZhang/zion-skills.git
归档下载后检查是否为有效 ZIP；失败则用 git，不反复下载同一错误页面。

确认当前工具实际扫描的技能目录，再复制所需技能的完整目录。
更新时替换整个技能目录，清理源中已删除的旧文件；保留备份，勿清理其他技能。
验证 SKILL.md、文件集合与内容均与源一致。若能运行 Python，再运行所装
技能的自动回归。汇报验证结果、commit SHA（归档则报下载时间）与生效方式。
```

### 3.1.1 目标目录

| 环境 | 本仓库使用的目录 |
|---|---|
| Codex | `~/.codex/skills/` |
| WorkBuddy | `~/.workbuddy/skills/` |
| 其他 agent | 以该工具的实际配置或官方文档为准，不猜测兼容目录 |

Windows 下 `~` 对应用户目录。技能采用 `SKILL.md` 格式，但发现目录与刷新方式由各工具决定。

### 3.2 手工安装与更新

按上面的命令取包后，把所需目录复制到目标，例如：

```powershell
Copy-Item -Recurse zion-script,zion-assets,zion-storyboard,zion-qa "$env:USERPROFILE\.workbuddy\skills\"
```

首次安装先确保目标父目录存在。更新前备份旧技能，然后替换完整目录；仅把新文件覆盖进去会留下已删除的旧参考档。不要只复制 `SKILL.md`。

`curl -L` 用于跟随归档地址的跳转；拿到 HTML 时先检查跳转和响应，不据此推断仓库是否公开。包大小、文件数随版本变化，验证以本次下载的源为准。

### 3.3 维护者同步与验证

在开发工作区修改源文件，按 [AGENTS.md](AGENTS.md) 校验后同步**已有**安装目录。未知参数、缺失参数或源技能缺少有效入口时会停止，不执行镜像：

```bash
python .workbuddy/tools/sync_skills.py --target codex
python .workbuddy/tools/sync_skills.py --target codex --dry
```

WorkBuddy 把目标换为 `workbuddy`；脚本只支持这两个目标，目标不存在时会跳过，首次安装用上面的目录复制。镜像会补齐、覆盖并删除源中已移除的文件；包括本机生成的 `_user_meta.json`，客户端会重新生成自己的元数据。

验证：

1. 四个（或选装的）技能入口存在；逐文件比较内容与文件集合，排除 Python 缓存和客户端生成的元数据。
2. 同步后的 `--dry` 应为 `added=0 updated=0 removed=0`；在安装副本运行对应自动回归。
3. 检查入口文本为 UTF-8、无 BOM、LF。Windows 终端乱码先检查终端编码，不直接判定文件损坏。
4. 记录源 commit SHA 或归档下载时间。仓库更新后还需更新安装副本；客户端未发现新技能时按其要求刷新或重新打开。

## 四、目录与文档

| 位置 | 内容与读取时机 |
|---|---|
| 四个 `zion-*/SKILL.md` | 技能入口；仅按当前任务加载相关参考档 |
| 各技能 `references/`、`scripts/`、`tests/` | 详细判据、工具和回归资料；目录随技能完整分发 |
| [Zion技能使用手册.md](Zion技能使用手册.md) | 调用示例、任务路由与交付说明 |
| [AGENTS.md](AGENTS.md) | 维护流程、并发规则与提交条件的唯一来源 |
| [CHANGELOG.md](CHANGELOG.md) | 当前版本、规模、验证状态与本轮变化 |
| `.workbuddy/tools/` | lint、并发守卫、安装镜像；参数见各脚本 docstring |
| `.workbuddy/memory/MEMORY.md` | 长期事实与已知限制 |
| `.workbuddy/memory/style-single-source.md` | 内容归属地图 |
| `.workbuddy/memory/material-intake.md` | 外部材料的吸收规则 |
| [.workbuddy/archive/README.md](.workbuddy/archive/README.md) | 历史记录索引；仅回溯具体问题时读取 |

参考档编号用于路由，不是阅读顺序。维护步骤按 AGENTS 执行，不在本入口重复；版本规则在 CHANGELOG 维护，技能正文不写版本号。
