---
name: agnes-image-gen
description: 图片生成 + 视频生成 — Agnes AI优先（agnes-image-2.5-flash），阿里云MaaS备用；生成后必须用 vision_analyze 读图再汇报
version: 3.3.0
platforms: [qq]
trigger: 用户要求生成图片/画图/作图/编辑图片/生成视频时
metadata:
  hermes:
    tags: [image, image-generation, image-edit, video, agnes, aliyun, creative]
    category: creative
---

## 重要提醒
- **脚本和key都在skill目录下**：`scripts/generate.py`、`scripts/ali_gen.py`、`scripts/agkes_key.txt`
- **路径是skill内置的**：脚本内部用 `os.path.join(os.path.dirname(os.path.abspath(__file__)), "agkes_key.txt")` 自动找key，不需要手动传递key路径
- **运行命令**：`cd <skill_dir>/scripts && python generate.py "提示词"` （用skill目录下的scripts，不是根scripts目录）
- **key显示问题**：Hermes会自动mask key（显示为`***DPZN`），但文件内容是完整的，不影响脚本运行
- **图片保存位置**：`D:\Users\shi'zhan\Pictures\agnes\`，文件名格式 `img_<uuid>.png`
- **输出包含MEDIA路径**：脚本最后会打印 `MEDIA:<save_path>`，可直接用于发送图片
- **代理规则**：创建API请求**不走代理**；下载图片资源**优先直连**，失败才回退代理 `127.0.0.1:7897`
- **生成后必须读图**：拿到 `MEDIA:<path>` 后先 `vision_analyze` 看实际画面，再按看到的内容汇报（见"生成后自动读图"章节）

## 快速用法
```bash
cd /c/Users/"shi'zhan"/AppData/Local/hermes/skills/creative/agnes-image-gen/scripts

# 文生图（默认 1K，1:1）
python generate.py "你的提示词"

# 文生图 + 尺寸档位 + 宽高比
python generate.py "你的提示词" --size 2K --ratio 16:9

# 图生图（第二位置参数为参考图，向后兼容旧用法）
python generate.py "你的提示词" reference.png

# 图生图 / 多图合成（显式 flag，本地路径或 URL，可重复）
python generate.py "你的提示词" --image a.png --image b.png

# Base64 输出
python generate.py "你的提示词" --base64

# 指定旧模型
python generate.py "你的提示词" --model agnes-image-2.1-flash
```

## 生成后自动读图（必做）

**生成成功 ≠ 画对了。** 脚本只返回一个文件路径，看不到画面内容；不读图就直接汇报，等于盲报（实测踩过：把一张跑偏的图当成"画好了"发给用户）。

流程固定为三步：

```
1. 运行 generate.py            → 得到 MEDIA:<path>
2. vision_analyze(<path>)      → 看实际画面
3. 按看到的内容汇报 + 发 MEDIA
```

### 检查清单

调用 `vision_analyze` 时按提示词逐项核对，**用一句话问清**：

| 检查项 | 说明 |
|--------|------|
| 主体数量 | 提示词要"五位少女"就必须数得出 5 个 |
| 关键元素 | 提示词点名的道具/场景/动作是否真的出现 |
| 明显崩坏 | 多手多脚、五官错位、文字乱码、结构扭曲 |
| 风格 | 是否落在要求的画风里（如"京阿尼风格"）|

### 汇报规则

- **只描述实际看到的内容**，不要把提示词改写成"完成情况"复述给用户
- 发现跑偏/崩坏 → **主动说出来**（哪一项不符），并问是否需要重画，不要藏
- 读图失败（vision 报错）→ 明确告知"图生成好了但没能自动读图"，附路径；**绝不编造画面描述**
- 尺寸/分辨率之类的硬指标可以直接从文件读取，不必依赖视觉模型

### 配置前提

- 视觉走 `auxiliary.vision`（当前 = `provider: deepseek` / `model: deepseek-flash`），**与主对话模型共用额度**，不再消耗阿里云 MaaS 计费额度
- 该配置**在会话启动时读取**，改完必须重启网关才生效；改完先实测一张图确认，再看 `success: true`
- 若 `auxiliary.vision.model` 与实际 provider 不匹配，报错形如 `The supported API model names are ..., but you passed <旧模型名>` —— 说明配置未生效（多半是没重启）

### 视频同理

视频没有直接的视觉通道：先用 `ffmpeg -ss <秒> -i out.mp4 -frames:v 1 frame.png` 抽 1–2 帧，再对帧图 `vision_analyze`，确认画面与提示词一致后再发。

## 首选方案：Agnes AI（免费/额度）

- 基础URL: `https://apihub.agnes-ai.com`
- API Key 在 `scripts/agkes_key.txt`
- 注意：创建API请求不走代理，只有下载资源失败时才回退代理 `127.0.0.1:7897`

