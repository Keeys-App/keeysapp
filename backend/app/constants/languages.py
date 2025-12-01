"""
Language configuration constants.
Contains default locale mappings and text direction for all supported languages.
"""

from typing import Dict

# Language configuration with locale, direction, and name for AI translation
LANGUAGE_CONFIGS: Dict[str, Dict[str, str]] = {
    'en': {'locale': 'en-US', 'direction': 'ltr', 'name': 'English'},
    'es': {'locale': 'es-ES', 'direction': 'ltr', 'name': 'Spanish'},
    'fr': {'locale': 'fr-FR', 'direction': 'ltr', 'name': 'French'},
    'de': {'locale': 'de-DE', 'direction': 'ltr', 'name': 'German'},
    'it': {'locale': 'it-IT', 'direction': 'ltr', 'name': 'Italian'},
    'pt': {'locale': 'pt-PT', 'direction': 'ltr', 'name': 'Portuguese'},
    'ru': {'locale': 'ru-RU', 'direction': 'ltr', 'name': 'Russian'},
    'zh': {'locale': 'zh-CN', 'direction': 'ltr', 'name': 'Chinese'},
    'ja': {'locale': 'ja-JP', 'direction': 'ltr', 'name': 'Japanese'},
    'ko': {'locale': 'ko-KR', 'direction': 'ltr', 'name': 'Korean'},
    'ar': {'locale': 'ar-SA', 'direction': 'rtl', 'name': 'Arabic'},
    'hi': {'locale': 'hi-IN', 'direction': 'ltr', 'name': 'Hindi'},
    'nl': {'locale': 'nl-NL', 'direction': 'ltr', 'name': 'Dutch'},
    'pl': {'locale': 'pl-PL', 'direction': 'ltr', 'name': 'Polish'},
    'tr': {'locale': 'tr-TR', 'direction': 'ltr', 'name': 'Turkish'},
    'vi': {'locale': 'vi-VN', 'direction': 'ltr', 'name': 'Vietnamese'},
    'th': {'locale': 'th-TH', 'direction': 'ltr', 'name': 'Thai'},
    'sv': {'locale': 'sv-SE', 'direction': 'ltr', 'name': 'Swedish'},
    'no': {'locale': 'no-NO', 'direction': 'ltr', 'name': 'Norwegian'},
    'da': {'locale': 'da-DK', 'direction': 'ltr', 'name': 'Danish'},
    'fi': {'locale': 'fi-FI', 'direction': 'ltr', 'name': 'Finnish'},
    'cs': {'locale': 'cs-CZ', 'direction': 'ltr', 'name': 'Czech'},
    'hu': {'locale': 'hu-HU', 'direction': 'ltr', 'name': 'Hungarian'},
    'ro': {'locale': 'ro-RO', 'direction': 'ltr', 'name': 'Romanian'},
    'uk': {'locale': 'uk-UA', 'direction': 'ltr', 'name': 'Ukrainian'}
}


def get_language_name(code: str) -> str:
    """
    Get human-readable language name for AI translation.
    
    Args:
        code: Language code (e.g., 'en', 'es')
        
    Returns:
        Language name (e.g., 'English', 'Spanish') or the code itself if not found
    """
    config = LANGUAGE_CONFIGS.get(code)
    if config:
        return config.get('name', code)
    return code

# Default locale mappings for language codes (backward compatibility)
DEFAULT_LANGUAGE_LOCALES = {
    code: config['locale'] 
    for code, config in LANGUAGE_CONFIGS.items()
}

