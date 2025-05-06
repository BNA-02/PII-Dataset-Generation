from datasets import load_from_disk
import re

# 1. Load your saved dataset
dataset = load_from_disk("PII_dataset_rand")

# 2. Initialize counters and collectors
bad_samples = 0
bad_samples_with_phrase = 0
bad_samples_info = []
bad_samples_with_phrase_info = []

# 3. Loop through the dataset
for i, sample in enumerate(dataset):
    raw_text = sample[dataset.column_names[1]]  # 2nd column
    entities = sample[dataset.column_names[3]]  # 4th column

    # Condition 1: entities column is empty
    is_entities_empty = (entities == "[]" or entities is None)
    
    # Condition 2: raw_text contains the phrase
    contains_phrase = "je ne peux pas" in raw_text.lower()
    
    if is_entities_empty:
        bad_samples += 1
        bad_samples_info.append({
            "index": i,
            "raw_text_snippet": raw_text[:80] + ("..." if len(raw_text) > 80 else ""),
            "entities": entities
        })
        if contains_phrase:
            bad_samples_with_phrase += 1
            bad_samples_with_phrase_info.append({
                "index": i,
                "raw_text_snippet": raw_text[:80] + ("..." if len(raw_text) > 80 else ""),
                "entities": entities
            })

# 4. Final count and sample info
print(f"📊 Number of problematic records (entities empty): {bad_samples}")
print(f"🧮 Total records checked: {len(dataset)}")
print(f"🔍 Number of records where 'je ne peux pas' is present and entities are empty: {bad_samples_with_phrase}")

print("\n--- Bad samples (entities empty) ---")
for info in bad_samples_info[:5]:  # Show only first 5 for brevity
    print(f"Index: {info['index']}, Entities: {info['entities']}, Text: {info['raw_text_snippet']}")

print("\n--- Bad samples with phrase (entities empty & phrase present) ---")
for info in bad_samples_with_phrase_info[:5]:  # Show only first 5 for brevity
    print(f"Index: {info['index']}, Entities: {info['entities']}, Text: {info['raw_text_snippet']}")

#📊 Number of problematic records: 216
#🧮 Total records checked: 1000
