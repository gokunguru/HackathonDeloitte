"""PII detection and masking module using Google Cloud DLP with local regex fallback."""

import os
import re
from typing import Any

import config


def _mask_with_gcp_dlp(text: str, project_id: str) -> dict[str, Any] | None:
    """Attempt PII inspection and de-identification via Google Cloud DLP."""
    try:
        from google.cloud import dlp_v2  # type: ignore

        client = dlp_v2.DlpServiceClient()
        parent = f"projects/{project_id}/locations/{config.GCP_REGION}"

        info_types = [{"name": t} for t in config.GCP_DLP_INFO_TYPES]
        inspect_config = {
            "info_types": info_types,
            "include_quote": True,
        }
        deidentify_config = {
            "info_type_transformations": {
                "transformations": [
                    {
                        "primitive_transformation": {
                            "replace_with_info_type_config": {}
                        }
                    }
                ]
            }
        }

        response = client.deidentify_content(
            request={
                "parent": parent,
                "deidentify_config": deidentify_config,
                "inspect_config": inspect_config,
                "item": {"value": text},
            }
        )

        summaries = response.overview.transformation_summaries or []
        details: list[dict[str, Any]] = []
        total_count = 0
        for summary in summaries:
            info_type_name = summary.info_type.name or "SENSITIVE_DATA"
            count = sum(r.count for r in summary.results)
            if count > 0:
                total_count += count
                details.append(
                    {
                        "info_type": info_type_name,
                        "count": count,
                        "engine": "gcp_dlp",
                    }
                )

        return {
            "masked_text": response.item.value,
            "findings_count": total_count,
            "details": details,
        }
    except Exception:
        return None


def _mask_with_regex(text: str) -> dict[str, Any]:
    """Fallback local regex masking using centralized config.DLP_PATTERNS."""
    masked_text = text
    details: list[dict[str, Any]] = []
    total_count = 0

    for info_type, pattern in config.DLP_PATTERNS.items():
        compiled = re.compile(pattern)
        matches = list(compiled.finditer(masked_text))
        count = len(matches)
        if count > 0:
            replacement = config.DLP_MASK_TEMPLATE.format(info_type=info_type)
            if "prefix" in compiled.groupindex:
                masked_text = compiled.sub(
                    lambda m, repl=replacement: f"{m.group('prefix')}{repl}",
                    masked_text,
                )
            else:
                masked_text = compiled.sub(replacement, masked_text)
            total_count += count
            details.append(
                {
                    "info_type": info_type,
                    "count": count,
                    "engine": "regex_fallback",
                }
            )

    return {
        "masked_text": masked_text,
        "findings_count": total_count,
        "details": details,
    }


def mask_sensitive_data(text: str) -> dict[str, Any]:
    """Detect and mask PII in text via Google Cloud DLP or local regex fallback."""
    if not text or not text.strip():
        return {"masked_text": text or "", "findings_count": 0, "details": []}

    project_id = os.environ.get(config.ENV_GCP_PROJECT, "").strip()
    if project_id:
        gcp_result = _mask_with_gcp_dlp(text, project_id)
        if gcp_result is not None:
            return gcp_result

    return _mask_with_regex(text)
