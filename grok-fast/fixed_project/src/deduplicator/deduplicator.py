import csv

def deduplicate_records(records):
    """
    Deduplicate records based on 'id' field and return sorted unique IDs.
    """
    seen_ids = set()
    for record in records:
        seen_ids.add(record['id'])
    return sorted(seen_ids)  # Return sorted list for deterministic order

def load_records_from_csv(file_path):
    """
    Load records from CSV file.
    """
    records = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records