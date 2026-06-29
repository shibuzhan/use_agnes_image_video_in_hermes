import requests, json, base64, os, sys, uuid

# Read key
key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agkes_key.txt")
key = ""
if os.path.exists(key_path):
    with open(key_path) as f:
        key = f.read().strip()
if not key:
    print("ERROR: no API key found")
    sys.exit(1)

headers = {"Authorization": "Bearer " + key, "Content-Type": "application/json"}

prompt = sys.argv[1] if len(sys.argv) >= 2 else "a cute cat"
img_path = sys.argv[2] if len(sys.argv) >= 3 else None

if img_path:
    # Image-to-image: image goes INSIDE extra_body (NOT top-level!)
    # Prompt should be MINIMAL — just character + effect, not detailed description
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    data = {
        "model": "agnes-image-2.1-flash",
        "prompt": prompt,
        "size": "1024x1024",
        "extra_body": {
            "image": ["data:image/png;base64," + img_b64],
            "response_format": "url"
        }
    }
else:
    # Text-to-image
    data = {
        "model": "agnes-image-2.1-flash",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }

# API请求不走代理
resp = requests.post("https://apihub.agnes-ai.com/v1/images/generations", headers=headers, json=data, timeout=120)
result = resp.json()

if resp.status_code == 200 and "data" in result and len(result["data"]) > 0:
    img_url = result["data"][0].get("url", "")
    print("URL:", img_url)
    os.environ["http_proxy"] = "http://127.0.0.1:7897"
    os.environ["https_proxy"] = "http://127.0.0.1:7897"
    r2 = requests.get(img_url, timeout=60)
    save_dir = r"D:\Users\shi'zhan\Pictures\agnes"
    os.makedirs(save_dir, exist_ok=True)
    fname = f"img_{uuid.uuid4().hex[:8]}.png"
    save_path = os.path.join(save_dir, fname)
    with open(save_path, "wb") as f:
        f.write(r2.content)
    print("SAVED:", save_path, len(r2.content), "bytes")
    print("MEDIA:" + save_path)
else:
    print("ERROR:", json.dumps(result, ensure_ascii=False)[:500])
