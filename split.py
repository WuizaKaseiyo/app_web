import pandas as pd
import os
import json


excel_path = "用研_评价抽样_20250403(1).xlsx"
output_dir = "."
group_counts = {
    1: (10, 3),  # 模块1：每组10条，共3组
    2: (1, 3),   # 模块2：每组1条对比，共3组
    3: (5, 3)    # 模块3：每组5条，共3组
}


df = pd.read_excel(excel_path)


df = df[df["模块"].isin([1, 2, 3])]
df = df.dropna(subset=["评价ID", "文本A", "图片链接A（html）"])


module_data = {1: [], 2: [], 3: []}

for _, row in df.iterrows():
    mid = row["模块"]
    item_id = str(row["评价ID"])
    textA = str(row["文本A"]).strip()
    imgA = str(row["图片链接A（html）"]).strip()
    if mid == 1:
        module_data[1].append({
            "id": item_id,
            "text": textA,
            "image": imgA
        })
    elif mid == 2 and pd.notna(row.get("文本B")) and pd.notna(row.get("图片链接B（html）")):
        textB = str(row["文本B"]).strip()
        imgB = str(row["图片链接B（html）"]).strip()
        idB = str(row["评价ID_B"]) if "评价ID_B" in row and pd.notna(row["评价ID_B"]) else "UNKNOWN"
        module_data[2].append({
            "id": f"{item_id}|{idB}",
            "textA": textA,
            "imageA": imgA,
            "textB": textB,
            "imageB": imgB
        })
    elif mid == 3:
        module_data[3].append({
            "id": item_id,
            "text": textA,
            "image": imgA
        })


def split_and_save(module_id, items, per_group, total_groups):
    total_required = per_group * total_groups
    assert len(items) >= total_required, f"模块{module_id} 数据不足：需要 {total_required} 条，实际 {len(items)} 条"

    used = set()
    for gid in range(1, total_groups + 1):
        group_items = []
        for item in items:
            if item["id"] not in used:
                group_items.append(item)
                used.add(item["id"])
            if len(group_items) == per_group:
                break
        fname = f"data_module{module_id}_{gid}.json"
        with open(os.path.join(output_dir, fname), "w", encoding="utf-8") as f:
            json.dump(group_items, f, ensure_ascii=False, indent=2)
        print(f"[✅ 写入] {fname} 共 {len(group_items)} 条")

# === 执行 ===
for module_id in [1, 2, 3]:
    per_group, total_groups = group_counts[module_id]
    split_and_save(module_id, module_data[module_id], per_group, total_groups)
