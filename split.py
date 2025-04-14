import pandas as pd
import os
import json
import random
from itertools import combinations

# 读取并重命名
df = pd.read_excel("用研_评价抽样_20250414.xlsx")
df = df.rename(columns={
    "评价": "id",
    "评价内容链接": "image",
    "评价文字内容": "text",
    "商品名称": "name"
})

# 清洗数据
df = df.dropna(subset=["id", "image", "text", "name"]).drop_duplicates(subset="id").reset_index(drop=True)

# 仅取前50条
df = df.sample(frac=1, random_state=42).head(50).reset_index(drop=True)

# 输出目录
output_dir = "./"
os.makedirs(output_dir, exist_ok=True)

# ========== 模块 1: 单条打分（50条） ==========
module1 = []
for _, row in df.iterrows():
    module1.append({
        "id": str(row["id"]),
        "text": row["text"],
        "image": row["image"],
        "name": row["name"]
    })
with open(f"{output_dir}/data_module1.json", "w", encoding="utf-8") as f:
    json.dump(module1, f, ensure_ascii=False, indent=2)

# ========== 模块 2: 两两配对（25组） ==========
pairs = list(combinations(df.index, 2))
random.seed(42)
random.shuffle(pairs)
selected_pairs = pairs[:25]

module2 = []
for idx_a, idx_b in selected_pairs:
    a = df.loc[idx_a]
    b = df.loc[idx_b]
    module2.append({
        "id": f"{a['id']}|{b['id']}",
        "textA": a["text"],
        "imageA": a["image"],
        "nameA": a["name"],
        "textB": b["text"],
        "imageB": b["image"],
        "nameB": b["name"]
    })
with open(f"{output_dir}/data_module2.json", "w", encoding="utf-8") as f:
    json.dump(module2, f, ensure_ascii=False, indent=2)

# ========== 模块 3: 拖拽排序题（10组，每组5条） ==========
groups = [df.iloc[i*5:(i+1)*5] for i in range(10)]
module3 = []
for g in groups:
    for _, row in g.iterrows():
        module3.append({
            "id": str(row["id"]),
            "text": row["text"],
            "image": row["image"],
            "name": row["name"]
        })
with open(f"{output_dir}/data_module3.json", "w", encoding="utf-8") as f:
    json.dump(module3, f, ensure_ascii=False, indent=2)

print("✅ 已生成 data_module1.json / 2 / 3（每模块仅一个文件）")
