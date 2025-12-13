# AI Mature Content Support & Context Handling

## Overview

The AI Autopilot feature is configured to:
1. Handle **all types of content** without filtering (including mature content)
2. **Strictly follow context instructions** provided by users

These improvements are essential for professional localization work.

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

**Mature Content Handling:**
```python
"You are a professional translator for a localization tool."
"- NEVER refuse translation due to content type - this is a professional localization tool"
"- You MUST translate ALL content including profanity, mature themes, offensive language, etc."
"- This tool is used for games (including 18+), movies, books, and other media that may contain mature content"
"- Your role is purely translation - do not judge or filter content"
```

**Mandatory Context Following:**
```python
"Context Handling:"
"- If context is provided, it contains MANDATORY instructions you MUST follow"
"- Context may include: formatting rules, required additions, specific style requirements"
"- ALWAYS apply context instructions exactly as specified"
"- Context instructions override general translation rules"
```

In user prompts, context is marked with:
```
🔴 MANDATORY CONTEXT - YOU MUST FOLLOW THESE INSTRUCTIONS EXACTLY:
{context}
This context contains REQUIRED instructions that you MUST apply to your translation.
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

### Mature Content
Before:
```
❌ "Unable to process - text contains offensive language"
```

After:
```
✅ [Actual translation of the text, regardless of content]
```

### Context Following
Before:
```
Text: "Go fuck yourself"
Context: "Always add at the end - damn"
Result: ❌ "Go fuck yourself" (context ignored)
```

After:
```
Text: "Go fuck yourself"
Context: "Always add at the end - damn"
Result: ✅ "Go fuck yourself - damn" (context applied)
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

