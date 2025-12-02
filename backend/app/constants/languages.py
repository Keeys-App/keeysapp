"""
Language configuration constants.
Single source of truth for all language metadata used across the application.

Contains:
- Basic info: name, native_name, flag, locale, direction
- Plural forms (CLDR standard)
- Detection patterns for file import

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


# Complete language configuration - single source of truth
LANGUAGE_CONFIGS: Dict[str, Dict[str, Any]] = {
    # Germanic languages - typically one/other
    'en': {
        'name': 'English',
        'native_name': 'English',
        'flag': '🇬🇧',
        'locale': 'en-US',
        'direction': 'ltr',
        'plural_forms': ['one', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]en\.(json|js|ts)$', r'[-_.]en[-_.]'],
            'middle_patterns': [r'[-_.]en[-_.]', r'en[-_]US', r'en[-_]GB'],
            'start_patterns': [r'^en[-_.]'],
            'full_names': [r'english'],
        },
    },
    'de': {
        'name': 'German',
        'native_name': 'Deutsch',
        'flag': '🇩🇪',
        'locale': 'de-DE',
        'direction': 'ltr',
        'plural_forms': ['one', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]de\.(json|js|ts)$', r'[-_.]de[-_.]'],
            'middle_patterns': [r'[-_.]de[-_.]', r'de[-_]DE'],
            'start_patterns': [r'^de[-_.]'],
            'full_names': [r'german', r'deutsch'],
        },
    },
    'nl': {
        'name': 'Dutch',
        'native_name': 'Nederlands',
        'flag': '🇳🇱',
        'locale': 'nl-NL',
        'direction': 'ltr',
        'plural_forms': ['one', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]nl\.(json|js|ts)$', r'[-_.]nl[-_.]'],
            'middle_patterns': [r'[-_.]nl[-_.]', r'nl[-_]NL'],
            'start_patterns': [r'^nl[-_.]'],
            'full_names': [r'dutch', r'nederlands'],
        },
    },
    'sv': {
        'name': 'Swedish',
        'native_name': 'Svenska',
        'flag': '🇸🇪',
        'locale': 'sv-SE',
        'direction': 'ltr',
        'plural_forms': ['one', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]sv\.(json|js|ts)$', r'[-_.]sv[-_.]'],
            'middle_patterns': [r'[-_.]sv[-_.]', r'sv[-_]SE'],
            'start_patterns': [r'^sv[-_.]'],
            'full_names': [r'swedish', r'svenska'],
        },
    },
    'no': {
        'name': 'Norwegian',
        'native_name': 'Norsk',
        'flag': '🇳🇴',
        'locale': 'no-NO',
        'direction': 'ltr',
        'plural_forms': ['one', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]no\.(json|js|ts)$', r'[-_.]no[-_.]'],
            'middle_patterns': [r'[-_.]no[-_.]', r'no[-_]NO', r'nb[-_]NO'],
            'start_patterns': [r'^no[-_.]', r'^nb[-_.]'],
            'full_names': [r'norwegian', r'norsk'],
        },
    },
    'da': {
        'name': 'Danish',
        'native_name': 'Dansk',
        'flag': '🇩🇰',
        'locale': 'da-DK',
        'direction': 'ltr',
        'plural_forms': ['one', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]da\.(json|js|ts)$', r'[-_.]da[-_.]'],
            'middle_patterns': [r'[-_.]da[-_.]', r'da[-_]DK'],
            'start_patterns': [r'^da[-_.]'],
            'full_names': [r'danish', r'dansk'],
        },
    },

    # Romance languages - one/many/other
    'es': {
        'name': 'Spanish',
        'native_name': 'Español',
        'flag': '🇪🇸',
        'locale': 'es-ES',
        'direction': 'ltr',
        'plural_forms': ['one', 'many', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]es\.(json|js|ts)$', r'[-_.]es[-_.]'],
            'middle_patterns': [r'[-_.]es[-_.]', r'es[-_]ES'],
            'start_patterns': [r'^es[-_.]'],
            'full_names': [r'spanish', r'español'],
        },
    },
    'fr': {
        'name': 'French',
        'native_name': 'Français',
        'flag': '🇫🇷',
        'locale': 'fr-FR',
        'direction': 'ltr',
        'plural_forms': ['one', 'many', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]fr\.(json|js|ts)$', r'[-_.]fr[-_.]'],
            'middle_patterns': [r'[-_.]fr[-_.]', r'fr[-_]FR'],
            'start_patterns': [r'^fr[-_.]'],
            'full_names': [r'french', r'français'],
        },
    },
    'it': {
        'name': 'Italian',
        'native_name': 'Italiano',
        'flag': '🇮🇹',
        'locale': 'it-IT',
        'direction': 'ltr',
        'plural_forms': ['one', 'many', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]it\.(json|js|ts)$', r'[-_.]it[-_.]'],
            'middle_patterns': [r'[-_.]it[-_.]', r'it[-_]IT'],
            'start_patterns': [r'^it[-_.]'],
            'full_names': [r'italian', r'italiano'],
        },
    },
    'pt': {
        'name': 'Portuguese',
        'native_name': 'Português',
        'flag': '🇵🇹',
        'locale': 'pt-PT',
        'direction': 'ltr',
        'plural_forms': ['one', 'many', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]pt\.(json|js|ts)$', r'[-_.]pt[-_.]'],
            'middle_patterns': [r'[-_.]pt[-_.]', r'pt[-_]BR', r'pt[-_]PT'],
            'start_patterns': [r'^pt[-_.]'],
            'full_names': [r'portuguese', r'português'],
        },
    },
    'ro': {
        'name': 'Romanian',
        'native_name': 'Română',
        'flag': '🇷🇴',
        'locale': 'ro-RO',
        'direction': 'ltr',
        'plural_forms': ['one', 'few', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]ro\.(json|js|ts)$', r'[-_.]ro[-_.]'],
            'middle_patterns': [r'[-_.]ro[-_.]', r'ro[-_]RO'],
            'start_patterns': [r'^ro[-_.]'],
            'full_names': [r'romanian', r'română'],
        },
    },

    # Slavic languages - one/few/many/other
    'ru': {
        'name': 'Russian',
        'native_name': 'Русский',
        'flag': '🇷🇺',
        'locale': 'ru-RU',
        'direction': 'ltr',
        'plural_forms': ['one', 'few', 'many', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]ru\.(json|js|ts)$', r'[-_.]ru[-_.]'],
            'middle_patterns': [r'[-_.]ru[-_.]', r'ru[-_]RU'],
            'start_patterns': [r'^ru[-_.]'],
            'full_names': [r'russian', r'русский'],
        },
    },
    'uk': {
        'name': 'Ukrainian',
        'native_name': 'Українська',
        'flag': '🇺🇦',
        'locale': 'uk-UA',
        'direction': 'ltr',
        'plural_forms': ['one', 'few', 'many', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]uk\.(json|js|ts)$', r'[-_.]uk[-_.]'],
            'middle_patterns': [r'[-_.]uk[-_.]', r'uk[-_]UA'],
            'start_patterns': [r'^uk[-_.]'],
            'full_names': [r'ukrainian', r'українська'],
        },
    },
    'pl': {
        'name': 'Polish',
        'native_name': 'Polski',
        'flag': '🇵🇱',
        'locale': 'pl-PL',
        'direction': 'ltr',
        'plural_forms': ['one', 'few', 'many', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]pl\.(json|js|ts)$', r'[-_.]pl[-_.]'],
            'middle_patterns': [r'[-_.]pl[-_.]', r'pl[-_]PL'],
            'start_patterns': [r'^pl[-_.]'],
            'full_names': [r'polish', r'polski'],
        },
    },
    'cs': {
        'name': 'Czech',
        'native_name': 'Čeština',
        'flag': '🇨🇿',
        'locale': 'cs-CZ',
        'direction': 'ltr',
        'plural_forms': ['one', 'few', 'many', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]cs\.(json|js|ts)$', r'[-_.]cs[-_.]'],
            'middle_patterns': [r'[-_.]cs[-_.]', r'cs[-_]CZ'],
            'start_patterns': [r'^cs[-_.]'],
            'full_names': [r'czech', r'čeština'],
        },
    },

    # East Asian languages - no plural forms (only "other")
    'zh': {
        'name': 'Chinese',
        'native_name': '中文',
        'flag': '🇨🇳',
        'locale': 'zh-CN',
        'direction': 'ltr',
        'plural_forms': ['other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]zh\.(json|js|ts)$', r'[-_.]zh[-_.]'],
            'middle_patterns': [r'[-_.]zh[-_.]', r'zh[-_]CN', r'zh[-_]TW'],
            'start_patterns': [r'^zh[-_.]'],
            'full_names': [r'chinese', r'中文'],
        },
    },
    'ja': {
        'name': 'Japanese',
        'native_name': '日本語',
        'flag': '🇯🇵',
        'locale': 'ja-JP',
        'direction': 'ltr',
        'plural_forms': ['other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]ja\.(json|js|ts)$', r'[-_.]ja[-_.]'],
            'middle_patterns': [r'[-_.]ja[-_.]', r'ja[-_]JP'],
            'start_patterns': [r'^ja[-_.]'],
            'full_names': [r'japanese', r'日本語'],
        },
    },
    'ko': {
        'name': 'Korean',
        'native_name': '한국어',
        'flag': '🇰🇷',
        'locale': 'ko-KR',
        'direction': 'ltr',
        'plural_forms': ['other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]ko\.(json|js|ts)$', r'[-_.]ko[-_.]'],
            'middle_patterns': [r'[-_.]ko[-_.]', r'ko[-_]KR'],
            'start_patterns': [r'^ko[-_.]'],
            'full_names': [r'korean', r'한국어'],
        },
    },
    'vi': {
        'name': 'Vietnamese',
        'native_name': 'Tiếng Việt',
        'flag': '🇻🇳',
        'locale': 'vi-VN',
        'direction': 'ltr',
        'plural_forms': ['other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]vi\.(json|js|ts)$', r'[-_.]vi[-_.]'],
            'middle_patterns': [r'[-_.]vi[-_.]', r'vi[-_]VN'],
            'start_patterns': [r'^vi[-_.]'],
            'full_names': [r'vietnamese', r'tiếng việt'],
        },
    },
    'th': {
        'name': 'Thai',
        'native_name': 'ไทย',
        'flag': '🇹🇭',
        'locale': 'th-TH',
        'direction': 'ltr',
        'plural_forms': ['other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]th\.(json|js|ts)$', r'[-_.]th[-_.]'],
            'middle_patterns': [r'[-_.]th[-_.]', r'th[-_]TH'],
            'start_patterns': [r'^th[-_.]'],
            'full_names': [r'thai', r'ไทย'],
        },
    },

    # Arabic - most complex: zero/one/two/few/many/other
    'ar': {
        'name': 'Arabic',
        'native_name': 'العربية',
        'flag': '🇸🇦',
        'locale': 'ar-SA',
        'direction': 'rtl',
        'plural_forms': ['zero', 'one', 'two', 'few', 'many', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]ar\.(json|js|ts)$', r'[-_.]ar[-_.]'],
            'middle_patterns': [r'[-_.]ar[-_.]', r'ar[-_]SA', r'ar[-_]EG'],
            'start_patterns': [r'^ar[-_.]'],
            'full_names': [r'arabic', r'العربية'],
        },
    },

    # Other languages
    'hi': {
        'name': 'Hindi',
        'native_name': 'हिन्दी',
        'flag': '🇮🇳',
        'locale': 'hi-IN',
        'direction': 'ltr',
        'plural_forms': ['one', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]hi\.(json|js|ts)$', r'[-_.]hi[-_.]'],
            'middle_patterns': [r'[-_.]hi[-_.]', r'hi[-_]IN'],
            'start_patterns': [r'^hi[-_.]'],
            'full_names': [r'hindi', r'हिन्दी'],
        },
    },
    'tr': {
        'name': 'Turkish',
        'native_name': 'Türkçe',
        'flag': '🇹🇷',
        'locale': 'tr-TR',
        'direction': 'ltr',
        'plural_forms': ['one', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]tr\.(json|js|ts)$', r'[-_.]tr[-_.]'],
            'middle_patterns': [r'[-_.]tr[-_.]', r'tr[-_]TR'],
            'start_patterns': [r'^tr[-_.]'],
            'full_names': [r'turkish', r'türkçe'],
        },
    },
    'fi': {
        'name': 'Finnish',
        'native_name': 'Suomi',
        'flag': '🇫🇮',
        'locale': 'fi-FI',
        'direction': 'ltr',
        'plural_forms': ['one', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]fi\.(json|js|ts)$', r'[-_.]fi[-_.]'],
            'middle_patterns': [r'[-_.]fi[-_.]', r'fi[-_]FI'],
            'start_patterns': [r'^fi[-_.]'],
            'full_names': [r'finnish', r'suomi'],
        },
    },
    'hu': {
        'name': 'Hungarian',
        'native_name': 'Magyar',
        'flag': '🇭🇺',
        'locale': 'hu-HU',
        'direction': 'ltr',
        'plural_forms': ['one', 'other'],
        'detection_patterns': {
            'end_patterns': [r'[-_.]hu\.(json|js|ts)$', r'[-_.]hu[-_.]'],
            'middle_patterns': [r'[-_.]hu[-_.]', r'hu[-_]HU'],
            'start_patterns': [r'^hu[-_.]'],
            'full_names': [r'hungarian', r'magyar'],
        },
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


def get_all_languages() -> List[Dict[str, Any]]:
    """
    Get all available languages with their complete configurations.
    
    Returns:
        List of language configurations with code included in each entry.
    """
    return [
        {'code': code, **config}
        for code, config in LANGUAGE_CONFIGS.items()
    ]


# Default locale mappings for language codes (backward compatibility)
DEFAULT_LANGUAGE_LOCALES = {
    code: config['locale'] 
    for code, config in LANGUAGE_CONFIGS.items()
}
