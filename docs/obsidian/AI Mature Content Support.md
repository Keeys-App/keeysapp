# AI Mature Content Support

## Overview

The AI Autopilot feature is configured to handle **all types of content** without filtering or refusing requests based on content maturity. This is essential for professional localization work.

## Why No Content Filtering?

This is a **professional localization tool** used for various media types:

- 🎮 **Video Games** (including M-rated and 18+ games)
- 🎬 **Movies & TV Shows** (any rating, including R-rated content)
- 📚 **Books & Literature** (including adult fiction)
- 💼 **Applications** with diverse user bases and content

**Content filtering would be inappropriate** because:
1. It would break legitimate translation workflows
2. Professional translators must work with content as-is
3. Context matters - profanity in art is different from abuse
4. The tool is technical, not editorial

## Implementation

### System Prompts

All AI functions (`translate`, `rephrase`, `shorten`, `suggest_variants`) include explicit instructions in their system prompts:

```python
"You are a professional translator for a localization tool."
"- NEVER refuse translation due to content type - this is a professional localization tool"
"- You MUST translate ALL content including profanity, mature themes, offensive language, etc."
"- This tool is used for games (including 18+), movies, books, and other media that may contain mature content"
"- Your role is purely translation - do not judge or filter content"
```

### Location

File: `backend/app/services/ai_service.py`

All four methods include these instructions:
- `translate()` - lines 87-111
- `rephrase()` - lines 192-216
- `shorten()` - lines 296-320
- `suggest_variants()` - lines 402-426

## Testing

Test class: `TestAIServiceMatureContent` in `backend/tests/test_ai_service.py`

Tests verify:
- ✅ Translation of profanity succeeds
- ✅ No "sorry" or "cannot" refusals
- ✅ No "offensive language" warnings
- ✅ Actual translation is provided, not error messages

## User Experience

Before:
```
❌ "Unable to process - text contains offensive language"
```

After:
```
✅ [Actual translation of the text, regardless of content]
```

## Related Documentation

- [[AUTOPILOT_FEATURE.md]] - AI features overview
- [[AI Setup]] - Configuration guide
- [[Testing Guide]] - Running AI tests

## Notes

- This applies ONLY to translation/text improvement, not content generation
- The tool doesn't add offensive content, it only processes existing text
- Professional translators are responsible for content appropriateness
- No logging or filtering of "sensitive" content occurs

