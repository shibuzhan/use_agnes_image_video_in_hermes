# use_agnes_image/vedio_in_hermes

> Hermes Agent 中使用 Agnes AI 进行图片生成和视频生成的 Skill 配置

## 功能

- **文生图** — 通过文本提示词生成图片
- **图生图** — 基于参考图变换角色/风格，保留原构图
- **文生视频** — 通过文本提示词生成视频
- **图生视频** — 基于静态图片生成动态视频

## 文件结构

```
├── SKILL.md                        # 主配置文档
├── .gitignore
├── scripts/
│   ├── generate.py                 # Agnes AI 文生图/图生图脚本
│   ├── ali_gen.py                  # 阿里云 MaaS 备用脚本
│   └── agkes_key.txt               # API Key（已忽略，不在仓库中）
└── references/
    ├── Agnes Image 2.1 Flash.md    # 官方 API 文档
    ├── Agnes Image 2.0 Flash.md    # 旧版 API 文档
    ├── Agnes Video V2.0.md         # 视频 API 文档
    ├── agnes-api.md                # 精简 API 参考
    └── img2img-prompt-principles.md # 图生图提示词原则
```

## 重要要求

| 项目 | 说明 |
|------|------|
| API | `https://apihub.agnes-ai.com` |
| 图生图模型 | `agnes-image-2.1-flash` |
| 视频模型 | `agnes-video-v2.0` |
| 图生图参数位置 | `image` 必须在 `extra_body` 内（**不在顶层**），否则API走 `/t2i/` 路由忽略参考图 |
| 提示词原则 | 极简：只写角色名 + 效果，不逐条描述外观 |
| 代理 | API请求不走代理，只有下载资源走 `127.0.0.1:7897` |
| 视频查询 | 用 `video_id` 通过 `/agnesapi?video_id=` 轮询，`remixed_from_video_id` 字段取视频URL |

## 快速使用

```bash
# 文生图
cd scripts
python generate.py "一只可爱的小猫"

# 图生图（第二参数为图片路径）
python generate.py "Takanashi Rikka cosplay, dreamy haze" /path/to/image.png
```

## 视频生成

```python
import requests

data = {
    "model": "agnes-video-v2.0",
    "prompt": "描述动作",
    "image": "https://...",       # 公网可访问的图片URL
    "num_frames": 81,             # 8n+1, 81≈3秒
    "frame_rate": 24
}
resp = requests.post("https://apihub.agnes-ai.com/v1/videos", headers=headers, json=data, timeout=180)
vid = resp.json()["video_id"]

# 轮询结果
while True:
    resp = requests.get(f"https://apihub.agnes-ai.com/agnesapi?video_id={vid}&model_name=agnes-video-v2.0", headers=headers)
    rj = resp.json()
    if rj.get("status") == "completed":
        video_url = rj.get("remixed_from_video_id")
        break
```

## 备用方案

阿里云 MaaS (`qwen-image-2.0-pro`)，2048x2048，国内直连，仅在 Agnes 不可用时使用。
