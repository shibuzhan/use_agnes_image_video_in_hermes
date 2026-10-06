# 视频生成流程与坑点

> 模型优先级：`agnes-video-2.5-flash`（最新，推荐）→ `agnes-video-v2.0`（旧版兼容）

## 一、Agnes Video 2.5 Flash（推荐）

### 流程

1. **创建视频任务**：`POST https://apihub.agnes-ai.com/v1/videos`

   ```python
   data = {
       "model": "agnes-video-2.5-flash",
       "prompt": "雨后未来城市街道，霓虹倒映地面，银色跑车缓慢驶过",
       "seconds": "5",          # 字符串 "4"-"12"
       "mode": "text",          # text / keyframe / reference
       "size": "720P",          # Flash 固定 720P
       "aspect_ratio": "16:9"
   }
   ```

2. **轮询结果**：`GET /agnesapi?video_id=<VIDEO_ID>&model_name=agnes-video-2.5-flash`
   - 建议 1–2 秒一次，直到 `status` 为 `completed` / `failed`
   - 完成后从响应**顶层 `url` 字段**取视频地址

3. **下载**：优先直连，失败回退代理 `127.0.0.1:7897`

### 三种模式

| mode | 用途 | 必需 | 禁止 |
|------|------|------|------|
| `text` | 纯文本生成 | 无 | 所有媒体字段 |
| `keyframe` | 首尾帧控制 | `first_frame` / `last_frame` 至少一个 | images/audios/videos |
| `reference` | 图片/音频参考 | `images` 或 `audios` 至少一类 | first_frame/last_frame/videos |

- reference 模式：`images` ≤5 张，`audios` ≤3 段，**`videos` 不支持**
- prompt 中用 `<Picture N>` / `<Audio N>` 指代素材
- 所有媒体 URL 必须**公网可访问**并在任务完成前保持有效

### 画幅

`size` 固定 `"720P"`，尺寸由 `aspect_ratio` 决定：

| aspect_ratio | 输出像素 |
|--------------|---------|
| 21:9 | 1680x720 |
| 16:9 | 1280x704 |
| 4:3 | 960x720 |
| 1:1 | 720x720 |
| 3:4 | 720x960 |
| 9:16 | 720x1280 |

## 二、Agnes Video V2.0（旧版）

```python
data = {
    "model": "agnes-video-v2.0",
    "prompt": "描述动作和运动",
    "image": "https://...",   # 公网URL
    "num_frames": 81,         # 8n+1, 81≈3秒
    "frame_rate": 24
}
```

- 查询：`GET /agnesapi?video_id=<VIDEO_ID>&model_name=agnes-video-v2.0`
- 结果 URL 在 `remixed_from_video_id` 字段
- 分辨率档位: 480p / 720p / 1080p

| 目标时长 | num_frames | frame_rate |
|---------|-----------|-----------|
| 约3秒 | 81 | 24 |
| 约5秒 | 121 | 24 |
| 约10秒 | 241 | 24 |
| 约18秒 | 441 | 24 |

## 坑点

### 轮询假阳性（已踩坑）
- **错误写法**：`if "completed" in str(response)` ← 会匹配到 `"completed_at": null` 里的 "completed" 导致提前退出！
- **正确写法**：`if rj.get("status") == "completed"` ← 精确匹配 status 字段
- **2.5 额外坑**：`internal_status` / `internal_progress` 是内部字段，可能一直显示 `pending` / `0`，**必须**以 `status` / `progress` 为准

### 503 与 429 交替出现 —— 重试死循环（实测踩坑，最坑的一个）
视频接口有**双重门槛**：
1. **队列容量** → HTTP 503 `{"code":"video_queue_full","message":"video queue is full, please retry later"}`
2. **免费速率限制** → HTTP 429 `{"error":{"message":"You've reached the API rate limit for free users..."}}`

**实测日志**（12 次重试，503 与 429 交替，始终没创建成功）：
```
[1] 503 video_queue_full     [2] 429 rate limit
[3] 429 rate limit           [4] 429 rate limit
[5] 503 video_queue_full     [6] 503 video_queue_full
[7] 429 rate limit           [8] 429 rate limit
[9] 503 video_queue_full     [10] 503 video_queue_full
[11] 429 rate limit          [12] 429 rate limit
→ FAILED: queue never opened
```

**死循环成因**：每次撞 503 就 retry，retry 本身消耗速率额度 → 触发 429 → 冷却后再撞 503 → 再 retry……自己把自己限流了。

**正确策略**：
- 503：最多重试 **3 次**，间隔 **30 秒**
- 429：**立即停止**，不重试。冷却需数分钟~次日；重试只会加剧限流
- 脚本 `generate_video.py` 已按此实现，遇 429 直接 `sys.exit` 并提示

**注意**：429 只影响**视频**接口。实测限流期间图片 API 完全正常（`generate.py` 照常出图成功）。

### 未经实测的部分
2.5-flash 的「轮询 → 取顶层 `url` → 下载落盘」全链路是**按官方文档实现**的，但因队列满 + 限流，本次**未能跑通验证**。首次成功使用后建议回补确认。

### 图片必须公网URL
- 视频API不接受 Data URI Base64 或本地路径
- 解决：用 `generate.py` 先生成图片拿 Agnes 平台URL，或用 `generate_video.py` 自动上传换 URL

### 本地音频无法自动上传
- reference 模式的 `audios` 必须是公网可访问的音频 URL；脚本遇到本地音频路径会直接报错提示

### video_id 与 task_id
- 创建任务响应同时含 `id` / `task_id`（任务ID）和 `video_id`（推荐查询用）
- 2.5 的 keyframe / reference 模式查询**必须**带 `model_name`；仅 `text` 模式可省略

### 创建任务可能超时
- 设置 `timeout=180` 比较稳妥

### 视频URL获取
- 2.5-flash：顶层 `url` 字段
- v2.0：`remixed_from_video_id` 字段
- 下载优先直连，失败回退代理 `127.0.0.1:7897`
