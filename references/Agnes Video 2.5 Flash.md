# Agnes Video 2.5 Flash

使用 OpenAI Videos 兼容 API 接入 Agnes Video 2.5 Flash，支持**文生视频**、**首尾帧控制**和**图片/音频参考生成**。

复用 Agnes Video 2.5 的模型能力和异步任务接口；除本页列出的 Flash 专属限制外，其他请求参数、响应字段和查询方式均与 Agnes Video 2.5 一致。

- **模型 ID**: `agnes-video-2.5-flash`
- **创建任务**: `POST https://apihub.agnes-ai.com/v1/videos`
- **查询任务**: `GET https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>&model_name=agnes-video-2.5-flash`
- **当前价格**: 原价 $0.025 / 秒，现价 **$0 / 秒**（限时免费）

## 与 Agnes Video 2.5 的差异（Flash 规则）

| 校验项 | Flash 规则 | 校验失败响应 |
|--------|-----------|-------------|
| `size` | 仅支持字符串 `"720P"` | HTTP 400: `size must be 720P` |
| reference 图片数量 | `images` 最多 5 张 | HTTP 400: `images length must not exceed 5` |
| reference 音频数量 | `audios` 最多 3 段 | HTTP 400: `audios length must not exceed 3` |
| reference 视频输入 | 不支持有效的 `videos` 内容 | HTTP 400: `videos is not supported` |

Flash 专属校验在任务创建、排队、计费和推理前执行。校验失败的请求不会创建视频任务，也不会产生费用。

## 快速接入

### 1. 环境变量

```bash
export AGNES_API_KEY="***"
export AGNES_BASE_URL="https://apihub.agnes-ai.com/v1"
```

### 2. 创建视频任务

```bash
curl -sS -X POST "$AGNES_BASE_URL/videos" \
  -H "Authorization: Bearer *** "Content-Type: application/json" \
  -d '{
    "model": "agnes-video-2.5-flash",
    "prompt": "雨后的未来城市街道，霓虹灯倒映在地面，一辆银色跑车缓慢驶过，电影级运镜",
    "seconds": "5",
    "mode": "text",
    "size": "720P",
    "aspect_ratio": "16:9"
  }'
```

创建成功后保存响应中的 `video_id`（`id` / `task_id` 是任务 ID，`video_id` 用于查询任务）。

### 3. 查询任务结果

**推荐方式：`video_id` + `model_name`**（适用于 text / keyframe / reference 全部模式）

```bash
curl -sS "https://apihub.agnes-ai.com/agnesapi?video_id=VIDEO_ID&model_name=agnes-video-2.5-flash" \
  -H "Authorization: Bearer ***
```

**仅 `video_id`**（仅适用于 `mode: "text"`；keyframe / reference 模式必须带 `model_name`）

- 建议每隔 1–2 秒查询一次，直至 `status` 变为 `completed` 或 `failed`
- `status` 为 `completed` 时，从响应的**顶层 `url` 字段**获取视频地址
- `internal_status` / `internal_progress` 是内部字段，即使仍为 `pending` / `0`，也应以 `status` 和 `progress` 为准

任务完成响应示例：

```json
{
  "completed_at": 1790062857,
  "created_at": 1790062812,
  "error": null,
  "id": "task_YOUR_TASK_ID",
  "progress": 100,
  "seconds": "4",
  "size": "720P",
  "status": "completed",
  "url": "https://example.com/generated/video.mp4"
}
```

## 请求参数

### 公共参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 使用 `agnes-video-2.5-flash` |
| `prompt` | string | 是 | 视频内容描述。Reference 模式可用 `<Picture N>` 和 `<Audio N>` 指代素材 |
| `mode` | string | 是 | `text`、`keyframe` 或 `reference` |
| `seconds` | string | 否 | 视频时长，字符串 `"4"`–`"12"`，默认 `"5"` |
| `size` | string | 否 | Flash 固定为 `"720P"`；其他值返回 HTTP 400 |
| `aspect_ratio` | string | 否 | 默认 `16:9` |
| `seed` | integer | 否 | 随机种子 |
| `n` | integer | 否 | 当前仅支持 1，默认 1 |

### 模式专用参数

| 参数 | 类型 | 适用模式 | 说明 |
|------|------|---------|------|
| `first_frame` | string | keyframe | 首帧图片 URL；与 `last_frame` 至少提供一个 |
| `last_frame` | string | keyframe | 尾帧图片 URL；与 `first_frame` 至少提供一个 |
| `images` | string[] | reference | 参考图片 URL 列表，Flash 最多 5 张 |
| `audios` | string[] | reference | 参考音频 URL 列表，Flash 最多 3 段 |
| `videos` | object[] | reference | Flash 不支持；传入有效内容返回 HTTP 400 |

