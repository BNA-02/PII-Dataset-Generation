from datasets import load_from_disk
import re

# 1. Load your saved dataset
dataset = load_from_disk("PII_dataset")

# 2. Initialize counters
bad_samples = 0

# 3. Loop through the dataset
for i, sample in enumerate(dataset):
    raw_text = sample[dataset.column_names[1]]  # 2nd column
    entities = sample[dataset.column_names[3]]  # 4th column
    print(sample[dataset.column_names[3]])
    # Condition 1: entities column is empty
    is_entities_empty = (entities == "[]" or entities is None)
    print(is_entities_empty)
    if is_entities_empty:
        bad_samples += 1

# 4. Final count
print(f"📊 Number of problematic records: {bad_samples}")
print(f"🧮 Total records checked: {len(dataset)}")
#📊 Number of problematic records: 216
#🧮 Total records checked: 1000
