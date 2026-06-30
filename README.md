<p align="center">
  <img src="https://img.shields.io/badge/Agnes%20AI-2.1%20Flash-blueviolet?style=flat" alt="Agnes AI">
  <img src="https://img.shields.io/badge/status-production-green" alt="Status">
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
  <img src="https://img.shields.io/badge/Hermes-Skill-ff69b4" alt="Hermes Skill">
</p>

# use_agnes_image_video_in_hermes

> 🎨 在 **Hermes Agent** 中使用 **Agnes AI** 进行图片生成与视频生成的 Skill 配置

## 📦 导入方法

### 方式一：直接克隆到 Hermes Skills 目录

```bash
# 进入 Hermes Skills 目录
cd ~/AppData/Local/hermes/skills/creative/

# 克隆仓库
git clone https://github.com/shibuzhan/use_agnes_image_video_in_hermes.git agnes-image-gen

# 配置 API Key
echo "sk-你的API密钥" > agnes-image-gen/scripts/agkes_key.txt
```

### 方式二：使用 Hermes Skill Hub（若已配置）

```bash
hermes skill install shibuzhan/use_agnes_image_video_in_hermes
```

### 方式三：手动复制

直接将 `SKILL.md`、`scripts/`、`references/` 复制到 `~/AppData/Local/hermes/skills/creative/agnes-image-gen/` 下。

### 配置 API Key

```bash
# 在 skill 目录的 scripts/ 下创建 key 文件
echo "sk-你的Agnes AI API密钥" > scripts/agkes_key.txt
```

> ⚠️ `agkes_key.txt` 已被 `.gitignore` 排除，不会误提交到仓库。

---

## ✨ 支持能力

| 功能 | 说明 | 模型 |
|------|------|------|
| 🖼️ **文生图** | 文本提示词 → 图片 | `agnes-image-2.1-flash` |
| 🔄 **图生图** | 参考图变换角色/风格，保留构图 | `agnes-image-2.1-flash` |
| 🎬 **文生视频** | 文本提示词 → 视频 | `agnes-video-v2.0` |
| 🎥 **图生视频** | 静态图片 → 动态视频 | `agnes-video-v2.0` |
| ☁️ **阿里云备用** | Agnes 不可用时降级方案 | `qwen-image-2.0-pro` |

---

## 📁 文件结构

```
agnes-image-gen/
├── SKILL.md                        # 🌟 Hermes Skill 主配置（自动加载）
├── README.md                       # 本文档
├── .gitignore
│
├── scripts/                        # ⚡ 可执行脚本
│   ├── generate.py                 # Agnes AI 文生图/图生图
│   ├── ali_gen.py                  # 阿里云 MaaS 备用
│   └── agkes_key.txt               # 🔒 API Key（已gitignore）
│
└── references/                     # 📚 官方 API 文档
    ├── Agnes Image 2.1 Flash.md    # 图生图/文生图 API
    ├── Agnes Image 2.0 Flash.md    # 旧版 API
    ├── Agnes Video V2.0.md         # 视频生成 API
    ├── agnes-api.md                # 精简速查
    └── img2img-prompt-principles.md # 提示词原则
```

---

## ⚡ 快速使用

```bash
cd scripts/

# 🖼️ 文生图
python generate.py "一只可爱的猫娘，二次元风格"

# 🔄 图生图（第二参数为图片路径）
python generate.py "Takanashi Rikka cosplay, dreamy haze, motion blur" /path/to/reference.png
```

### ⚙️ 图生图关键规则

```json
// ✅ 正确：image 在 extra_body 里（走 /i2i/ 路由，保留原图）
{
  "model": "agnes-image-2.1-flash",
  "prompt": "简短提示词",
  "size": "1024x1024",
  "extra_body": {
    "image": ["data:image/png;base64,..."],
    "response_format": "url"
  }
}

// ❌ 错误：image 在顶层（走 /t2i/ 路由，忽略参考图）
{ "model": "...", "prompt": "...", "image": [...], "size": "..." }
```

### 💡 提示词原则

```
✅ "Takanashi Rikka cosplay, dreamy haze, motion blur"     ← 极简，只写角色名+效果
❌ "Change hair to long blue twin-tails, change eyepatch..." ← 逐条描述 → 模型硬生成
```

---

## 🎬 视频生成

### 图生视频

```python
import requests

data = {
    "model": "agnes-video-v2.0",
    "prompt": "The character gently looks around, subtle breathing motion",
    "image": "https://...",           # 需要公网可访问的图片URL
    "num_frames": 81,                 # 8n+1, 81 ≈ 3秒
    "frame_rate": 24
}
resp = requests.post(
    "https://apihub.agnes-ai.com/v1/videos",
    headers=headers, json=data, timeout=180
)
vid = resp.json()["video_id"]

# 轮询结果
while True:
    resp = requests.get(
        f"https://apihub.agnes-ai.com/agnesapi?video_id={vid}&model_name=agnes-video-v2.0",
        headers=headers
    )
    rj = resp.json()
    if rj.get("status") == "completed":
        video_url = rj.get("remixed_from_video_id")    # 视频URL在此字段
        # 下载视频
        import requests as r2
        with open("output.mp4", "wb") as f:
            f.write(r2.get(video_url).content)
        break
```

### 视频时长参考

| 目标时长 | num_frames | frame_rate |
|---------|-----------|------------|
| ≈3秒 | 81 | 24 |
| ≈5秒 | 121 | 24 |
| ≈10秒 | 241 | 24 |
| ≈18秒 | 441 | 24 |

> `num_frames` 必须遵循 `8n + 1` 规则。分辨率支持 480p / 720p / 1080p。

---

## 🌐 代理配置

- **API 请求**：**不走代理**（直连 `apihub.agnes-ai.com`）
- **资源下载**：走代理 `http://127.0.0.1:7897`
- 阿里云 MaaS 国内直连，不需要代理

---

## ❗ 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 图生图结果和原图完全无关 | `image`放在了请求体顶层 | 放到 `extra_body` 里 |
| "invalid input image" | Data URI 格式错误 | 确保格式为 `data:image/png;base64,...` |
| 代理连接被重置 | API请求走了代理 | 仅下载资源时走代理 |
| API key 显示为 `***DPZN` | Hermes自动mask | 文件实际内容完整，不影响运行 |

---

## 📄 许可证

MIT
