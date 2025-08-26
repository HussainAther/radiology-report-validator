from typing import Dict, Any

SIZE_TOL_MM = 1.0

def validate_row(structured: Dict[str, Any], extracted: Dict[str, Any], size_tol_mm: float = SIZE_TOL_MM) -> Dict[str, Any]:
    mismatches = []
    def add(name, s, e):
        mismatches.append(f"{name}: {s} vs {e}")

    # normalize keys for convenience
    e_lat = extracted.get("laterality")
    e_quad = extracted.get("quadrant")
    e_find = extracted.get("finding")
    e_calc = extracted.get("microcalcifications")
    e_size = extracted.get("size_mm")

    s_lat  = structured.get("structured_laterality")
    s_quad = structured.get("structured_quadrant")
    s_find = structured.get("structured_finding")
    s_calc = structured.get("structured_microcalcifications")
    s_size = structured.get("structured_size_mm")

    if e_lat is not None and s_lat != e_lat:
        add("laterality", s_lat, e_lat)
    if e_quad is not None and s_quad != e_quad:
        add("quadrant", s_quad, e_quad)
    if e_find is not None and s_find != e_find:
        add("finding", s_find, e_find)
    if e_calc is not None and s_calc != e_calc:
        add("microcalcifications", s_calc, e_calc)

    if e_size is not None:
        if s_size is None:
            add("size_mm", None, e_size)
        else:
            try:
                if abs(float(s_size) - float(e_size)) > float(size_tol_mm):
                    add("size_mm", s_size, e_size)
            except Exception:
                add("size_mm", s_size, e_size)

    return {
        "extracted_laterality": e_lat,
        "extracted_quadrant": e_quad,
        "extracted_finding": e_find,
        "extracted_microcalcifications": e_calc,
        "extracted_size_mm": e_size,
        "mismatch_count": len(mismatches),
        "mismatches": "; ".join(mismatches),
        "report_text": structured.get("report_text", ""),
    }

