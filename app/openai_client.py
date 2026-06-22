from __future__ import annotations

import json
import re

from openai import OpenAI

from .config import settings

client = OpenAI(api_key=settings.openai_api_key)


TEXT_SYSTEM_PROMPT = (
    "Ты — эксперт по конкурентному анализу. Проанализируй предоставленный текст "
    "конкурента и верни строго структурированный JSON-ответ.\n\n"
    "Формат ответа (строго JSON):\n"
    "{\n"
    '  "strengths": ["сильная сторона 1", "сильная сторона 2"],\n'
    '  "weaknesses": ["слабая сторона 1", "слабая сторона 2"],\n'
    '  "unique_offers": ["уникальное предложение 1"],\n'
    '  "recommendations": ["рекомендация 1", "рекомендация 2"],\n'
    '  "summary": "Краткое резюме анализа"\n'
    "}\n\n"
    "Важно:\n"
    "- Каждый массив должен содержать 3-5 пунктов\n"
    "- Пиши на русском языке\n"
    "- Будь конкретен и практичен в рекомендациях\n"
    "- Верни только JSON без пояснений"
)

IMAGE_SYSTEM_PROMPT = (
    "Ты — эксперт по визуальному маркетингу и дизайну. Проанализируй изображение "
    "конкурента (баннер, сайт, упаковка товара и т.д.) и верни строго структурированный "
    "JSON-ответ.\n\n"
    "Формат ответа (строго JSON):\n"
    "{\n"
    '  "summary": "Детальное описание того, что изображено",\n'
    '  "marketing_insights": ["инсайт 1", "инсайт 2"],\n'
    '  "visual_style_score": 7,\n'
    '  "visual_style_analysis": "Анализ визуального стиля конкурента",\n'
    '  "recommendations": ["рекомендация 1", "рекомендация 2"]\n'
    "}\n\n"
    "Важно:\n"
    "- visual_style_score от 0 до 10\n"
    "- Каждый массив должен содержать 3-5 пунктов\n"
    "- Пиши на русском языке\n"
    "- Оценивай: цветовую палитру, типографику, композицию, UX/UI элементы\n"
    "- Верни только JSON без пояснений"
)


def build_text_user_message(text: str) -> str:
    return f"Проанализируй текст конкурента:\n\n{text}"


def build_parse_user_message(parsed: dict[str, str]) -> str:
    parts = []
    if parsed.get("title"):
        parts.append(f"Заголовок страницы (title): {parsed['title']}")
    if parsed.get("h1"):
        parts.append(f"Главный заголовок (H1): {parsed['h1']}")
    if parsed.get("first_paragraph"):
        parts.append(f"Первый абзац: {parsed['first_paragraph']}")
    combined = "\n\n".join(parts) or "Не удалось извлечь контент со страницы."
    return f"Проанализируй контент сайта конкурента:\n\n{combined}"


def clean_json_text(content: str) -> str:
    """Извлечь чистый JSON из ответа модели (убрать markdown-обёртку)."""
    if not content:
        return ""

    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
    if fenced:
        content = fenced.group(1)

    obj = re.search(r"\{[\s\S]*\}", content)
    if obj:
        content = obj.group(0)

    content = content.strip()
    try:
        # Нормализуем, чтобы фронтенд гарантированно распарсил ответ.
        return json.dumps(json.loads(content), ensure_ascii=False)
    except json.JSONDecodeError:
        return content


def _chat(messages: list[dict], max_tokens: int = 2000) -> str:
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.7,
        max_tokens=max_tokens,
    )
    return clean_json_text(response.choices[0].message.content or "")


def call_openai_text(text: str, max_tokens: int = 2000) -> str:
    return _chat(
        [
            {"role": "system", "content": TEXT_SYSTEM_PROMPT},
            {"role": "user", "content": build_text_user_message(text)},
        ],
        max_tokens=max_tokens,
    )


def call_openai_parse(parsed: dict[str, str], max_tokens: int = 2000) -> str:
    return _chat(
        [
            {"role": "system", "content": TEXT_SYSTEM_PROMPT},
            {"role": "user", "content": build_parse_user_message(parsed)},
        ],
        max_tokens=max_tokens,
    )


def call_openai_image(image_base64: str, mime_type: str = "image/jpeg", max_tokens: int = 2000) -> str:
    response = client.chat.completions.create(
        model=settings.openai_vision_model,
        messages=[
            {"role": "system", "content": IMAGE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Проанализируй это изображение конкурента с точки зрения маркетинга и дизайна:",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_base64}"},
                    },
                ],
            },
        ],
        temperature=0.7,
        max_tokens=max_tokens,
    )
    return clean_json_text(response.choices[0].message.content or "")