### 模型选择

| 模型 | 状态 | 说明 |
|------|------|------|
| `agnes-image-2.5-flash` | **默认（最新）** | 生成/编辑/构图/细节/提示词遵循全面超过 2.1；支持多图合成 |
| `agnes-image-2.1-flash` | 旧版 | 接入参数与 2.5 完全一致，可随时切回 |

### 文生图 / 图生图 / 多图合成

- 端点: `POST /v1/images/generations`
- 模型: `agnes-image-2.5-flash`
- 参数说明：
  - `size`（必填）：尺寸档位 `1K`/`2K`/`3K`/`4K`；也兼容 `1024x768` 精确写法
  - `ratio`（可选）：配合档位式 size，支持 `1:1`/`3:4`/`4:3`/`16:9`/`9:16`/`2:3`/`3:2`/`21:9`，默认 `1:1`
  - `image`（图生图/多图合成必填）：**必须放在 `extra_body.image` 里**
  - `return_base64: true`：文生图 Base64 输出
  - `extra_body.response_format`：`url` 或 `b64_json`
- 脚本: `scripts/generate.py`（文生图/图生图/多图合成）, `scripts/generate_video.py`（图生视频）

### 尺寸档位表（用 --size 档位 + --ratio，输出可预期）

| Ratio | 1K | 2K | 3K | 4K |
|-------|-----|-----|-----|-----|
| 1:1 | 1024x1024 | 2048x2048 | 3072x3072 | 4096x4096 |
| 16:9 | 1312x736 | 2624x1472 | 3936x2208 | 5248x2944 |
| 9:16 | 736x1312 | 1472x2624 | 2208x3936 | 2944x5248 |
| 4:3 | 1152x864 | 2304x1728 | 3456x2592 | 4608x3456 |
| 3:4 | 864x1152 | 1728x2304 | 2592x3456 | 3456x4608 |

> 1920x1080 / 2560x1440 等精确尺寸**不是原生输出**，会被标准化到最近档位。需要 16:9 素材时用 `size: 2K + ratio: 16:9`（=2624x1472）再裁剪。

## 图生图关键坑点（必读）
- **`image` 和 `response_format` 必须放在 `extra_body` 里！放在顶层的会被当作文生图处理！**
- 正确格式（官方文档示例）：
  ```json
  {
    "model": "agnes-image-2.5-flash",
    "prompt": "Change character while preserving original composition",
    "size": "1024x768",
    "extra_body": {
      "image": ["data:image/png;base64,..."],
      "response_format": "url"
    }
  }
  ```
- 错误格式（放顶层）：
  ```json
  {"model": "agnes-image-2.5-flash", "prompt": "...", "image": [...], "size": "..."}
  ```
  ~~API虽然返回200，但走的是 `/t2i/` 路由，完全忽略参考图，只按提示词硬生成~~
- **判定方法**：看返回URL路径。`/t2i/` = 假图生图（文生图路由），`/i2i/` = 真图生图
- **图生图不需要 `tags: ["img2img"]`**（2.5 文档明确说明）
- 参考图支持公网URL或Data URI Base64，两种方式都可用
- Base64 Data URI完全可行（实测55kb→73k字符、147kb→196k字符均通过）
- 如果公网URL不可达（DNS解析失败），先用代理下载图片，再转为Base64 Data URI传入
- 生成成功后，下载结果图片**优先尝试直连**（实测直连可用），失败后再走代理 `127.0.0.1:7897`

