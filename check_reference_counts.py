
import json
from collections import Counter

with open(
    "data/retrieved_missing_records.json",
    "r",
    encoding="utf-8"
) as f:
    records = json.load(f)

counts = Counter(
    record.get("referenced_works_count")
    for record in records
)

print("REFERENCE COUNT FIELD")
print("=====================")

for value, number in sorted(
    counts.items(),
    key=lambda x: (x[0] is None, x[0] or 0)
):
    print(f"{value}: {number} publications")

print("\nEXAMPLE RECORDS")

for record in records[:5]:
    print("\nTitle:", record.get("title"))
    print("Reference count:", record.get("referenced_works_count"))
    print("Matched references:", len(record.get("referenced_works") or []))
