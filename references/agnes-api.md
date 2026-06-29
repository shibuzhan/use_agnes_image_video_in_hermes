# Agnes AI Image API 参考

## 基本信息

- Base URL: `https://apihub.agnes-ai.com`
- 认证: Bearer Token (Authorization header)
- 兼容性: OpenAI API 兼容
- 模型列表:
  - `agnes-image-2.1-flash`: 最新版，支持文生图和图生图，1024x1024
  - `agnes-image-2.0-flash`: 旧版，支持文生图和图生图

## 文生图

```
POST /v1/images/generations
Content-Type: application/json
Authorization: Bearer <key>

{
  "model": "agnes-image-2.1-flash",
  "prompt": "一只巨大的棕熊，威风凛凛地站在森林中，写实风格，摄影级画质",
  "n": 1,
  "size": "1024x1024"
}
```

返回:
```json
{
  "data": [{"url": "https://platform-outputs.agnes-ai.space/images/t2i/xxx.png"}]
}
```

## 图生图

```
POST /v1/images/generations
Content-Type: application/json
Authorization: Bearer <key>

{
  "model": "agnes-image-2.1-flash",
  "prompt": "Change the background from forest to a bustling city street",
  "size": "1024x1024",
  "extra_body": {
    "image": ["data:image/png;base64,..."],
    "response_format": "url"
  }
}
```

- **重要：`image` 必须放在 `extra_body` 里！放顶层会被当作文生图处理**
- `image`: Base64 Data URI 格式 `data:image/png;base64,<data>` 或公网URL数组

## 阿里云 MaaS (Qwen Image)

### 文生图

```
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer <key>

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
    "choices": [
      {
        "message": {
          "content": [
            {"image": "https://dashscope-...oss-accelerate.aliyuncs.com/xxx.png"}
          ]
        }
      }
    ]
  },
  "usage": {"image_count": 1, "height": 2048, "width": 2048}
}
```

注意: 阿里云 MaaS 使用的是 chat/completions 端点（非 images/generations），且 content 字段必须为列表格式（多模态格式），不能是纯字符串。

## 环境变量

| 变量名 | 用途 | 存储位置 |
|--------|------|---------|
| Agnes API Key | Agnes AI 认证 | `scripts/generate.py` 中硬编码 |
| `ALIYUN_API_KEY` | 阿里云 MaaS 认证 | `.env` 文件 |
