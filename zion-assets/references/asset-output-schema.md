# 资产输出契约

适用于人物、场景、道具及其他资产登记。字段可以按任务裁剪，但同一项目内保持一致。

## 项目级字段

| 字段 | 用途 |
|---|---|
| `meta.handoff_schema_version` | 跨 Skill 交接契约版本；当前为 `1.0` |
| `meta.project_id` | 项目稳定 ID；继承剧本，不因文件改名变化 |
| `meta.source` | 源剧本、文档、视频、粗分镜或已有资产 |
| `meta.source_script_version` | 当前资产包所依据的剧本版本 |
| `meta.source_scene_ids` | 当前资产包覆盖的稳定场次 ID 列表 |
| `meta.image_engine` | 需要图像提示词时记录目标图像引擎与版本；未指定时为 `GPT Image 2` |
| `meta.visual_profile` | 已确认的题材、美术和材质方向 |
| `meta.style_skeleton` | 项目风格骨架的冻结段文本；同批资产逐字复用，写法见 [资产提示词](asset-prompt-builder.md#项目风格骨架冻结段与变量段) |
| `meta.style_version` | 冻结段版本号（如 `style_v1`）；替换光源、材质锚点或调色时递增，并记录被替换项 |
| `meta.evidence_policy` | 只提取 / 允许推断 / 允许设计补全 |
| `meta.downstream_use` | 人设确认、场景参考、正式分镜、视频参考、版式等 |

## 通用资产字段

| 字段 | 用途 |
|---|---|
| `asset_id` | 已登记资产的稳定唯一 ID；人物提取结果尚未登记时为 null，不能作为正式资产交接 |
| `category` | character / location / prop / costume / creature / vehicle / gfx / vfx / audio / other |
| `name` / `aliases` | 显示名与别名 |
| `source_evidence` | 原文、画面、用户设定或粗分镜需求 |
| `source_extraction_ids` | 可选；经证据核对映射到本资产的人物提取记录键，不以姓名自动关联 |
| `evidence_level` | explicit / inferred / designed / unknown |
| `stable_anchors` | 不随镜头变化的身份、结构、材质或声音特征 |
| `scene_consistency` | 可选；仅场景资产使用。含 `power_mechanism`（谁控制入口/座位/桌/门）、`vertical_lane`（前景压迫物／中央通道／背景锚点／门槛轴／交接区）、`clearance`（净空与体量：头顶净空／身体余量／可退距离／比例参照）、`view_set`（已制作观察方向及所属时间/天气状态）、`light_source_shared`（同组 View 共用主光与色温关系）、`state_ladder`（已用 S 状态与可见证据）、`protected_anchors` / `allowed_changes` / `forbidden_drift`、`narrative_objects`、`empty_stage`、`readiness`、`before_after`。字段定义见 [场景一致性与状态阶梯](26-scene-consistency.md) |
| `state_variant` | 默认、换装、损伤、破损、开合、天气/时间等状态 |
| `version` | 当前版本及父版本 |
| `status` | identified / designed / candidate / approved / uploaded / deprecated；状态定义与准入见 [资产登记与交接](asset-registry-and-handoff.md) |
| `required_views` | 下游实际需要的角度、比例、局部或状态 |
| `files` | 真实文件、格式、用途与验收状态 |
| `target_reference` | 目标入口的实际附件/引用映射 |
| `dependencies` | 相关人物、场景、道具、服装、声音或镜头 |
| `constraints` | 不可修改项、使用边界和未知项 |
| `image_prompt` | 需要时提供的目标引擎提示词；不等同于已生成文件 |
| `source_provenance` | 外部或用户素材的来源、提供者、链接或项目登记位置；未知时明确记录 |
| `rights_status` | confirmed / user-asserted / pending / restricted / unknown；与制作状态分开 |
| `permitted_uses` / `rights_restrictions` | 已明确允许的参考、编辑、生成、发布等用途及限制，不自行补全 |
| `identity_consent` / `attribution` | 涉及可识别人物、声音或需署名素材时按实际证据记录 |

人物的详细语义字段继续使用 [人物 JSON](json-schema.md)；本档负责跨资产统一登记，不重复人物专用字段。来源与使用边界字段的判定见 [来源、许可与使用边界登记](source-and-rights.md)，不适用时可以省略。

## 资产交接字段（供分镜拼装引用表）

正式分镜的生成器（`zion-storyboard` 的导出脚本）按以下结构消费资产交接数据。资产登记后交付时写入这些字段，口径与脚本保持一致：

| 字段 | 用途 |
|---|---|
| `meta.asset_mode.enabled` | 是否启用“全能参考”模式；启用后人物/场景/道具外观以资产引用表为准，提示词不重复外貌与服装 |
| `meta.asset_mode.reference_syntax` | 引用符号，默认 `@` |
| `meta.asset_mode.character_assets[]` | 人物交接项；保留 `asset_id`、`ref`、`version`、`status`、`files`、`target_reference`，可附 `identity`/`role` |
| `meta.asset_mode.scene_assets[]` | 场景交接项；保留上述公共字段，可附 `angles[]`、`single_angle_only`、`fixed_props` |
| `meta.asset_mode.prop_assets[]` | 道具交接项；保留上述公共字段 |
| `meta.asset_mode.other_assets[]` | 服装、生物、载具、图形、特效、声音等交接项；保留上述公共字段 |
| `meta.asset_mode.unregistered_characters` | 未登记角色，需回补资产 |
| `meta.temp_asset_mode` | 临时资产引用模式（区别于正式资产库） |
| `meta.state_assets.official[]` | 正式状态资产引用 |
| `meta.state_assets.temporary[]` | 临时状态引用 |
| `meta.state_assets.suggested[]` | 建议补做的状态资产 |

交接项不是只含 `ref` 的摘要，而是登记记录的无损投影视图；公共字段不可丢失，角度、状态、依赖与限制按用途带入。正式导演稿与视频生成提示词的状态准入统一按 [资产登记与交接](asset-registry-and-handoff.md) 执行。

分镜的每个镜头用 `source_scene_id` 回指剧本场次，并通过 `asset_refs`、`character_refs`、`scene_refs`、`prop_refs` 引用交接项的 `ref` 或 `asset_id`。任何引用必须唯一命中当前交接包。

## 最小示例

```json
{
  "meta": {
    "handoff_schema_version": "1.0",
    "project_id": "PRJ_contract",
    "source": "合同对峙",
    "source_script_version": "script_v3",
    "source_scene_ids": ["SC001"],
    "image_engine": "GPT Image 2",
    "evidence_policy": "允许设计补全",
    "downstream_use": "正式分镜与视频参考",
    "asset_mode": {
      "enabled": true,
      "reference_syntax": "@",
      "prop_assets": [{
        "asset_id": "prop_contract_01",
        "ref": "@合作合同",
        "version": "1.0",
        "status": "approved",
        "files": [{"path": "assets/contract_v1.0.png"}],
        "target_reference": null
      }]
    }
  },
  "assets": [
    {
      "asset_id": "prop_contract_01",
      "category": "prop",
      "name": "合作合同",
      "aliases": ["文件", "合同"],
      "evidence_level": "explicit",
      "stable_anchors": ["深蓝封面", "A4尺寸", "左侧装订"],
      "state_variant": "未签署",
      "version": "1.0",
      "status": "approved",
      "required_views": ["封面", "打开后的签字页"],
      "files": [{"path": "assets/contract_v1.0.png", "purpose": "正式分镜参考"}],
      "target_reference": null,
      "constraints": ["正文精确文字留待后期合成"]
    }
  ]
}
```

示例值只说明结构，不是项目默认内容。
