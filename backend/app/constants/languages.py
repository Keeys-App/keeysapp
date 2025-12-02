"""
Language configuration constants.
Contains default locale mappings, text direction, and plural forms for all supported languages.

Plural forms follow CLDR (Unicode Common Locale Data Repository) standard:
- zero: Used for zero quantity (e.g., Arabic)
- one: Singular form (e.g., 1 item)
- two: Dual form (e.g., Arabic for exactly 2)
- few: Paucal form (e.g., Russian 2-4)
- many: Large quantity form (e.g., Russian 5-20)
- other: General/default form (always required)

Reference: https://cldr.unicode.org/index/cldr-spec/plural-rules
"""

from typing import Dict, List, Any

# Language configuration with locale, direction, name, and plural forms
LANGUAGE_CONFIGS: Dict[str, Dict[str, Any]] = {
    # Germanic languages - typically one/other
    'en': {
        'locale': 'en-US',
        'direction': 'ltr',
        'name': 'English',
        'plural_forms': ['one', 'other']
    },
    'de': {
        'locale': 'de-DE',
        'direction': 'ltr',
        'name': 'German',
        'plural_forms': ['one', 'other']
    },
    'nl': {
        'locale': 'nl-NL',
        'direction': 'ltr',
        'name': 'Dutch',
        'plural_forms': ['one', 'other']
    },
    'sv': {
        'locale': 'sv-SE',
        'direction': 'ltr',
        'name': 'Swedish',
        'plural_forms': ['one', 'other']
    },
    'no': {
        'locale': 'no-NO',
        'direction': 'ltr',
        'name': 'Norwegian',
        'plural_forms': ['one', 'other']
    },
    'da': {
        'locale': 'da-DK',
        'direction': 'ltr',
        'name': 'Danish',
        'plural_forms': ['one', 'other']
    },
    
    # Romance languages - typically one/other (French has special "many" for large numbers)
    'es': {
        'locale': 'es-ES',
        'direction': 'ltr',
        'name': 'Spanish',
        'plural_forms': ['one', 'many', 'other']
    },
    'fr': {
        'locale': 'fr-FR',
        'direction': 'ltr',
        'name': 'French',
        'plural_forms': ['one', 'many', 'other']
    },
    'it': {
        'locale': 'it-IT',
        'direction': 'ltr',
        'name': 'Italian',
        'plural_forms': ['one', 'many', 'other']
    },
    'pt': {
        'locale': 'pt-PT',
        'direction': 'ltr',
        'name': 'Portuguese',
        'plural_forms': ['one', 'many', 'other']
    },
    'ro': {
        'locale': 'ro-RO',
        'direction': 'ltr',
        'name': 'Romanian',
        'plural_forms': ['one', 'few', 'other']
    },
    
    # Slavic languages - one/few/many/other
    'ru': {
        'locale': 'ru-RU',
        'direction': 'ltr',
        'name': 'Russian',
        'plural_forms': ['one', 'few', 'many', 'other']
    },
    'uk': {
        'locale': 'uk-UA',
        'direction': 'ltr',
        'name': 'Ukrainian',
        'plural_forms': ['one', 'few', 'many', 'other']
    },
    'pl': {
        'locale': 'pl-PL',
        'direction': 'ltr',
        'name': 'Polish',
        'plural_forms': ['one', 'few', 'many', 'other']
    },
    'cs': {
        'locale': 'cs-CZ',
        'direction': 'ltr',
        'name': 'Czech',
        'plural_forms': ['one', 'few', 'many', 'other']
    },
    
    # East Asian languages - no plural forms (only "other")
    'zh': {
        'locale': 'zh-CN',
        'direction': 'ltr',
        'name': 'Chinese',
        'plural_forms': ['other']
    },
    'ja': {
        'locale': 'ja-JP',
        'direction': 'ltr',
        'name': 'Japanese',
        'plural_forms': ['other']
    },
    'ko': {
        'locale': 'ko-KR',
        'direction': 'ltr',
        'name': 'Korean',
        'plural_forms': ['other']
    },
    'vi': {
        'locale': 'vi-VN',
        'direction': 'ltr',
        'name': 'Vietnamese',
        'plural_forms': ['other']
    },
    'th': {
        'locale': 'th-TH',
        'direction': 'ltr',
        'name': 'Thai',
        'plural_forms': ['other']
    },
    
    # Arabic - most complex: zero/one/two/few/many/other
    'ar': {
        'locale': 'ar-SA',
        'direction': 'rtl',
        'name': 'Arabic',
        'plural_forms': ['zero', 'one', 'two', 'few', 'many', 'other']
    },
    
    # Other languages
    'hi': {
        'locale': 'hi-IN',
        'direction': 'ltr',
        'name': 'Hindi',
        'plural_forms': ['one', 'other']
    },
    'tr': {
        'locale': 'tr-TR',
        'direction': 'ltr',
        'name': 'Turkish',
        'plural_forms': ['one', 'other']
    },
    'fi': {
        'locale': 'fi-FI',
        'direction': 'ltr',
        'name': 'Finnish',
        'plural_forms': ['one', 'other']
    },
    'hu': {
        'locale': 'hu-HU',
        'direction': 'ltr',
        'name': 'Hungarian',
        'plural_forms': ['one', 'other']
    },
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


def get_plural_forms(code: str) -> List[str]:
    """
    Get plural forms for a language according to CLDR standard.
    
    Args:
        code: Language code (e.g., 'en', 'ru', 'ar')
        
    Returns:
        List of plural form names (e.g., ['one', 'other'] for English,
        ['one', 'few', 'many', 'other'] for Russian).
        Returns ['other'] as fallback for unknown languages.
    """
    config = LANGUAGE_CONFIGS.get(code)
    if config:
        return config.get('plural_forms', ['other'])
    return ['other']


# Default locale mappings for language codes (backward compatibility)
DEFAULT_LANGUAGE_LOCALES = {
    code: config['locale'] 
    for code, config in LANGUAGE_CONFIGS.items()
}