### 生成模式规则

| mode | 用途 | 必需媒体 | 不允许的媒体字段 |
|------|------|---------|-----------------|
| `text` | 纯文本生成视频 | 无 | first_frame、last_frame、images、audios、videos |
| `keyframe` | 首帧、尾帧或首尾帧控制 | first_frame 与 last_frame 至少一个 | images、audios、videos |
| `reference` | 图片或音频参考生成 | images 或 audios 至少一类非空 | first_frame、last_frame、videos |

- reference 模式下 `images` 与 `audios` 可单独或同时使用；图片 ≤5 张，音频 ≤3 段
- 所有媒体 URL 都需可被 Agnes AI 服务**公开访问**，并在任务完成前保持有效

## 请求示例

### 文生视频

```json
{
  "model": "agnes-video-2.5-flash",
  "prompt": "夜晚森林中三只猫组成微型铜管乐队向前行进，镜头平稳后退，月光穿过树叶",
  "seconds": "5",
  "mode": "text",
  "size": "720P",
  "aspect_ratio": "16:9"
}
```

### 首尾帧控制（keyframe）

```json
{
  "model": "agnes-video-2.5-flash",
  "prompt": "人物从首帧姿态自然转身走向窗边，镜头缓慢推进并平滑过渡到尾帧",
  "seconds": "5",
  "mode": "keyframe",
  "size": "720P",
  "first_frame": "https://example.com/first.png",
  "last_frame": "https://example.com/last.png"
}
```

### 图片参考（reference）

```json
{
  "model": "agnes-video-2.5-flash",
  "prompt": "以 <Picture 1> 中的角色和美术风格为参考，角色在花田中自然奔跑，保持外观一致",
  "seconds": "5",
  "mode": "reference",
  "size": "720P",
  "aspect_ratio": "16:9",
  "images": ["https://example.com/character.png"]
}
```

### 音频参考（reference）

```json
{
  "model": "agnes-video-2.5-flash",
  "prompt": "以 <Audio 1> 的节奏和环境氛围作为参考，生成电影感夜间驾驶画面",
  "seconds": "5",
  "mode": "reference",
  "size": "720P",
  "aspect_ratio": "16:9",
  "audios": ["https://example.com/reference-audio.mp3"]
}
```

## 视频尺寸与画幅

`size` 必须使用 `"720P"`。具体输出尺寸通过 `aspect_ratio` 选择：

| aspect_ratio | 输出像素 |
|--------------|---------|
| 21:9 | 1680x720 |
| 16:9 | 1280x704 |
| 4:3 | 960x720 |
| 1:1 | 720x720 |
| 3:4 | 720x960 |
| 9:16 | 720x1280 |

> 16:9 的输出尺寸以实际生成文件为准。2026 年 9 月实测 720P 输出为 **1280x704**。

## Flash 专属错误

同一次请求存在多个 Flash 参数错误时，按 `size` → `images` → `audios` → `videos` 顺序返回首个检测到的错误。以上响应 HTTP 状态码均为 400。

```json
{"detail": "size must be 720P"}
{"detail": "images length must not exceed 5"}
{"detail": "audios length must not exceed 3"}
{"detail": "videos is not supported"}
```

其他错误码、任务响应字段和失败任务格式与 Agnes Video 2.5 一致。

## 接入检查清单

- 模型 ID 使用 `agnes-video-2.5-flash`
- `size` 固定为字符串 `"720P"`
- `mode=reference` 时，`images` ≤5 张、`audios` ≤3 段
- `mode=reference` 时不要传入有效的 `videos` 内容
- `seconds` 使用字符串 `"4"`–`"12"`，`n` 固定为 1
- 所有模式推荐使用 `video_id` + `model_name=agnes-video-2.5-flash` 查询；不带 `model_name` 的纯 `video_id` 查询仅适用于 `mode: "text"`
- 不要在前端代码、日志或公开仓库中暴露 API Key

## 计费规则

采用与 Agnes Video 2.5 相同的计费公式，**当前限时免费**。

```
视频总金额 = 输出秒数 × 输出分辨率单价
           + 输入视频秒数 × 输出分辨率单价
           + max(0, 图片数 - 免费图片张数) × 图片超额单价
```

按刊例价计算时，免费图片张数为 5 张。

| 输出分辨率 | 原价 | 现价 |
|-----------|------|------|
| 720P | $0.025 / 秒 | $0 / 秒 |

---
来源：https://www.agnes-ai.com/zh-Hans/docs/agnes-video-25-flash
