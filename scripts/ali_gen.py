import os, requests, json, sys, uuid

# Read key from .env
env_path = r"C:\Users\shi'zhan\AppData\Local\hermes\.env"
key = None
with open(env_path, "r") as f:
    for line in f:
        line = line.strip()
        if line.startswith("ALIYUN_API_KEY=*** and not line.startswith("#"):
            key = line.split("=", 1)[1]
            break

if not key:
    print("ERROR: ALIYUN_API_KEY not found in .env")
    sys.exit(1)

prompt = sys.argv[1] if len(sys.argv) > 1 else "一只可爱的小猫"

# Generate via Aliyun MaaS
base = "https://ws-hxvuw1657mil82ij.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
headers = {"Authorization": "Bearer " + key, "Content-Type": "application/json"}
data = {
    "model": "qwen-image-2.0-pro",
    "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    "max_tokens": 2000
}
r = requests.post(base + "/chat/completions", headers=headers, json=data, timeout=120)
result = r.json()

if "output" not in result or "choices" not in result["output"]:
    print("ERROR:", json.dumps(result, ensure_ascii=False)[:500])
    sys.exit(1)

content = result["output"]["choices"][0]["message"]["content"]
if not content or "image" not in content[0]:
    print("ERROR: no image in response")
    sys.exit(1)

img_url = content[0]["image"]
print("URL:", img_url)

# Download
save_dir = r"D:\Users\shi'zhan\Pictures\agnes"
os.makedirs(save_dir, exist_ok=True)
fname = f"ali_img_{uuid.uuid4().hex[:8]}.png"
save_path = os.path.join(save_dir, fname)
r2 = requests.get(img_url, timeout=60)
with open(save_path, "wb") as f:
    f.write(r2.content)
print("SAVED:", save_path, len(r2.content), "bytes")
print("MEDIA:" + save_path)
