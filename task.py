import json

import pandas as pd
from dotenv import load_dotenv

from data import add_info
from llm import analyze
from play_scraper import create_category_dataset

load_dotenv()

category = "FINANCE"
country = "IN"
dataset = create_category_dataset(category, country)

with open("dataset\\dataset_FINANCE_IN.json", encoding="utf-8") as f:
    dataset = json.load(f)

print("Loaded dataset")
print("Length:", len(dataset))

expanded = []
for i in range(len(dataset)):
    try:
        print(f"-----{i}-----")
        old = dataset[i]
        new = add_info(old)
        expanded.append(new)
    except Exception as e:
        print(f"XXXX {i} XXXX - {e}")


with open(f"dataset\\dataset_{category}_{country}_expanded.json", "w", encoding="utf-8") as f:
    json.dump(expanded, f, indent=4, ensure_ascii=False, default=str)


results = []

for i, app in enumerate(dataset):
    try:
        print(f"---- {i} -----")
        app_id, url = app["appId"], app["url"]
        result = analyze(app)
    except Exception as e:
        print(f"XXXXX {i} XXXXX")
        print(e)
        continue

    res = result.pop("overall_analysis", None)
    pred, reason = res["type"], res["reason"]
    results.append({
        "app_id": app_id,
        "url": url,
        "prediction": pred,
        "reason": reason,
        "other": result,
    })

df = pd.DataFrame(results)
df[["app_id", "url", "prediction", "reason"]].to_csv("results.csv")
df.to_json("results.json", orient="records")
