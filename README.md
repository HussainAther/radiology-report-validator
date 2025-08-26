# Radiology Report Validator (Amazon Nova)

A lightweight **Streamlit app** that validates radiology free-text reports against structured fields.  
It can extract fields using **Amazon Nova (Bedrock)** or a simple **local regex fallback** for offline demos.

---

## ✨ Features
- Upload CSV with required columns:
  - `patient_id`
  - `report_text`
  - `structured_laterality`
  - `structured_quadrant`
  - `structured_finding`
  - `structured_microcalcifications`
  - `structured_size_mm`
- Choose backend:
  - **AWS Nova (Bedrock)** → structured extraction via LLM
  - **Local regex (demo)** → quick offline rule-based extraction
- Configurable **size tolerance** (mm)
- Interactive results table + **CSV download**

---

## 🚀 Run Locally

```bash
# 1. Clone repo & enter
git clone https://github.com/<your-username>/streamlit-nova-validator.git
cd streamlit-nova-validator

# 2. Set up Python environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure AWS Bedrock
export BEDROCK_REGION=us-east-1
export BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
# Ensure your AWS profile/creds has Bedrock InvokeModel permissions

# 5. Run Streamlit app
streamlit run app.py

