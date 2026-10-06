# -*- coding: utf-8 -*-
"""Agnes AI 图像生成 — 文生图 / 图生图 / 多图合成

默认模型: agnes-image-2.5-flash (最新, 免费)

用法:
  # 文生图 (默认 1K, 1:1)
  python generate.py "提示词"

  # 文生图 + 尺寸档位 + 宽高比
  python generate.py "提示词" --size 2K --ratio 16:9

  # 文生图 + 精确尺寸 (兼容写法)
  python generate.py "提示词" --size 1024x768

  # 图生图 (位置参数, 向后兼容旧用法)
  python generate.py "提示词" reference.png

  # 图生图 (显式 flag, 支持 URL 或本地路径)
  python generate.py "提示词" --image reference.png

  # 多图合成 (多张参考图)
  python generate.py "提示词" --image a.png --image b.png

  # Base64 输出
  python generate.py "提示词" --base64

  # 指定旧模型
  python generate.py "提示词" --model agnes-image-2.1-flash

尺寸档位: 1K / 2K / 3K / 4K, 配合 --ratio (1:1, 3:4, 4:3, 16:9, 9:16, 2:3, 3:2, 21:9)
"""
import requests
import json
import base64
import os
import sys
import uuid
import argparse

EP = "https://apihub.agnes-ai.com/v1/images/generations"
DEFAULT_MODEL = "agnes-image-2.5-flash"
SAVE_DIR = r"D:\Users\shi'zhan\Pictures\agnes"
PROXY = {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}


def load_key():
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agkes_key.txt")
    if os.path.exists(key_path):
        with open(key_path) as f:
            return f.read().strip()
    return ""


def to_input_image(ref):
    """本地路径 -> Data URI Base64; http(s) URL 原样返回"""
    if ref.startswith("http://") or ref.startswith("https://"):
        return ref
    if ref.startswith("data:"):
        return ref
    with open(ref, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(ref)[1].lower().lstrip(".") or "png"
    if ext == "jpg":
        ext = "jpeg"
    return "data:image/%s;base64,%s" % (ext, b64)


def fetch_bytes(url):
    """下载图片: 直连优先, 失败再走代理"""
    try:
        r = requests.get(url, timeout=90)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
    except Exception:
        pass
    r = requests.get(url, timeout=90, proxies=PROXY)
    r.raise_for_status()
    return r.content


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("prompt")
    ap.add_argument("image_pos", nargs="?", default=None,
                    help="位置参数形式的参考图 (向后兼容)")
    ap.add_argument("--image", action="append", default=[],
                    help="参考图, 可重复; 本地路径或 URL")
    ap.add_argument("--size", default="2K",
                    help="尺寸档位 1K/2K/3K/4K 或精确尺寸 1024x768 (默认 2K)")
    ap.add_argument("--ratio", default="16:9",
                    help="宽高比, 需配合档位式 size (默认 16:9)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--base64", action="store_true", help="以 Base64 返回")
    ap.add_argument("--count", type=int, default=1)
    args = ap.parse_args()

    key = load_key()
    if not key:
        print("ERROR: no API key found")
        sys.exit(1)
    headers = {"Authorization": "Bearer " + key, "Content-Type": "application/json"}

    refs = list(args.image)
    if args.image_pos:
        refs.append(args.image_pos)

    data = {
        "model": args.model,
        "prompt": args.prompt,
        "size": args.size,
    }
    if args.ratio:
        data["ratio"] = args.ratio

    if refs:
        # 图生图 / 多图合成: image 必须在 extra_body 里!
        data["extra_body"] = {
            "image": [to_input_image(r) for r in refs],
            "response_format": "b64_json" if args.base64 else "url",
        }
    else:
        # 文生图
        if args.count > 1:
            data["n"] = args.count
        if args.base64:
            data["return_base64"] = True
        else:
            data["extra_body"] = {"response_format": "url"}

    # API 请求不走代理
    resp = requests.post(EP, headers=headers, json=data, timeout=300)
    try:
        result = resp.json()
    except Exception:
        print("ERROR: non-JSON response", resp.status_code, resp.text[:300])
        sys.exit(1)

    if resp.status_code != 200 or not result.get("data"):
        print("ERROR:", json.dumps(result, ensure_ascii=False)[:600])
        sys.exit(1)

    os.makedirs(SAVE_DIR, exist_ok=True)
    for item in result["data"]:
        url = item.get("url") or ""
        b64 = item.get("b64_json") or ""
        fname = "img_%s.png" % uuid.uuid4().hex[:8]
        save_path = os.path.join(SAVE_DIR, fname)
        if b64:
            with open(save_path, "wb") as f:
                f.write(base64.b64decode(b64))
            print("SAVED(base64):", save_path)
        elif url:
            print("URL:", url)
            content = fetch_bytes(url)
            with open(save_path, "wb") as f:
                f.write(content)
            print("SAVED:", save_path, len(content), "bytes")
        print("MEDIA:" + save_path)


if __name__ == "__main__":
    main()
