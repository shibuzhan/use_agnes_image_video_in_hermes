# -*- coding: utf-8 -*-
"""Agnes AI 视频生成 — 文生视频 / 图生视频 / 首尾帧 / 参考图 · 音频

默认模型: agnes-video-2.5-flash (最新, 720P, 免费)

用法:
  # 文生视频 (默认 5秒, 16:9)
  python generate_video.py "提示词"

  # 指定时长与画幅
  python generate_video.py "提示词" --seconds 8 --ratio 9:16

  # 图生视频 (首帧, 本地图片会自动上传为公网URL)
  python generate_video.py "提示词" --first-frame photo.png

  # 首尾帧控制
  python generate_video.py "提示词" --first-frame a.png --last-frame b.png

  # 参考图生成 (最多5张)
  python generate_video.py "以 <Picture 1> 的角色为参考，角色在奔跑" --ref-image c.png

  # 参考音频生成 (最多3段)
  python generate_video.py "以 <Audio 1> 的节奏生成夜间驾驶" --ref-audio bgm.mp3

  # 使用旧模型
  python generate_video.py "提示词" --model agnes-video-v2.0

画幅: 21:9(1680x720) 16:9(1280x704) 4:3(960x720) 1:1(720x720) 3:4(720x960) 9:16(720x1280)
"""
import requests
import json
import base64
import os
import sys
import time
import argparse

BASE = "https://apihub.agnes-ai.com"
DEFAULT_MODEL = "agnes-video-2.5-flash"
SAVE_DIR = r"D:\Users\shi'zhan\Videos\agnes"
PROXY = {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}


def load_key():
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agkes_key.txt")
    if os.path.exists(key_path):
        with open(key_path) as f:
            return f.read().strip()
    return ""


def upload_media(path, kind="image"):
    """把本地图片/音频上传到 Agnes 换取公网 URL。

    图片走 images/generations 的 'pass through' 方式；
    音频无对应端点，必须自行提供公网 URL（本地路径会报错）。
    """
    if path.startswith("http://") or path.startswith("https://"):
        return path

    if kind == "audio":
        raise SystemExit(
            "ERROR: 本地音频无法自动上传，请先提供公网可访问的音频 URL（例如用图床/OSS）")

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(path)[1].lower().lstrip(".") or "png"
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    headers = {"Authorization": "Bearer " + load_key(), "Content-Type": "application/json"}
    data = {
        "model": "agnes-image-2.5-flash",
        "prompt": "pass through, keep exact same image",
        "size": "1K",
        "extra_body": {
            "image": ["data:%s;base64,%s" % (mime, b64)],
            "response_format": "url",
        },
    }
    r = requests.post(BASE + "/v1/images/generations", headers=headers, json=data, timeout=180)
    rj = r.json()
    if r.status_code != 200 or not rj.get("data"):
        raise SystemExit("ERROR uploading media: " + json.dumps(rj, ensure_ascii=False)[:300])
    return rj["data"][0]["url"]


