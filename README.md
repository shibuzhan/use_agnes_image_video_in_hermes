<p align="center">
  <img src="https://img.shields.io/badge/Agnes%20AI-2.5%20Flash-blueviolet?style=flat" alt="Agnes AI">
  <img src="https://img.shields.io/badge/status-production-green" alt="Status">
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
  <img src="https://img.shields.io/badge/Hermes-Skill-ff69b4" alt="Hermes Skill">
</p>

# use_agnes_image_video_in_hermes

> 🎨 在 **Hermes Agent** 中使用 **Agnes AI** 进行图片生成与视频生成的 Skill 配置

---

## 📦 导入方法

### 方式一：克隆到 Hermes Skills 目录

```bash
# 进入 Hermes Skills 目录（git-bash 环境）
cd /c/Users/你的用户名/AppData/Local/hermes/skills/creative/

# 克隆仓库
git clone https://github.com/shibuzhan/use_agnes_image_video_in_hermes.git agnes-image-gen
```

### 方式二：手动复制

将 `SKILL.md`、`scripts/`、`references/` 复制到：

```
C:\Users\你的用户名\AppData\Local\hermes\skills\creative\agnes-image-gen\
```

### 配置 API Key

```bash
# 在 scripts/ 下创建 key 文件
echo "sk-你的Agnes AI API密钥" > scripts/agkes_key.txt
```

> ⚠️ `agkes_key.txt` 已被 `.gitignore` 排除，不会误提交到仓库。

---

## ✨ 支持能力

| 功能 | 说明 | 模型 |
|------|------|------|
| 🖼️ **文生图** | 文本提示词 → 图片 | `agnes-image-2.5-flash` |
| 🔄 **图生图** | 参考图变换角色/风格，保留构图 | `agnes-image-2.5-flash` |
| 🧩 **多图合成** | 多张参考图组合生成新图 | `agnes-image-2.5-flash` |
| 🎬 **文生视频** | 文本提示词 → 视频 | `agnes-video-2.5-flash` |
| 🎥 **图生视频** | 静态图片 → 动态视频（首帧） | `agnes-video-2.5-flash` |
| 🖼️ **首尾帧控制** | 首帧/尾帧之间平滑过渡 | `agnes-video-2.5-flash` |
| 🎵 **参考图/音频** | 最多5张图 / 3段音频引导生成 | `agnes-video-2.5-flash` |
| ☁️ **阿里云备用** | Agnes 不可用时降级方案 | `qwen-image-2.0-pro` |

### 🆕 v3.3 更新（Agnes Video 2.5 Flash）

- 默认视频模型升级为 **`agnes-video-2.5-flash`**（720P，限时免费）
- 全新 API 参数：`mode`（text/keyframe/reference）、`seconds`、`size: "720P"`、`aspect_ratio`
- 新增 **首尾帧控制**：`--first-frame` / `--last-frame`
- 新增 **参考图/音频生成**：`--ref-image`（≤5）/ `--ref-audio`（≤3）
- 内置**队列满自动重试**（HTTP 503 `video_queue_full`）
- 本地图片自动上传换取公网 URL
- 结果 URL 改从顶层 `url` 字段读取

### 🆕 v3.2 更新（Agnes Image 2.5 Flash）

- 默认模型升级为 **`agnes-image-2.5-flash`**（生成/编辑/构图/细节/提示词遵循全面超过 2.1）
- 新增 **尺寸档位 + 宽高比** 控制：`--size 1K/2K/3K/4K` + `--ratio 16:9`
- 新增 **多图合成** 支持：`--image a.png --image b.png`
- 新增 **Base64 输出**：`--base64`
- 图片下载改为**直连优先**，失败才回退代理（实测 CDN 可直连）
- 全档位输出免费

---

## 📁 文件结构

```
agnes-image-gen/
├── SKILL.md                        # 🌟 Hermes Skill 主配置（自动加载）
├── README.md                       # 本文档
├── .gitignore
│
├── scripts/                        # ⚡ 可执行脚本
│   ├── generate.py                 # Agnes AI 文生图/图生图/多图合成
│   ├── ali_gen.py                  # 阿里云 MaaS 备用
│   └── agkes_key.txt               # 🔒 API Key（已gitignore）
│
└── references/                     # 📚 官方 API 文档
    ├── Agnes Image 2.5 Flash.md    # 🆕 最新模型完整 API
    ├── Agnes Image 2.1 Flash.md    # 旧版 API（参数一致）
    ├── Agnes Image 2.0 Flash.md    # 更旧版 API
    ├── Agnes Video 2.5 Flash.md   # 🆕 最新视频 API
    ├── Agnes Video V2.0.md         # 旧版视频 API
    ├── agnes-api.md                # 精简速查
    └── img2img-prompt-principles.md # 提示词原则
```

---

## ⚡ 快速使用

```bash
cd scripts/

# 🖼️ 文生图（默认 1K，1:1）
python generate.py "一只可爱的猫娘，二次元风格"

# 🖼️ 文生图 + 尺寸档位 + 宽高比
python generate.py "赛博朋克城市夜景" --size 2K --ratio 16:9

# 🔄 图生图（第二位置参数为参考图）
python generate.py "Takanashi Rikka cosplay, dreamy haze, motion blur" /path/to/reference.png

# 🧩 多图合成
python generate.py "combine into a fantasy battle scene" --image a.png --image b.png

# 📦 Base64 输出
python generate.py "product photo" --base64
```

### ⚙️ 图生图关键规则