## 图生图提示词原则（必读）
- **提示词要极简**：只需写角色名 + 照片风格/效果即可。例如 `"Takanashi Rikka cosplay, dreamy haze, motion blur"`
- **不要详细描述角色外观**：发型、衣服、颜色等细节让模型从参考图自己提取。写太多描述会覆盖参考图，导致模型"硬生成"一张新图而非基于参考图变换
- **不要额外添加不存在的东西**：比如原图角色没有翅膀，提示词里不要写"add wings"，模型会乱加
- **生成结果和原图完全无关**：100%是因为 `image` 放在了请求体顶层，API当作文生图处理。必须放到 `extra_body` 里
- **多图合成**：在 `extra_body.image` 里传多张图，提示词说明每张图的角色和组合方式
- **"invalid input image"**：检查 `image` 数组里的Data URI格式是否正确（`data:image/png;base64,...`）
- **代理连接被重置（ConnectionResetError）**：API请求本身不要走代理，只有下载图片资源时才走代理
- **key被mask**：config.yaml和.env里的key都会被Hermes显示为`***`，但实际文件内容完整，脚本能正常读取
- **DNS解析失败**：国内域名（如moegirl.org.cn）可能需要代理才能访问

## 视频生成

### 模型选择

| 模型 | 状态 | 说明 |
|------|------|------|
| `agnes-video-2.5-flash` | **默认（最新）** | 720P 固定；支持 text / keyframe / reference 三种模式；当前免费 |
| `agnes-video-v2.0` | 旧版 | 用 `width`/`height`/`num_frames` 参数，见下方旧版说明 |

### Agnes Video 2.5 Flash（推荐）

- 端点: `POST /v1/videos`
- 查询: `GET /agnesapi?video_id=<VIDEO_ID>&model_name=agnes-video-2.5-flash`
  - **keyframe / reference 模式必须带 `model_name`**；仅 `mode: "text"` 可省略
- 结果 URL 在响应**顶层 `url` 字段**（不是 `remixed_from_video_id`）

**公共参数**

| 参数 | 必填 | 说明 |
|------|------|------|
| `model` | 是 | `agnes-video-2.5-flash` |
| `prompt` | 是 | 内容描述；reference 模式可用 `<Picture N>` / `<Audio N>` 指代素材 |
| `mode` | 是 | `text` / `keyframe` / `reference` |
| `seconds` | 否 | 字符串 `"4"`–`"12"`，默认 `"5"` |
| `size` | 否 | Flash **固定 `"720P"`**，其他值报 HTTP 400 |
| `aspect_ratio` | 否 | 默认 `16:9` |
| `seed` / `n` | 否 | n 仅支持 1 |

**模式专用参数**

| 参数 | 适用模式 | 说明 |
|------|---------|------|
| `first_frame` / `last_frame` | keyframe | 首尾帧图片 URL，至少提供一个 |
| `images` | reference | 参考图 URL 列表，Flash **最多 5 张** |
| `audios` | reference | 参考音频 URL 列表，Flash **最多 3 段** |
| `videos` | reference | Flash **不支持**，传入报 400 |

**模式规则**

| mode | 用途 | 必需媒体 | 禁止字段 |
|------|------|---------|---------|
| `text` | 纯文本生成 | 无 | first_frame/last_frame/images/audios/videos |
| `keyframe` | 首尾帧控制 | first_frame 或 last_frame 至少一个 | images/audios/videos |
| `reference` | 图片/音频参考 | images 或 audios 至少一类 | first_frame/last_frame/videos |

**画幅对照**

| aspect_ratio | 输出像素 |
|--------------|---------|
| 21:9 | 1680x720 |
| 16:9 | 1280x704 |
| 4:3 | 960x720 |
| 1:1 | 720x720 |
| 3:4 | 720x960 |
| 9:16 | 720x1280 |

**脚本用法**

