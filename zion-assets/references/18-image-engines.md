# 图像引擎：选择与适配

核验日期：2026-09-21。以下是提示词适配依据；真正提交前仍须核对当前工具或入口是否开放相应能力。

## 选择与记录

未指定图像引擎时使用项目默认 **GPT Image 2**，在 `meta.image_engine` 记录。**Midjourney 仅在用户主动提起时使用**。项目已确认的通道与参数优先；不擅自切换通道或升级模型。

图像与视频模型分别确认；视频规格由 `zion-storyboard` 的模型适配档管理。未收录模型可先提供内容草案，核验任务实际需要的能力后再说明适配范围。

## GPT Image 2

- 模型 ID：`gpt-image-2`，支持生成与编辑。身份、风格、构图等参考图需标明用途；编辑后的身份和细节仍须复核，不承诺完全锁定。[模型页](https://developers.openai.com/api/docs/models/gpt-image-2)
- API 尺寸受边长、比例及总像素约束，并非任意“4K”尺寸都可用。需要精确交付时按实际尺寸查表；该模型的输入保真度始终为高，不添加 `input_fidelity` 参数。[生成指南](https://developers.openai.com/api/docs/guides/image-generation)
- 透明背景处于预览支持阶段；使用 `background=transparent` 时输出需为 PNG 或 WebP。实际入口没有暴露该能力时，说明限制并安排后期处理，不自动换模型。[生成接口参考](https://developers.openai.com/api/reference/cli/resources/images/methods/generate)

提示词按“用途 → 主体与结构 → 构图 → 光色 → 文字 → 必须保持或排除的内容”组织，需要的栏目才写。要渲染的文字用引号照录，说明位置与层级；生成后逐字验收，不以准确率宣传代替检查。

编辑时明确“改什么、保留什么”，引用真实输入文件。先用适合预览的设置验证构图和身份，再按交付要求提高质量；不写固定延迟、单图价格或未经核验的参考图数量。

## Midjourney

核验时的默认版本为 **V8.2**，但用户实际选择的版本决定参数兼容性。[版本文档](https://docs.midjourney.com/hc/en-us/articles/32199405667853-Version)

| 用途 | 已核验方式 | 使用边界 |
|---|---|---|
| V8.1 / V8.2 编辑与参考 | Edit Model，可用最多 4 张参考图；支持局部编辑和扩图 | 按实际网页或 Discord 入口操作；不承诺主体绝对不变 |
| V7 主体参考 | Omni Reference，单张图，`--oref` 与 `--ow` | 只在明确使用 V7 时采用，不外推到 V8 |
| 风格参考 | Style Reference，`--sref` | 传递视觉风格，不等同人物身份或物体复制 |

依据：[Edit Model](https://docs.midjourney.com/hc/en-us/articles/48495453462797-Edit-Model)、[Omni Reference](https://docs.midjourney.com/hc/en-us/articles/36285124473997-Omni-Reference)、[Style Reference](https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference)。

提示词先写主体、空间连接、人物路径和必要材质，再写气氛。只使用当前版本与入口已核验的参数，不拼接不同代际的参数，不声称系统会自动回退到其它版本。

## 项目级覆盖与文字通道

以下是本项目的制作约定，不是对所有模型文字能力的断言；用户要求优先。

| 通道 | 可见中文与项目指定品牌字 |
|---|---|
| GPT Image 2 | 默认直接渲染，用引号照录，生成后逐字检查 |
| Midjourney | 默认留空，后期合成贴字 |

切换通道时同步说明文字生成与合成安排，更新元数据；不覆盖已交付资产。

## 扩展或复核能力

只核验当前任务涉及的项目：官方来源与日期、模型版本和入口、参考图方式、文字要求、尺寸与格式、编辑能力、实际可用参数。未知字段明确标注，不能据默认值宣称“已验证可生成”。价格、延迟和平台上架情况不作为长期提示词规则存放。
