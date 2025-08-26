import re
from typing import Dict, Any

QUADS = ["upper outer","upper inner","lower outer","lower inner","retroareolar"]

def extract_fields_locally(text: str) -> Dict[str, Any]:
    t = text.lower().replace("-", " ").replace("_", " ")
    # laterality
    laterality = None
    for k in ["left", "right"]:
        if re.search(rf"\b{k}\b", t):
            laterality = k
            break
    # quadrant
    quadrant = None
    for q in QUADS:
        if q in t:
            quadrant = q
            break
    # size (in mm)
    m = re.search(r"(\d+(?:\.\d+)?)\s*mm", t)
    size_mm = float(m.group(1)) if m else None
    # calcifications
    if re.search(r"no\s+(suspicious\s+)?micro\s?calcifications|no\s+calcifications", t):
        microcalcs = False
    elif re.search(r"micro\s?calcifications|calcifications", t):
        microcalcs = "benign" not in t
    else:
        microcalcs = None
    # finding
    if "no suspicious" in t or "birads 1" in t:
        finding = "no suspicious finding"
    elif "mass" in t or "lesion" in t or "focus" in t:
        finding = "mass"
    else:
        finding = None

    return {
        "laterality": laterality,
        "quadrant": quadrant,
        "finding": finding,
        "microcalcifications": microcalcs,
        "size_mm": size_mm,
    }

