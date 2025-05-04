from datasets import load_from_disk
import re

# 1. Load your saved dataset
dataset = load_from_disk("PII_dataset") #_clean
dataset.to_json("PII_dataset/dataset.json", orient="records", lines=True)

print(f"✅ Clean dataset saved with {len(dataset)} rows (from original {len(dataset)} rows).")
print("✅ JSON file also saved at 'PII_dataset/dataset.json'.")