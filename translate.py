#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
translate.py - Optionale KI-Übersetzung für WikiStub-Seed
=======================================================

Übersetzt deutsche Wissens-Stubs ins Englische via Claude API.

Voraussetzungen:
    pip install anthropic
    export ANTHROPIC_API_KEY="<your-anthropic-api-key>"

Nutzung als Modul:
    from translate import translate_text
    english = translate_text("Kurzdefinition auf Deutsch")

Ohne API-Key oder ohne installiertes Paket wird "" zurückgegeben (kein Fehler).
"""

import os
import time

MODEL_ID = "claude-haiku-4-5-20251001"
MAX_OUTPUT_TOKENS = 500
INPUT_USD_PER_MILLION_TOKENS = 1.0
OUTPUT_USD_PER_MILLION_TOKENS = 5.0
PRICING_AS_OF = "2026-07-15"
_MESSAGE_OVERHEAD_TOKENS = 256


def _translation_prompt(text: str, target_lang: str) -> str:
    lang_names = {
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "it": "Italian",
        "pt": "Portuguese",
        "zh": "Chinese",
        "ja": "Japanese",
        "ru": "Russian",
    }
    target_name = lang_names.get(target_lang, target_lang)
    return (
        f"Translate the following German academic definition to {target_name}. "
        f"Return only the translation, no explanations or additional text.\n\n"
        f"German text: {text}"
    )


def estimate_max_request_cost_usd(text: str, target_lang: str = "en") -> float:
    """Return a conservative preflight ceiling for one standard API request.

    Pricing is pinned to Claude Haiku 4.5 standard API rates verified on
    2026-07-15. UTF-8 byte length plus protocol overhead bounds input tokens;
    output is bounded by ``MAX_OUTPUT_TOKENS``.
    """
    prompt = _translation_prompt(text, target_lang)
    max_input_tokens = len(prompt.encode("utf-8")) + _MESSAGE_OVERHEAD_TOKENS
    return (
        max_input_tokens * INPUT_USD_PER_MILLION_TOKENS / 1_000_000
        + MAX_OUTPUT_TOKENS * OUTPUT_USD_PER_MILLION_TOKENS / 1_000_000
    )


def estimate_batch_max_cost_usd(texts: list[str], target_lang: str = "en") -> float:
    return sum(estimate_max_request_cost_usd(text, target_lang) for text in texts)


def translate_text(text: str, target_lang: str = "en") -> str:
    """
    Übersetzt Text via Claude API.

    Args:
        text:        Zu übersetzender Text (Deutsch)
        target_lang: Zielsprache als ISO-Code (default: "en")

    Returns:
        Übersetzter Text oder "" falls API nicht verfügbar.
    """
    if not text or not text.strip():
        return ""

    try:
        import anthropic
    except ImportError:
        return ""

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return ""

    prompt = _translation_prompt(text, target_lang)

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=MODEL_ID,
            max_tokens=MAX_OUTPUT_TOKENS,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return ""


def is_available() -> bool:
    """Prüft ob die Translation-API verfügbar ist."""
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def translate_batch(
    texts: list[str],
    target_lang: str = "en",
    delay: float = 0.3,
    *,
    max_budget_usd: float | None = None,
) -> list[str]:
    """
    Übersetzt eine Liste von Texten mit optionalem Delay zwischen Anfragen.

    Args:
        texts:       Liste von Texten
        target_lang: Zielsprache als ISO-Code
        delay:       Wartezeit in Sekunden zwischen API-Anfragen (Rate-Limit)

    Returns:
        Liste von übersetzten Texten (gleiche Länge wie Input)
    """
    projected_cost = estimate_batch_max_cost_usd(texts, target_lang)
    if max_budget_usd is None or max_budget_usd <= 0:
        raise ValueError("max_budget_usd must be a positive explicit cost ceiling")
    if projected_cost > max_budget_usd:
        raise ValueError(
            f"projected maximum cost ${projected_cost:.6f} exceeds "
            f"budget ${max_budget_usd:.6f}"
        )

    results = []
    for i, text in enumerate(texts):
        result = translate_text(text, target_lang)
        results.append(result)
        if delay > 0 and i < len(texts) - 1:
            time.sleep(delay)
    return results


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="WikiStub-Seed: Text-Übersetzung")
    parser.add_argument("text", nargs="?", help="Zu übersetzender Text")
    parser.add_argument("--lang", default="en", help="Zielsprache (default: en)")
    parser.add_argument("--check", action="store_true", help="API-Verfügbarkeit prüfen")
    parser.add_argument("--max-budget-usd", type=float, help="Explizite Kostenobergrenze in USD")
    parser.add_argument("--confirm-api-cost", action="store_true", help="Mögliche API-Kosten bestätigen")
    args = parser.parse_args()

    if args.check:
        if is_available():
            print("  Übersetzung verfügbar (ANTHROPIC_API_KEY gesetzt)")
        else:
            print("  Übersetzung nicht verfügbar.")
            print("  Bitte setze ANTHROPIC_API_KEY und installiere: pip install anthropic")
        sys.exit(0)

    if not args.text:
        parser.print_help()
        sys.exit(1)

    projected_cost = estimate_max_request_cost_usd(args.text, args.lang)
    if not args.confirm_api_cost or not args.max_budget_usd or args.max_budget_usd <= 0:
        print("FEHLER: --confirm-api-cost und --max-budget-usd > 0 sind erforderlich.")
        sys.exit(1)
    if projected_cost > args.max_budget_usd:
        print(
            f"FEHLER: Maximale Anfragekosten ${projected_cost:.6f} "
            f"überschreiten Budget ${args.max_budget_usd:.6f}."
        )
        sys.exit(1)

    if not is_available():
        print("FEHLER: ANTHROPIC_API_KEY nicht gesetzt oder 'anthropic' nicht installiert.")
        sys.exit(1)

    result = translate_text(args.text, args.lang)
    if result:
        print(result)
    else:
        print("FEHLER: Übersetzung fehlgeschlagen.")
        sys.exit(1)
