
import re
import json
from pathlib import Path


# LOAD FIELD INDEX
BASE_DIR = Path(__file__).resolve().parents[2]

INDEX_FILE = (BASE_DIR/ "index_dictionary"/ "field_index.json")

with open(INDEX_FILE, "r", encoding="utf-8") as file:
    field_index = json.load(file)


# NORMALIZE FIELD NAME
def normalize_field_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[_-]+", " ", name)
    name = re.sub(r"\s+", " ", name)

    return name


# GET FEATURE FIELD INFO
def get_feature_field_info(value: str, info: str, feature_view: str = None):
    info = info.strip().lower()
    # Split multiple field names
    fields = re.split(
        r"\s*(?:,|\bor\b|\band\b)\s*",
        value,
        flags=re.IGNORECASE
    )

    fields = [field.strip() for field in fields if field.strip()]

    results = {}
    not_found = []
    normalized_feature_view = (normalize_field_name(feature_view) if feature_view else None)

    # Process each requested field
    for field_name in fields:

        normalized_name = normalize_field_name(field_name)

        # Direct lookup using normalized field name
        files = field_index.get(normalized_name, [])

        # Field does not exist
        if not files:
            not_found.append(field_name)
            continue

        field_results = []

        # Process every matching field entry
        for entry in files:
            if normalized_feature_view:
                if normalize_field_name(entry.get("feature_view","")) != normalized_feature_view:
                    continue
                
            result = {
                "field": normalized_name,
                "feature_view": entry.get("feature_view"),
                "normalized_feature_view": normalize_field_name(entry.get("feature_view","")),
                "entity": entry.get("entity"),
                "file": entry.get("file"),
            }

            # Requested information
            if info == "description":
                result["description"] = entry.get("description", "")

            elif info == "business_logic":
                result["business_logic"] = entry.get("business_logic", "")

            elif info == "type":
                result["type"] = entry.get("type", "")

            elif info == "all":
                result["type"] = entry.get("type", "")
                result["description"] = entry.get("description", "")
                result["business_logic"] = entry.get("business_logic", "")

            else:
                result["error"] = (f"Unknown information type '{info}'.")
            field_results.append(result)
        results[field_name] = field_results

    return {
        "results": results,
        "info": info,
        "not_found": not_found
    }
