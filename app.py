import os
import json
import streamlit as st
import pandas as pd
from typing import Dict, Any

from validator import validate_row, SIZE_TOL_MM
from extractor_bedrock import call_nova_extract, BedrockConfig, ensure_boto3
from extractor_regex import extract_fields_locally

st.set_page_config(page_title="Radiology Report Validator (AWS Nova)", layout="wide")
st.title("Radiology Report Validator")
st.caption("Validate radiology free-text against structured fields using Amazon Nova (or a local regex fallback).")

# Sidebar configuration
mode = st.sidebar.radio("Extraction backend", ["AWS Nova (Bedrock)", "Local regex (demo)"])
size_tol = st.sidebar.slider("Size tolerance (mm)", min_value=0.0, max_value=5.0, value=1.0, step=0.5)
st.sidebar.markdown("---")
st.sidebar.markdown("**AWS Settings (for Nova mode)**")
region = st.sidebar.text_input("BEDROCK_REGION", os.getenv("BEDROCK_REGION", "us-east-1"))
model_id = st.sidebar.text_input("BEDROCK_MODEL_ID", os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0"))
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.0, 0.1)

uploaded = st.file_uploader("Upload CSV with columns: patient_id, report_text, structured_laterality, structured_quadrant, structured_finding, structured_microcalcifications, structured_size_mm", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    required_cols = ["patient_id","report_text","structured_laterality","structured_quadrant","structured_finding","structured_microcalcifications","structured_size_mm"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
        st.stop()

    st.subheader("Input preview")
    st.dataframe(df.head(), use_container_width=True)

    if st.button("Run validation", type="primary"):
        results = []
        if mode.startswith("AWS"):
            ensure_boto3()
            cfg = BedrockConfig(region=region, model_id=model_id, temperature=temperature)
        for _, row in df.iterrows():
            report = str(row["report_text"])
            try:
                if mode.startswith("AWS"):
                    extracted = call_nova_extract(report, cfg).dict()
                else:
                    extracted = extract_fields_locally(report)
            except Exception as e:
                extracted = {"error": str(e)}

            structured = {
                "structured_laterality": row.get("structured_laterality"),
                "structured_quadrant": row.get("structured_quadrant"),
                "structured_finding": row.get("structured_finding"),
                "structured_microcalcifications": row.get("structured_microcalcifications"),
                "structured_size_mm": row.get("structured_size_mm"),
                "report_text": report,
            }

            out = validate_row(structured, extracted, size_tol_mm=size_tol)
            out["patient_id"] = row.get("patient_id")
            results.append(out)

        res_df = pd.DataFrame(results)
        st.subheader("Validation results")
        st.dataframe(res_df, use_container_width=True)
        csv = res_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download results CSV", data=csv, file_name="validation_results.csv", mime="text/csv")
else:
    st.info("Upload a CSV to begin. You can try the included **sample_data/sample_reports.csv** from the repo.")

