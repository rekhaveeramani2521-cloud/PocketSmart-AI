import base64
import json
import re
from typing import Any
from .config import AI_ENABLED, GEMINI_API_KEY, GEMINI_MODEL


SYSTEM_RULES = """
You are the recommendation engine for PocketSmart AI, an Indian budget planning assistant.
Return practical, budget-aware suggestions only. Prices are estimates in INR, not live quotes.
Never claim that a product is currently in stock or that a price is live unless external verified data is supplied.
Keep the sum of estimated prices at or below the user's budget whenever possible.
Return JSON only, with keys: title, summary, budget, estimated_total, remaining_budget,
recommendations, tips, outfit_analysis. recommendations is an array of objects with keys:
category, item, platform, estimated_price, reason. Platforms should be selected only from the
platforms named in the user request. tips must be an array of short strings.
""".strip()


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I | re.S)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def generate_json(prompt: str, image_bytes: bytes | None = None, mime_type: str | None = None) -> dict[str, Any] | None:
    if not AI_ENABLED or not GEMINI_API_KEY:
        return None
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)
        contents: list[Any] = [SYSTEM_RULES + "\n\n" + prompt]
        if image_bytes and mime_type:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.35,
                response_mime_type="application/json",
            ),
        )
        if not getattr(response, "text", None):
            return None
        return _extract_json(response.text)
    except Exception as exc:
        print(f"[PocketSmart AI] Gemini unavailable, using fallback: {exc}")
        return None
