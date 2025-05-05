import argparse
from datasets import load_from_disk
import json

# 1. Parse command-line arguments
parser = argparse.ArgumentParser(description="Export HuggingFace dataset to a single JSON file.")
parser.add_argument(
    "--dataset",
    type=str,
    required=True,
    help="Path to the saved HuggingFace dataset folder"
)
parser.add_argument(
    "--output",
    type=str,
    default="dataset.json",
    help="Output JSON file path"
)
args = parser.parse_args()

# 2. Load your saved dataset from the specified path
dataset = load_from_disk(args.dataset)

# 3. Convert to list of dicts
data = dataset.to_list() if hasattr(dataset, 'to_list') else [dict(row) for row in dataset]

# 4. Write as a single JSON array
with open(args.output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Clean dataset saved with {len(dataset)} rows (from original {len(dataset)} rows).")
print(f"✅ JSON file also saved at '{args.output}'.")
