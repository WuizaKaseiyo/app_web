import os
import json
import time
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0"
}

base_dir = "."  # 当前路径
image_root = "image"
module_defs = {
    1: ["image"],  # 模块1
    2: ["imageA", "imageB"],  # 模块2
    3: ["image"]  # 模块3
}

def extract_image_url(jd_html_url):
    try:
        resp = requests.get(jd_html_url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        imgs = soup.select("img")
        for tag in imgs:
            src = tag.get("src") or tag.get("data-lazy-img")
            if src and ("jfs" in src or src.startswith("//img")):
                return "https:" + src if src.startswith("//") else src
    except Exception as e:
        print(f"[❌ 提取失败] {jd_html_url} - {e}")
    return None

def download_image(url, save_path):
    try:
        img_data = requests.get(url, headers=headers, timeout=10).content
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(img_data)
        print(f"[✅ 下载成功] {url} -> {save_path}")
        return True
    except Exception as e:
        print(f"[❌ 下载失败] {url} - {e}")
        return False

def process_json(module_id, group_id):
    json_name = f"data_module{module_id}_{group_id}.json"
    json_path = os.path.join(base_dir, json_name)

    if not os.path.exists(json_path):
        print(f"[⚠️ 跳过] 找不到文件 {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = False
    for item in data:
        for field in module_defs[module_id]:
            image_url = item.get(field, "")
            if image_url.endswith(".html"):
                suffix = f"_{field[-1]}" if field in ("imageA", "imageB") else ""
                image_id = str(item["id"]).split("|")[0]  # 用第一个id做文件名
                image_name = f"{image_id}{suffix}.jpg"
                save_dir = os.path.join(base_dir, image_root, f"set{module_id}", f"set{module_id}_{group_id}")
                save_path = os.path.join(save_dir, image_name)

                if os.path.exists(save_path):
                    print(f"[⏭ 已存在] {save_path}")
                    item[field] = os.path.relpath(save_path, base_dir).replace("\\", "/")
                    continue

                real_img_url = extract_image_url(image_url)
                if real_img_url and download_image(real_img_url, save_path):
                    item[field] = os.path.relpath(save_path, base_dir).replace("\\", "/")
                    updated = True
                else:
                    print(f"[⚠️ 提取失败] {image_url}")
    # 回写 JSON 文件
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[✔ 完成] {json_name}\n")

def run_all():
    for module_id in [1, 2, 3]:
        for group_id in [1, 2, 3]:
            process_json(module_id, group_id)
            time.sleep(1)  # 避免访问过快被封

if __name__ == "__main__":
    run_all()