```json
// ✅ 正确：image 在 extra_body 里（走 /i2i/ 路由，保留原图）
{
  "model": "agnes-image-2.5-flash",
  "prompt": "简短提示词",
  "size": "1024x768",
  "extra_body": {
    "image": ["data:image/png;base64,..."],
    "response_format": "url"
  }
}

// ❌ 错误：image 在顶层（走 /t2i/ 路由，忽略参考图）
{ "model": "...", "prompt": "...", "image": [...], "size": "..." }
```

### 📐 尺寸档位速查

| Ratio | 1K | 2K | 4K |
|-------|-----|-----|-----|
| 1:1 | 1024x1024 | 2048x2048 | 4096x4096 |
| 16:9 | 1312x736 | 2624x1472 | 5248x2944 |
| 9:16 | 736x1312 | 1472x2624 | 2944x5248 |

> `1920x1080` / `2560x1440` 不是原生尺寸，会被标准化。需要 16:9 素材时用 `--size 2K --ratio 16:9`（=2624x1472）。

### 💡 提示词原则

```
✅ "Takanashi Rikka cosplay, dreamy haze, motion blur"     ← 极简，只写角色名+效果
❌ "Change hair to long blue twin-tails, change eyepatch..." ← 逐条描述 → 模型硬生成
```

---

## 🎬 视频生成（Agnes Video 2.5 Flash）

### 三种模式

| mode | 用途 | 必需媒体 | 禁止字段 |
|------|------|---------|---------|
| `text` | 纯文本生成视频 | 无 | 所有媒体字段 |
| `keyframe` | 首尾帧控制 | `first_frame` 或 `last_frame` 至少一个 | images/audios/videos |
| `reference` | 图片/音频参考 | `images` 或 `audios` 至少一类 | first_frame/last_frame/videos |

> reference 模式：`images` ≤5 张，`audios` ≤3 段，`videos` **不支持**。

### 请求示例

```python
import requests, time

data = {
    "model": "agnes-video-2.5-flash",
    "prompt": "雨后的未来城市街道，霓虹倒映在地面，一辆银色跑车缓慢驶过，电影级运镜",
    "seconds": "5",            # 字符串 "4"-"12"
    "mode": "text",
    "size": "720P",            # Flash 固定 720P
    "aspect_ratio": "16:9"
}
resp = requests.post("https://apihub.agnes-ai.com/v1/videos",
                     headers=headers, json=data, timeout=180)
# ⚠️ 503 video_queue_full / 429 rate limit 会交替出现（详见 video-workflow.md）
vid = resp.json()["video_id"]

# 轮询（keyframe/reference 模式必须带 model_name）
while True:
    rj = requests.get(
        f"https://apihub.agnes-ai.com/agnesapi?video_id={vid}&model_name=agnes-video-2.5-flash",
        headers=headers).json()
    if rj.get("status") == "completed":
        video_url = rj.get("url")     # 2.5 的 URL 在顶层 url 字段
        break
    elif rj.get("status") == "failed":
        raise Exception("Video generation failed")
    time.sleep(2)
```

### 脚本用法

```bash
# 文生视频（默认 5秒 16:9）
python generate_video.py "夜间森林中三只猫组成铜管乐队向前行进"

# 指定时长与画幅
python generate_video.py "雨后未来城市" --seconds 8 --ratio 9:16

# 图生视频（首帧；本地图片自动上传换公网URL）
python generate_video.py "角色缓慢转身看向镜头" --first-frame photo.png

# 首尾帧控制
python generate_video.py "从首帧自然过渡到尾帧" --first-frame a.png --last-frame b.png

# 参考图生成（最多5张）
python generate_video.py "以 <Picture 1> 的角色为参考，角色在花田中奔跑" --ref-image c.png
```

### 画幅对照

| aspect_ratio | 输出像素 |
|--------------|---------|
| 21:9 | 1680x720 |
| 16:9 | 1280x704 |
| 4:3 | 960x720 |
| 1:1 | 720x720 |
| 3:4 | 720x960 |
| 9:16 | 720x1280 |

### 旧版模型（Agnes Video V2.0）

仍可用 `--model agnes-video-v2.0`，参数为 `width`/`height`/`num_frames`（`8n+1`，≤441）/
`frame_rate`（1–60），结果 URL 在 `remixed_from_video_id` 字段。

| 目标时长 | num_frames | frame_rate |
|---------|-----------|------------|
| ≈3秒 | 81 | 24 |
| ≈5秒 | 121 | 24 |
| ≈10秒 | 241 | 24 |
| ≈18秒 | 441 | 24 |

---

## 🌐 代理配置

- **API 请求**：**不走代理**（直连 `apihub.agnes-ai.com`）
- **资源下载**：**直连优先**，失败才走代理 `http://127.0.0.1:7897`
- 阿里云 MaaS 国内直连，不需要代理

---

## ❗ 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 图生图结果和原图完全无关 | `image` 放在了请求体顶层 | 放到 `extra_body` 里 |
| 返回 URL 是 `/t2i/` 而非 `/i2i/` | 被当作文生图处理 | 检查 `extra_body.image` |
| "invalid input image" | Data URI 格式错误 | 确保格式为 `data:image/png;base64,...` |
| 代理连接被重置 | API请求走了代理 | 仅下载资源时走代理 |
| 请求超时 | 生成需数秒到几十秒 | 超时设置 60s - 360s |
| API key 显示为 `***DPZN` | Hermes 自动 mask | 文件实际内容完整，不影响运行 |

---

## 📄 许可证

MIT
