"""LLM client for B2 — OpenAI-compatible structured extraction.

Reaches the model through the OpenAI Python SDK. ``LLM_PROVIDER=azure_openai``
uses the ``AzureOpenAI`` client; everything else (``azure_foundry`` and any
OpenAI-compatible gateway) uses the plain ``OpenAI`` client pointed at the
configured ``base_url`` — the path validated in the original Colab notebook.
"""

from __future__ import annotations

import json
import time

from smart_tender_assistant.config import Settings, get_settings
from smart_tender_assistant.extraction.prompts import LLM_PROMPT, LLM_SCHEMA

_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {"name": "estrazione_requisiti_bando", "schema": LLM_SCHEMA},
}


class LLMExtractionError(RuntimeError):
    """Raised when the LLM call fails or returns unparsable output."""


def _build_client(settings: Settings):
    base_url, api_key, model = settings.resolve_llm()
    if settings.is_azure_openai:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            azure_endpoint=base_url,
            api_key=api_key,
            api_version=settings.azure_openai_api_version,
            timeout=settings.llm_timeout_seconds,
        )
    else:
        from openai import OpenAI

        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=settings.llm_timeout_seconds,
        )
    return client, model


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1] if "\n" in text else text
        text = text.removeprefix("json").lstrip("\n")
        if text.endswith("```"):
            text = text[: text.rfind("```")]
    return text.strip()


def extract_raw_requirements(
    text: str,
    *,
    settings: Settings | None = None,
) -> list[dict]:
    """Call the LLM on one document's text and return raw requirement dicts.

    Each dict follows ``LLM_SCHEMA`` (keys: ``categoria``, ``tipo``,
    ``descrizione``, ``valore``, ``unita``, ``obbligatorio``, ``fonte_testuale``,
    ``confidenza``).

    Raises:
        LLMExtractionError: on transport failure (after retries) or bad JSON.
    """
    settings = settings or get_settings()
    client, model = _build_client(settings)

    last_error: Exception | None = None
    for attempt in range(settings.llm_max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model=model,
                temperature=settings.llm_temperature,
                messages=[
                    {"role": "system", "content": "Extract participation requirements."},
                    {"role": "user", "content": LLM_PROMPT + text},
                ],
                response_format=_RESPONSE_FORMAT,
            )
            content = completion.choices[0].message.content or ""
            payload = json.loads(_strip_code_fences(content))
            return list(payload.get("requisiti_partecipazione", []))
        except json.JSONDecodeError as exc:
            raise LLMExtractionError(
                f"INVALID_LLM_OUTPUT: model returned non-JSON content: {exc}"
            ) from exc
        except Exception as exc:
            last_error = exc
            if attempt < settings.llm_max_retries:
                time.sleep(2**attempt)

    raise LLMExtractionError(f"LLM call failed after retries: {last_error}") from last_error
