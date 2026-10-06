# Agnes AI Image API 参考（速查）

## 基本信息

- Base URL: `https://apihub.agnes-ai.com`
- 认证: Bearer Token (Authorization header)
- 兼容性: OpenAI API 兼容
- 模型列表:
  - `agnes-image-2.5-flash`: **最新版**，生成/编辑/构图/细节/提示词遵循全面超过 2.1，支持文生图/图生图/多图合成
  - `agnes-image-2.1-flash`: 旧版，参数与 2.5 完全一致
  - `agnes-image-2.0-flash`: 更旧版

## 文生图

```
POST /v1/images/generations
Content-Type: application/json
Authorization: Bearer ***

{
  "model": "agnes-image-2.5-flash",
  "prompt": "一只巨大的棕熊，威风凛凛地站在森林中，写实风格",
  "size": "1K",
  "ratio": "16:9",
  "extra_body": { "response_format": "url" }
}
```

- `size`: 档位 `1K`/`2K`/`3K`/`4K`，或精确尺寸 `1024x768`
- `ratio`: 可选，配合档位式 size（默认 1:1）
- `return_base64: true` 可让文生图返回 Base64

返回:
```json
{"data": [{"url": "https://platform-outputs.agnes-ai.space/images/t2i/xxx.png"}]}
```

## 图生图 / 多图合成

```
POST /v1/images/generations
Content-Type: application/json
Authorization: Bearer ***

{
  "model": "agnes-image-2.5-flash",
  "prompt": "Transform the scene into a rain-soaked cyberpunk night, preserve composition",
  "size": "1024x768",
  "extra_body": {
    "image": ["data:image/png;base64,..."],
    "response_format": "url"
  }
}
```

- **`image` 必须放在 `extra_body` 里！放顶层会被当作文生图处理（走 `/t2i/` 路由）**
- 多图合成时 `extra_body.image` 传多张
- `image`: Base64 Data URI（`data:image/png;base64,<data>`）或公网 URL 数组
- **不需要 `tags: ["img2img"]`**
- 判定真假图生图：返回 URL 路径 `/t2i/`=假，`/i2i/`=真

## 关键参数速查

| 参数 | 位置 | 取值 |
|------|------|------|
| `size` | 顶层 | `1K`/`2K`/`3K`/`4K` 或 `1024x768` |
| `ratio` | 顶层 | `1:1` `3:4` `4:3` `16:9` `9:16` `2:3` `3:2` `21:9` |
| `return_base64` | 顶层 | 文生图 Base64 输出 |
| `image` | `extra_body` | string[]，图生图/多图合成必填 |
| `response_format` | `extra_body` | `url` 或 `b64_json`（**勿放顶层**）|

## 输出尺寸速查

| Ratio | 1K | 2K | 4K |
|-------|-----|-----|-----|
| 1:1 | 1024x1024 | 2048x2048 | 4096x4096 |
| 16:9 | 1312x736 | 2624x1472 | 5248x2944 |
| 9:16 | 736x1312 | 1472x2624 | 2944x5248 |

> `1920x1080` / `2560x1440` 不是原生尺寸，会被标准化。用 `size: 2K + ratio: 16:9` 得 2624x1472。

## 定价

`agnes-image-2.5-flash` 与 `2.1-flash` 价格相同，**当前全档位免费**（1K/2K/3K/4K 输出 + 输入参考图）。

## 阿里云 MaaS (Qwen Image)

### 文生图

```
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer ***

{
  "model": "qwen-image-2.0-pro",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "一只巨大的棕熊，威风凛凛地站在森林中"}
      ]
    }
  ],
  "max_tokens": 2000
}
```

### 返回

```json
{
  "output": {
    "choices": [{"message": {"content": [{"image": "https://dashscope-...aliyuncs.com/xxx.png"}]}}]
  },
  "usage": {"image_count": 1, "height": 2048, "width": 2048}
}
```

注意: 阿里云 MaaS 使用 chat/completions 端点（非 images/generations），且 content 字段必须为列表格式（多模态格式），不能是纯字符串。

## 环境变量

| 变量名 | 用途 | 存储位置 |
|--------|------|---------|
| Agnes API Key | Agnes AI 认证 | `scripts/agkes_key.txt` |
| `ALIYUN_API_KEY` | 阿里云 MaaS 认证 | `.env` 文件 |
