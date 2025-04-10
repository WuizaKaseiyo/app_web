import json


input_path = "data_module3.json"
output_path = "data_module3.json"


with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)


for item in data:
    item["image"] = f"image/set3/{item['id']}.jpg"


with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

