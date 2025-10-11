"""
Language configuration constants.
Contains default locale mappings and text direction for all supported languages.
"""

from typing import Dict

# Language configuration with locale and direction
LANGUAGE_CONFIGS: Dict[str, Dict[str, str]] = {
    'en': {'locale': 'en-US', 'direction': 'ltr'},
    'es': {'locale': 'es-ES', 'direction': 'ltr'},
    'fr': {'locale': 'fr-FR', 'direction': 'ltr'},
    'de': {'locale': 'de-DE', 'direction': 'ltr'},
    'it': {'locale': 'it-IT', 'direction': 'ltr'},
    'pt': {'locale': 'pt-PT', 'direction': 'ltr'},
    'ru': {'locale': 'ru-RU', 'direction': 'ltr'},
    'zh': {'locale': 'zh-CN', 'direction': 'ltr'},
    'ja': {'locale': 'ja-JP', 'direction': 'ltr'},
    'ko': {'locale': 'ko-KR', 'direction': 'ltr'},
    'ar': {'locale': 'ar-SA', 'direction': 'rtl'},
    'hi': {'locale': 'hi-IN', 'direction': 'ltr'},
    'nl': {'locale': 'nl-NL', 'direction': 'ltr'},
    'pl': {'locale': 'pl-PL', 'direction': 'ltr'},
    'tr': {'locale': 'tr-TR', 'direction': 'ltr'},
    'vi': {'locale': 'vi-VN', 'direction': 'ltr'},
    'th': {'locale': 'th-TH', 'direction': 'ltr'},
    'sv': {'locale': 'sv-SE', 'direction': 'ltr'},
    'no': {'locale': 'no-NO', 'direction': 'ltr'},
    'da': {'locale': 'da-DK', 'direction': 'ltr'},
    'fi': {'locale': 'fi-FI', 'direction': 'ltr'},
    'cs': {'locale': 'cs-CZ', 'direction': 'ltr'},
    'hu': {'locale': 'hu-HU', 'direction': 'ltr'},
    'ro': {'locale': 'ro-RO', 'direction': 'ltr'},
    'uk': {'locale': 'uk-UA', 'direction': 'ltr'}
}

# Default locale mappings for language codes (backward compatibility)
DEFAULT_LANGUAGE_LOCALES = {
    code: config['locale'] 
    for code, config in LANGUAGE_CONFIGS.items()
}

