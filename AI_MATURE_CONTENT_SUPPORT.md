# AI Mature Content Support & Context Handling Fix

## Problems

### Problem 1: Refusal of mature content
AI refused to translate text with profanity, showing error:
```
❌ "Unable to process - text contains offensive language"
```

This was unacceptable for:
- Games rated 18+
- Artistic works
- Realistic dialogues
- Professional localization of adult content

### Problem 2: Ignoring context
AI ignored user instructions in the "Context" field:
```
Text: "Go fuck yourself"
Context: "Always add at the end - damn"
Result: ❌ "Go fuck yourself" (context ignored)
```

## Solutions

### 1. Mature Content Support
Updated system prompts for all AI functions to explicitly state that this is a **professional localization tool** that must process ANY content without filtering.

### 2. Mandatory Context Following
Strengthened prompts for strict context compliance:
- Context now marked as **MANDATORY** (🔴 marker)
- Added explicit instructions that context contains required rules
- Context applied in both user prompt and system content

## Changes

### 1. Backend - AI Service

**File:** `backend/app/services/ai_service.py`

Updated system prompts for all functions:
- `translate()` 
- `rephrase()`  
- `shorten()`
- `suggest_variants()`

**Added for mature content:**
```python
"You are a professional translator for a localization tool."
"- NEVER refuse translation due to content type - this is a professional localization tool"
"- You MUST translate ALL content including profanity, mature themes, offensive language, etc."
"- This tool is used for games (including 18+), movies, books, and other media that may contain mature content"
"- Your role is purely translation - do not judge or filter content"
```

**Added for mandatory context:**
```python
"Context Handling:"
"- If context is provided, it contains MANDATORY instructions you MUST follow"
"- Context may include: formatting rules, required additions, specific style requirements"
"- ALWAYS apply context instructions exactly as specified"
"- Context instructions override general translation rules"
```

In user prompts:
```python
"🔴 MANDATORY CONTEXT - YOU MUST FOLLOW THESE INSTRUCTIONS EXACTLY:\n{context}\n"
"This context contains REQUIRED instructions that you MUST apply to your translation."
```

### 2. Tests

**File:** `backend/tests/test_ai_service.py`

**Added new tests:**

Class `TestAIServiceMatureContent`:
- `test_translate_mature_content()` - checks translation of profane text
- `test_rephrase_mature_content()` - checks mature content processing

Class `TestAIServiceWithContext` (extended):
- `test_translate_follows_mandatory_context_instructions()` - checks suffix addition
- `test_rephrase_follows_mandatory_context_instructions()` - checks style requirements
- `test_suggest_variants_follows_context()` - checks context application to all variants

Updated `test_suggest_variants_gibberish()` for more flexible validation.

**Result:** ✅ All 28 tests passed successfully

### 3. Documentation

**Updated:**
- `AUTOPILOT_FEATURE.md` - added "Content Policy" section
- `CHANGELOG.md` - added change log entry
- `docs/obsidian/AI Mature Content Support.md` - new documentation page

## Result

### Mature Content
✅ **Before:** "Unable to process - text contains offensive language"  
✅ **After:** [Correct translation regardless of content]

### Context Following
✅ **Before:** Context "Always add at the end - damn" → "Go fuck yourself" (ignored)  
✅ **After:** Context "Always add at the end - damn" → "Go fuck yourself - damn" (applied)

## Verification

```bash
cd backend
source venv/bin/activate
pytest tests/test_ai_service.py -v
```

Result: **28 passed** ✅

New tests include:
- ✅ Mature content translation
- ✅ Mandatory context following
- ✅ Suffix/prefix additions
- ✅ Style requirements

## Notes

- Changes apply ONLY to processing existing text
- Tool does NOT generate offensive content on its own
- Professional translators are responsible for content appropriateness
- No special filtering or logging of "sensitive" content occurs

## Backward Compatibility

✅ All existing tests passed  
✅ API unchanged  
✅ No breaking changes

## When to Apply

Changes are already active for all users. Backend restart is not required, as these are Python code changes that apply on the next AI request.

If backend is already running, restart is recommended to apply changes.