def fetch_bytes(url):
    try:
        r = requests.get(url, timeout=180)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
    except Exception:
        pass
    r = requests.get(url, timeout=180, proxies=PROXY)
    r.raise_for_status()
    return r.content


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--mode", default=None, help="text / keyframe / reference (自动推断)")
    ap.add_argument("--seconds", default="5", help="字符串 4-12, 默认 5")
    ap.add_argument("--ratio", default="16:9", help="画幅, 默认 16:9")
    ap.add_argument("--size", default="720P", help="2.5-flash 固定 720P")
    ap.add_argument("--first-frame", default=None)
    ap.add_argument("--last-frame", default=None)
    ap.add_argument("--ref-image", action="append", default=[], help="参考图, 可重复(最多5)")
    ap.add_argument("--ref-audio", action="append", default=[], help="参考音频URL, 可重复(最多3)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--save", default=None, help="保存路径(不含扩展名)")
    args = ap.parse_args()

    headers = {"Authorization": "Bearer " + load_key(), "Content-Type": "application/json"}
    is_v25 = args.model.startswith("agnes-video-2.5")

    # 自动推断 mode
    mode = args.mode
    if not mode:
        if args.first_frame or args.last_frame:
            mode = "keyframe"
        elif args.ref_image or args.ref_audio:
            mode = "reference"
        else:
            mode = "text"

    # ---- 新版 2.5-flash 参数 ----
    if is_v25:
        data = {
            "model": args.model,
            "prompt": args.prompt,
            "seconds": str(args.seconds),
            "mode": mode,
            "size": args.size,
            "aspect_ratio": args.ratio,
        }
        if args.seed is not None:
            data["seed"] = args.seed
        if mode == "keyframe":
            if args.first_frame:
                data["first_frame"] = upload_media(args.first_frame)
            if args.last_frame:
                data["last_frame"] = upload_media(args.last_frame)
        elif mode == "reference":
            if args.ref_image:
                data["images"] = [upload_media(p) for p in args.ref_image]
            if args.ref_audio:
                data["audios"] = [upload_media(p, kind="audio") for p in args.ref_audio]
    else:
        # ---- 旧版 v2.0 参数 (兼容) ----
        data = {
            "model": args.model,
            "prompt": args.prompt,
            "num_frames": 121,
            "frame_rate": 24,
        }
        img = args.first_frame or (args.ref_image[0] if args.ref_image else None)
        if img:
            data["image"] = upload_media(img)
        if args.seed is not None:
            data["seed"] = args.seed

    # 创建任务（队列可能满）
    #
    # ⚠️ 实测坑：503 video_queue_full 与 429 rate limit 会交替出现。
    #    如果对 503 做高频重试，重试本身会消耗速率额度并触发 429，形成死循环。
    #    因此：503 最多重试 3 次且间隔较长；429 立即退出，绝不继续敲接口。
    vid = None
    QUEUE_RETRY_MAX = 3
    QUEUE_WAIT = 30
    for attempt in range(1, QUEUE_RETRY_MAX + 1):
        r = requests.post(BASE + "/v1/videos", headers=headers, json=data, timeout=180)
        try:
            rj = r.json()
        except Exception:
            print("ERROR: non-JSON", r.status_code, r.text[:300])
            sys.exit(1)
        if r.status_code == 200 and (rj.get("video_id") or rj.get("id")):
            vid = rj.get("video_id") or rj.get("id")
            print("CREATED video_id:", vid)
            print("size:", rj.get("size"), "seconds:", rj.get("seconds"))
            break
        msg = json.dumps(rj, ensure_ascii=False)[:150]
        print("  [%d] status=%s %s" % (attempt, r.status_code, msg))

        # 429 优先判断：限流时立即停止，重试只会加剧限流
        if r.status_code == 429 or "rate limit" in msg:
            sys.exit("ERROR: 429 API rate limit (free tier)。\n"
                     "  免费额度/速率已用尽，需等待冷却(数分钟~次日)或升级 Token Plan。\n"
                     "  不要循环重试——重试会加剧限流。")

        # 队列满：只做少量、长间隔重试
        if "queue is full" in msg or r.status_code == 503:
            if attempt < QUEUE_RETRY_MAX:
                print("  queue full, waiting %ds..." % QUEUE_WAIT)
                time.sleep(QUEUE_WAIT)
            continue

        sys.exit(1)   # 其他问题直接退出

    if not vid:
        print("ERROR: video queue busy after %d attempts, try again later" % QUEUE_RETRY_MAX)
        sys.exit(1)

    # 轮询（2.5-flash 推荐带 model_name）
    print("polling...")
    video_url = None
    for i in range(120):
        time.sleep(10)
        q = "%s/agnesapi?video_id=%s" % (BASE, vid)
        if is_v25 or args.model:
            q += "&model_name=" + args.model
        rj = requests.get(q, headers=headers, timeout=60).json()
        st = rj.get("status")
        print("  [%d] status=%s progress=%s" % (i + 1, st, rj.get("progress")))
        if st == "completed":
            video_url = rj.get("url") or rj.get("remixed_from_video_id")
            break
        if st == "failed":
            print("FAILED:", json.dumps(rj, ensure_ascii=False)[:400])
            sys.exit(1)

    if not video_url:
        print("ERROR: polling timed out")
        sys.exit(1)

    print("VIDEO URL:", video_url)
    os.makedirs(SAVE_DIR, exist_ok=True)
    out = args.save or os.path.join(SAVE_DIR, "vid_%s.mp4" % vid[-8:])
    with open(out, "wb") as f:
        f.write(fetch_bytes(video_url))
    print("SAVED:", out, os.path.getsize(out), "bytes")
    print("MEDIA:" + out)


if __name__ == "__main__":
    main()
