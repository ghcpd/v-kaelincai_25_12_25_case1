import hashlib

def generate_summary(unique_ids):
    """
    Generate a summary string from sorted unique IDs.
    """
    ids_str = ', '.join(map(str, unique_ids))
    return f"Unique IDs: {ids_str}"

def create_report(summary):
    """
    Create a report with a deterministic ID based on the summary.
    """
    hash_obj = hashlib.md5(summary.encode())
    report_id = f"RPT-{hash_obj.hexdigest()[:8]}"
    return {
        'report_id': report_id,
        'summary': summary
    }