from datasets import load_from_disk
import re

# 1. Load your saved dataset
dataset = load_from_disk("PII_dataset")

# 2. Define the function to detect problems
def has_issue(example):
    entities = example[dataset.column_names[3]]  # 4th column

    entities_empty = (entities == "[]" or entities is None)

    return entities_empty

# 3. Use .filter() to keep only rows WITHOUT issues
clean_dataset = dataset.filter(lambda example: not has_issue(example))

# 4. Save the cleaned dataset
clean_dataset.save_to_disk("PII_dataset_clean")

print(f"✅ Clean dataset saved with {len(clean_dataset)} rows (from original {len(dataset)} rows).")
