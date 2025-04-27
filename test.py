import os
import json
import time
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0"
}

base_dir = "."  
image_root = "image"
module_defs = {
    1: ["image"],
    2: ["imageA", "imageB"],
    3: ["image"]
}


image_cache = {}

def extract_review_image_urls(jd_html_url):

    if jd_html_url in image_cache:
        return image_cache[jd_html_url]

    try:
        resp = requests.get(jd_html_url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        img_tags = soup.select(".dt-content img")

        img_urls = []
        for tag in img_tags:
            src = tag.get("src") or tag.get("data-lazy-img")
            if src and ("jfs" in src or src.startswith("//img")):
                full_url = "https:" + src if src.startswith("//") else src
                img_urls.append(full_url)

        image_cache[jd_html_url] = img_urls
        return img_urls
    except Exception as e:
        # print(f"[fail] {jd_html_url} - {e}")
        image_cache[jd_html_url] = []
        return []

def download_image(url, save_path):
    try:
        img_data = requests.get(url, headers=headers, timeout=10).content
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(img_data)
        # print(f"[success] {url} -> {save_path}")
        return True
    except Exception as e:
        # print(f"[fail] {url} - {e}")
        return False

def process_json(module_id):
    json_name = f"data_module{module_id}.json"
    json_path = os.path.join(base_dir, json_name)

    if not os.path.exists(json_path):
        # print(f"no file {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = False
    for item in data:
        for field in module_defs[module_id]:
            html_url = item.get(field, "")
            if not html_url.endswith(".html"):
                continue

            suffix = f"_{field[-1]}" if field in ("imageA", "imageB") else ""
            id_part = str(item["id"]).split("|")[0]
            save_dir = os.path.join(base_dir, image_root, f"set{module_id}")

            img_urls = extract_review_image_urls(html_url)
            if not img_urls:
                # print(f"[no image] {html_url}")
                continue

            image_list_field = f"{field}_list"
            item[image_list_field] = []

            for idx, img_url in enumerate(img_urls):
                img_name = f"{id_part}{suffix}_{idx+1}.jpg"
                save_path = os.path.join(save_dir, img_name)
                img_rel_path = os.path.relpath(save_path, base_dir).replace("\\", "/")

                if os.path.exists(save_path):
                    # print(f"[exist] {save_path}")
                else:
                    if not download_image(img_url, save_path):
                        continue

                item[image_list_field].append(img_rel_path)

            item[field] = item[image_list_field][0] if item[image_list_field] else ""
            updated = True

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run_all():
    for module_id in [1, 2, 3]:
        process_json(module_id)
        time.sleep(1)

if __name__ == "__main__":
    run_all()
