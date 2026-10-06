# Agnes Image 2.5 Flash

Agnes AI 最新一代图像模型，图像生成、编辑、构图、细节呈现和提示词遵循等整体能力全面超过 Agnes Image 2.1 Flash。
请求与响应参数、支持尺寸、价格和计费方法均与 Agnes Image 2.1 Flash 保持一致。

- **模型名称**: `agnes-image-2.5-flash`
- **API Endpoint**: `POST https://apihub.agnes-ai.com/v1/images/generations`
- **核心优化**: 高信息密度图像、复杂视觉细节和语义对齐
- **当前价格**: 所有支持的输出分辨率档位和输入参考图片当前均免费

## 核心能力

- **文生图** — 根据自然语言提示词生成高质量图像
- **图生图** — 根据提示词转换或优化现有图像
- **多图合成** — 使用多张参考图像组合生成新图像
- **高信息密度图像** — 优化细节丰富、布局复杂、视觉元素密集的图像
- **构图保留** — 编辑输入图像时保留原始构图和主体布局
- **灵活尺寸控制** — 使用 1K / 2K / 3K / 4K 档位并配合宽高比
- **URL / Base64 输出** — 支持图像 URL 或 Base64 数据返回

## 请求头

```
-H "Authorization: Bearer <API_KEY>"
-H "Content-Type: application/json"
```

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 模型名称，使用 `agnes-image-2.5-flash` |
| `prompt` | string | 是 | 图像生成或图像编辑的文本指令 |
| `size` | string | 是 | 输出尺寸档位。推荐 `1K`/`2K`/`3K`/`4K`。也兼容 `1024x768` 这类历史精确尺寸写法，但不支持的尺寸可能被标准化 |
| `ratio` | string | 否 | 与档位式 size 配合使用的宽高比。支持 `1:1`、`3:4`、`4:3`、`16:9`、`9:16`、`2:3`、`3:2`、`21:9`，默认 `1:1` |
| `image` | string[] | 图生图/多图合成必填 | **放在 `extra_body.image` 内**。输入图像数组，支持公共图像 URL 或 Data URI Base64。多图合成时传入多张 |
| `return_base64` | boolean | 否 | 文生图需要以 Base64 返回时使用 |
| `extra_body` | object | 否 | 高级工作流的附加参数 |
| `extra_body.response_format` | string | 否 | 输出格式，常见值为 `url` 或 `b64_json` |

## 尺寸与宽高比

建议将 `size` 档位与 `ratio` 配合使用以获得可预期的输出尺寸。

- 推荐 size 值：`1K`、`2K`、`3K`、`4K`
- 支持的 ratio 值：`1:1`、`3:4`、`4:3`、`16:9`、`9:16`、`2:3`、`3:2`、`21:9`

`1920x1080`、`2560x1440` 等精确尺寸不是模型的**原生输出尺寸**，可能被自动映射到最接近的标准档位和宽高比（例如映射为 16:9 的 1K 输出 1312x736）。
如需生成 16:9 显示素材，建议请求 `size: "2K"` + `ratio: "16:9"`，再在下游裁剪缩放。

### 输出尺寸参考表

| Ratio | 1K | 2K | 3K | 4K |
|-------|-----|-----|-----|-----|
| 1:1 | 1024x1024 | 2048x2048 | 3072x3072 | 4096x4096 |
| 3:4 | 864x1152 | 1728x2304 | 2592x3456 | 3456x4608 |
| 4:3 | 1152x864 | 2304x1728 | 3456x2592 | 4608x3456 |
| 16:9 | 1312x736 | 2624x1472 | 3936x2208 | 5248x2944 |
| 9:16 | 736x1312 | 1472x2624 | 2208x3936 | 2944x5248 |
| 2:3 | 832x1248 | 1664x2496 | 2496x3744 | 3328x4992 |
| 3:2 | 1248x832 | 2496x1664 | 3744x2496 | 4992x3328 |
| 21:9 | 1568x672 | 3136x1344 | 4704x2016 | 6272x2688 |

## 请求示例

### 文生图（URL 输出）

```json
{
  "model": "agnes-image-2.5-flash",
  "prompt": "A luminous floating city above a misty canyon at sunrise, cinematic realism",
  "size": "1024x768",
  "extra_body": { "response_format": "url" }
}
```
返回路径：`data[0].url`

### 文生图（Base64 输出）

