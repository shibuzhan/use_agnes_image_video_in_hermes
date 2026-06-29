---
name: agnes-image-gen
description: 图片生成 + 视频生成 — Agnes AI优先，阿里云MaaS备用
version: 3.1.0
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
- **代理规则**：创建API请求**不走代理**，只有下载图片资源时才走代理 `127.0.0.1:7897`

## 快速用法
```bash
cd /c/Users/"shi'zhan"/AppData/Local/hermes/skills/creative/agnes-image-gen/scripts
python generate.py "你的提示词"
```

## 图生图关键坑点（必读）
- **`image` 和 `response_format` 必须放在 `extra_body` 里！放在顶层的会被当作文生图处理！**
- 正确格式（官方文档8.5节示例）：
  ```json
  {
    "model": "agnes-image-2.1-flash",
    "prompt": "Change character while preserving original composition",
    "size": "1024x1024",
    "extra_body": {
      "image": ["data:image/png;base64,..."],
      "response_format": "url"
    }
  }
  ```
- 错误格式（放顶层）：
  ```json
  {"model": "agnes-image-2.1-flash", "prompt": "...", "image": [...], "size": "..."}
  ```
  ~~API虽然返回200，但走的是 `/t2i/` 路由，完全忽略参考图，只按提示词硬生成~~
- **判定方法**：看返回URL路径。`/t2i/` = 假图生图（文生图路由），`/i2i/` = 真图生图
- 参考图支持公网URL或Data URI Base64，两种方式都可用
- Base64 Data URI完全可行（实测55kb→73k字符、147kb→196k字符均通过）
- 如果公网URL不可达（DNS解析失败），先用代理下载图片，再转为Base64 Data URI传入
- 生成成功后，下载结果图片可能需要代理（取决于CDN是否可直连），建议先尝试无代理，失败后再重试

## 图生图提示词原则（必读）
- **提示词要极简**：只需写角色名 + 照片风格/效果即可。例如 `"Takanashi Rikka cosplay, dreamy haze, motion blur"`
- **不要详细描述角色外观**：发型、衣服、颜色等细节让模型从参考图自己提取。写太多描述会覆盖参考图，导致模型"硬生成"一张新图而非基于参考图变换
- **不要额外添加不存在的东西**：比如原图角色没有翅膀，提示词里不要写"add wings"，模型会乱加
- **生成结果和原图完全无关**：100%是因为 `image` 放在了请求体顶层，API当作文生图处理。必须放到 `extra_body` 里
- **"invalid input image"**：检查 `image` 数组里的Data URI格式是否正确（`data:image/png;base64,...`）
- **代理连接被重置（ConnectionResetError）**：API请求本身不要走代理，只有下载图片资源时才走代理
- **key被mask**：config.yaml和.env里的key都会被Hermes显示为`***`，但实际文件内容完整，脚本能正常读取
- **DNS解析失败**：国内域名（如moegirl.org.cn）可能需要代理才能访问

## 首选方案：Agnes AI（免费/额度）

- 基础URL: `https://apihub.agnes-ai.com`
- API Key 在 `scripts/agkes_key.txt`
- 注意：创建API请求不走代理，只有下载资源才走代理 `127.0.0.1:7897`

### 文生图 / 图生图

- 端点: `POST /v1/images/generations`
- 模型: `agnes-image-2.1-flash`
- 图生图: `image` 字段传 data URI base64 或公网URL（**必须在 extra_body 里**）
- 脚本: `scripts/generate.py`
- 用法: `python generate.py "提示词"` 或 `python generate.py "提示词" "图片路径"`

### 文生视频 / 图生视频

- 端点: `POST /v1/videos`
- 模型: `agnes-video-v2.0`
- 图生视频: `image` 字段传**公网可访问的图片URL**（不支持 base64 或本地路径）
  - 可以用Agnes生成的图片URL（`https://platform-outputs.agnes-ai.space/...`）直接作为输入
- 参数: 使用 `width`/`height` 而非 `size`，`num_frames` 需遵循 `8n + 1` 规则
- 响应: 创建成功后返回 `video_id` 用于轮询
- `remixed_from_video_id` 字段在 `status: completed` 时包含最终视频URL
- 限流: 每分钟1次
- 下载需要走代理

### 图生视频完整流程

```python
# 1. 创建任务
data = {
    "model": "agnes-video-v2.0",
    "prompt": "描述动作和运动",
    "image": "https://...",  # 公网可访问的图片URL
    "num_frames": 81,        # 8n+1, 81≈3秒
    "frame_rate": 24
}
resp = requests.post("https://apihub.agnes-ai.com/v1/videos", headers=headers, json=data, timeout=180)
vid = resp.json()["video_id"]

# 2. 轮询结果 - 注意：不要用 "completed" in str(response) 匹配，
#    "completed_at": null 里的"completed"会导致假阳性！
while True:
    resp = requests.get(f"https://apihub.agnes-ai.com/agnesapi?video_id={vid}&model_name=agnes-video-v2.0", headers=headers)
    rj = resp.json()
    if rj.get("status") == "completed":       # 正确匹配方式
        video_url = rj.get("remixed_from_video_id")  # 视频URL在这里
        break
```

### 常用视频参数

| 目标时长 | 参数 |
|---------|------|
| 约3秒 | num_frames: 81, frame_rate: 24 |
| 约5秒 | num_frames: 121, frame_rate: 24 |
| 约10秒 | num_frames: 241, frame_rate: 24 |

- 分辨率档位: 480p / 720p / 1080p
- 推荐宽高比: 16:9（横版）, 9:16（竖版）, 1:1（方形）

## 备用方案：阿里云MaaS（付费）

- 模型: `qwen-image-2.0-pro`，2048x2048，国内直连
- 脚本: `scripts/ali_gen.py`
- 读取 `.env` 中的 `ALIYUN_API_KEY`
- 仅在Agnes不可用时使用