```bash
# 文生视频（默认 5秒 16:9）
python generate_video.py "夜间森林中三只猫组成铜管乐队向前行进"

# 指定时长与画幅
python generate_video.py "雨后未来城市，银色跑车缓慢驶过" --seconds 8 --ratio 9:16

# 图生视频（首帧；本地图片自动上传换公网URL）
python generate_video.py "角色缓慢转身看向镜头" --first-frame photo.png

# 首尾帧控制
python generate_video.py "从首帧自然过渡到尾帧" --first-frame a.png --last-frame b.png

# 参考图生成（最多5张）
python generate_video.py "以 <Picture 1> 的角色为参考，角色在花田中奔跑" --ref-image c.png
```

**关键坑点**
- **503 与 429 会交替出现（实测死循环坑）**：视频接口有**双重门槛** —— 队列容量(503 `video_queue_full`) + 免费速率限制(429 `rate limit`)。对 503 做高频重试时，重试本身消耗速率额度并触发 429，下一轮又撞 503，形成死循环（实测 12 次重试里 503/429 交替出现，始终没创建成功）。
  - **正确策略**：503 最多重试 3 次、间隔 30s；**429 必须立即停止**，冷却需数分钟~次日，绝不循环敲接口
  - 脚本 `generate_video.py` 已实现该策略
- **429 只影响视频接口**：限流期间图片 API 完全正常（实测图片生成照常成功）
- **`internal_status` / `internal_progress` 是内部字段**，即使显示 `pending`/`0`，也应以 `status`/`progress` 为准
- **不要用 `"completed" in str(response)` 匹配状态** — `completed_at: null` 会造成假阳性
- **本地音频无法自动上传**，reference 模式的音频必须自行提供公网 URL
- 轮询间隔建议 1–2 秒（脚本用 10 秒，节省额度）
- 下载视频走代理 `127.0.0.1:7897`
- **未经实测**：2.5-flash 的轮询→取 `url`→下载全链路按官方文档实现，但因队列满/限流未能跑通验证

### Agnes Video V2.0（旧版兼容）

- 端点: `POST /v1/videos`
- 模型: `agnes-video-v2.0`
- 参数: 使用 `width`/`height` 而非 `size`；`num_frames` 需遵循 `8n + 1` 规则（≤441）；`frame_rate` 1–60
- 图生视频: `image` 字段传**公网可访问的图片URL**（不支持 base64 或本地路径）
- 查询: `GET /agnesapi?video_id=<VIDEO_ID>&model_name=agnes-video-v2.0` 或 `GET /v1/videos/<TASK_ID>`
- 结果 URL 在 `remixed_from_video_id` 字段（`status: completed` 时）
- 分辨率档位: 480p / 720p / 1080p；推荐宽高比 16:9 / 9:16 / 1:1

| 目标时长 | 参数 |
|---------|------|
| 约3秒 | num_frames: 81, frame_rate: 24 |
| 约5秒 | num_frames: 121, frame_rate: 24 |
| 约10秒 | num_frames: 241, frame_rate: 24 |
| 约18秒 | num_frames: 441, frame_rate: 24 |

```python
data = {
    "model": "agnes-video-v2.0",
    "prompt": "描述动作和运动",
    "image": "https://...",  # 公网可访问的图片URL
    "num_frames": 81,
    "frame_rate": 24
}
```

详见 `references/video-workflow.md`、`references/Agnes Video V2.0.md`

## 备用方案：阿里云MaaS（付费）

- 模型: `qwen-image-2.0-pro`，2048x2048，国内直连
- 脚本: `scripts/ali_gen.py`
- 读取 `.env` 中的 `ALIYUN_API_KEY`
- 仅在Agnes不可用时使用

## 参考文档
- `references/Agnes Image 2.5 Flash.md` — 最新模型完整 API（推荐）
- `references/Agnes Image 2.1 Flash.md` — 旧版（参数一致）
- `references/agnes-api.md` — 精简速查
- `references/img2img-prompt-principles.md` — 图生图提示词原则
- `references/video-workflow.md` — 视频生成流程
