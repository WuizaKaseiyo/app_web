import os
import json
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def init_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    return webdriver.Chrome(options=options)

def extract_image(url, save_path, driver):
    if os.path.exists(save_path):
        print(f"[跳过] 已存在 {save_path}")
        return True
    try:
        driver.get(url)
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        imgs = driver.find_elements("tag name", "img")
        for img in imgs:
            src = img.get_attribute("src") or img.get_attribute("data-lazy-img")
            if src and "jfs" in src:
                if src.startswith("//"):
                    src = "https:" + src
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                urllib.request.urlretrieve(src, save_path)
                print(f"[保存] {save_path}")
                return True
        print(f"[未找到图片] {url}")
    except Exception as e:
        print(f"[错误] {url} - {e}")
    return False

def process_module1_3(filepath, module_idx, group_idx, driver):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    image_dir = os.path.join("image", f"set{module_idx}", f"set{module_idx}_{group_idx}")
    for idx, item in enumerate(data):
        if "image" in item and item["image"].endswith(".html"):
            save_path = os.path.join(image_dir, f"{idx + 1}.jpg")
            success = extract_image(item["image"], save_path, driver)
            item["image"] = save_path.replace("\\", "/") if success else ""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def process_module2(filepath, module_idx, group_idx, driver):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    image_dir = os.path.join("image", f"set{module_idx}", f"set{module_idx}_{group_idx}")
    for item in data:
        for suffix in ["A", "B"]:
            key = f"image{suffix}"
            if key in item and item[key].endswith(".html"):
                save_path = os.path.join(image_dir, f"{item['id']}_{suffix}.jpg")
                success = extract_image(item[key], save_path, driver)
                item[key] = save_path.replace("\\", "/") if success else ""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def run_all():
    base_dir = "."
    driver = init_driver()
    for fname in os.listdir(base_dir):
        if fname.startswith("data_module") and fname.endswith(".json"):
            parts = fname.replace(".json", "").split("_")
            if len(parts) != 3:
                continue
            _, module_idx, group_idx = parts
            filepath = os.path.join(base_dir, fname)
            print(f"🚀 处理：{fname}")
            if module_idx == "2":
                process_module2(filepath, module_idx, group_idx, driver)
            else:
                process_module1_3(filepath, module_idx, group_idx, driver)
    driver.quit()

if __name__ == "__main__":
    run_all()