```json
{
  "model": "agnes-image-2.5-flash",
  "prompt": "A clean product photo of a glass cube on a white studio background",
  "size": "1024x768",
  "return_base64": true
}
```
返回路径：`data[0].b64_json`

### 图生图（URL 输出）

```json
{
  "model": "agnes-image-2.5-flash",
  "prompt": "Transform the scene into a rain-soaked cyberpunk night while preserving the original composition",
  "size": "1024x768",
  "extra_body": {
    "image": ["https://example.com/input-image.png"],
    "response_format": "url"
  }
}
```

### 图生图（Base64 输出）

```json
{
  "model": "agnes-image-2.5-flash",
  "prompt": "Make the object orange while preserving the original composition",
  "size": "1024x768",
  "extra_body": {
    "image": ["data:image/png;base64,BASE64_HERE"],
    "response_format": "b64_json"
  }
}
```

### 多图合成

```json
{
  "model": "agnes-image-2.5-flash",
  "prompt": "Combine the two characters into an intense fantasy battle scene, cinematic composition",
  "size": "1024x768",
  "extra_body": {
    "image": ["https://example.com/character-1.png", "https://example.com/character-2.png"],
    "response_format": "url"
  }
}
```

## 响应格式

```json
{
  "created": 1780000000,
  "data": [
    {
      "url": "https://storage.googleapis.com/agnes-aigc/xxx.png",
      "b64_json": null,
      "revised_prompt": null
    }
  ]
}
```

## 推荐提示词结构

- **文生图**：`[主体] + [场景/环境] + [风格] + [光照] + [构图] + [质量要求]`
  - 例：日出时分薄雾峡谷上方的发光浮空城市，电影级写实风格，广角构图，丰富建筑细节，柔和金色光线，高视觉密度
- **图生图**：`[改变要求] + [新风格/场景] + [需要添加或移除的元素] + [需要保留的元素]`
  - 例：将白天街道场景改为电影级赛博朋克夜景，添加霓虹招牌和湿滑路面倒影，同时保留原始街道布局、相机角度和主要建筑形状
- **多图合成**：说明每张参考图的角色，以及最终图像应如何组合
  - `[参考图角色] + [目标场景] + [图像之间的关系] + [风格/光照/构图]`
- **高信息密度图像**：清晰描述视觉层次结构（主要主体、背景环境、重要次要细节、风格、光照、构图约束）

## 常见错误与故障排除

| 错误 | 说明 | 修正 |
|------|------|------|
| 顶层放置 `response_format` | 会被忽略 | 必须放在 `extra_body.response_format` |
| 图生图传递 `tags: ["img2img"]` | 不需要该参数 | 只需在 `extra_body.image` 提供输入图像 |
| 输入图像 URL 无法访问 | 使用了非公共 URL | 用公共 HTTPS URL（无需登录/cookie），否则改用 Data URI Base64 |
| 请求超时 | 生成需数秒到几十秒 | 客户端超时建议 60s - 360s |
| 图生图缺少 image | `extra_body.image` 为必填 | 补上输入图像 |

## 定价

`agnes-image-2.1-flash` 与 `agnes-image-2.5-flash` 的价格及计费方法相同。

| 计费项 | 刊例价 | 现价（优惠） |
|--------|--------|-------------|
| 1K 输出图片 | $10 / 千张 | $0 |
| 2K 输出图片 | $18 / 千张 | $0 |
| 3K 输出图片 | $21 / 千张 | $0 |
| 4K 输出图片 | $24 / 千张 | $0 |
| 第 4 张起的输入参考图片 | $0.003 / 张 | $0 / 张 |

按刊例价计算时，前 3 张输入参考图片不额外收费。当前所有输出分辨率档位和输入参考图片均免费。

## 接入检查清单

- 使用 `agnes-image-2.5-flash` 作为模型名称
- 使用 `https://apihub.agnes-ai.com/v1/images/generations` 作为 API 端点
- 文生图请求必须包含 `model`、`prompt` 和 `size`
- 建议使用 `1K`/`2K` 等 size 档位并配合 `ratio` 以获得可预期尺寸
- 图生图和多图合成请求需在 `extra_body.image` 中提供输入图像
- 请勿将 `response_format` 放在顶层，也不要传递 `tags: ["img2img"]`

---
来源：https://www.agnes-ai.com/zh-Hans/docs/agnes-image-25-flash
