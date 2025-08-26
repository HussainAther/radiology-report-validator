import os, json
from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, Field
import importlib

@dataclass
class BedrockConfig:
    region: str = "us-east-1"
    model_id: str = "amazon.nova-pro-v1:0"
    temperature: float = 0.0
    max_tokens: int = 512

def ensure_boto3():
    try:
        importlib.import_module("boto3")
    except ImportError as e:
        raise RuntimeError("boto3 is required for AWS Nova mode. Install with: pip install boto3") from e

class ExtractedReport(BaseModel):
    laterality: Optional[str] = Field(None)
    quadrant: Optional[str] = Field(None)
    finding: Optional[str] = Field(None)
    microcalcifications: Optional[bool] = None
    size_mm: Optional[float] = None

SYSTEM = (
    "You are a radiology QA extractor. "
    "Extract exactly these fields as JSON. Do not include commentary."
)

def _build_user_prompt(report_text: str) -> str:
    return f"""
Extract these fields from the radiology report:

Return strictly this JSON schema:
{{
  "laterality": "left|right|null",
  "quadrant": "upper outer|upper inner|lower outer|lower inner|retroareolar|null",
  "finding": "mass|no suspicious finding|other|null",
  "microcalcifications": true|false|null,
  "size_mm": number|null
}}

Rules:
- If benign calcifications only, set microcalcifications=false (not suspicious).
- If no size stated, size_mm=null.
- Be conservative; prefer null over guessing.

REPORT:
\"\"\"{report_text}\"\"\"
""".strip()

def call_nova_extract(report_text: str, cfg: BedrockConfig) -> ExtractedReport:
    import boto3
    brt = boto3.client("bedrock-runtime", region_name=cfg.region)
    messages = [
        {"role": "system", "content": [{"text": SYSTEM}]},
        {"role": "user", "content": [{"text": _build_user_prompt(report_text)}]},
    ]
    resp = brt.converse(
        modelId=cfg.model_id,
        messages=messages,
        inferenceConfig={"temperature": cfg.temperature, "maxTokens": cfg.max_tokens},
    )
    text = resp["output"]["message"]["content"][0]["text"]
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[1] if "\n" in text else text
    data = json.loads(text)
    return ExtractedReport(**data)

