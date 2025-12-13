# AI JSON Validation - Structured Output

## Problem

When working with gibberish text (e.g., "asdasdasd"), AI could return apologies in target language:
```
Lo siento, pero la entrada "asdasdasd" no contiene un significado claro...
```

Such responses were shown as valid translations, which was incorrect.

## Solution

Transition to **structured JSON output** from OpenAI. Now AI itself determines if it can perform the task.

## Response Format

### For translate, rephrase, shorten:
```json
{
  "success": true,
  "result": "Translated/rephrased/shortened text",
  "reason": "optional reason if success=false"
}
```

### For suggest_variants:
```json
{
  "success": true,
  "variants": ["variant 1", "variant 2", "variant 3"],
  "reason": "optional reason if success=false"
}
```

## Examples

### ✅ Success Case (valid text)
**Input:** "Hello, world!"
**Response:**
```json
{
  "success": true,
  "result": "Hola, mundo!"
}
```
→ Shown as suggestion

### ❌ Failure Case (gibberish)
**Input:** "asdasdasd"
**Response:**
```json
{
  "success": false,
  "result": "",
  "reason": "The input appears to be random characters without clear meaning"
}
```
→ Shows error: "Unable to translate this text. Please try with different content."

## Benefits

1. **Universal** - works in all languages
2. **AI decides** - no need to write patterns for each language
3. **Clean results** - never shows apologies/explanations as translations
4. **Logging** - backend logs show AI refusal reason

## Updated Methods

### AIService (backend/app/services/ai_service.py)

**translate()**
```python
response_format={"type": "json_object"}
# Parse JSON
response_data = json.loads(response_text)
if not response_data.get("success"):
    raise Exception("Unable to translate...")
return response_data["result"]
```

**rephrase()**, **shorten()** - same

**suggest_variants()**
```python
response_format={"type": "json_object"}
response_data = json.loads(response_text)
if not response_data.get("success"):
    raise Exception("Unable to generate variants...")
return response_data["variants"][:count]
```

## System Prompts

All prompts updated:
```
"You are a professional translator. "
"Respond ONLY with valid JSON in this exact format:
{"success": true/false, "result": "...", "reason": "..."}

Rules:
- If text is translatable, set success=true and provide translation
- If text is gibberish, set success=false and explain in reason
- NEVER include apologies or explanations in result field
```

## Testing

### Run Tests
```bash
cd backend
source venv/bin/activate
pytest tests/test_ai_service.py -v
```

### Test Cases

**test_translate_valid_text**
- Translates "Hello, world!" to Spanish
- Verifies result doesn't contain apologies

**test_translate_gibberish**
- Attempts to translate "asdasdasd"
- Should throw Exception
- Should not return "Lo siento..."

**test_rephrase_gibberish**
- Attempts to rephrase "xyzxyzxyz"
- Should throw Exception

**test_suggest_variants_gibberish**
- Attempts to generate variants for "qweasdzxc"
- Should throw Exception

**test_translate_to_russian/chinese/arabic**
- Verifies works in different languages

### Manual Testing

1. Open key in UI
2. Select language for translation
3. Try translating gibberish text (e.g., "asdasd")
4. Should show error, not card with apologies
5. Try normal text - should show card

## Breaking Changes

### Backend API

No changes in GraphQL API - everything works as before.

### Frontend

No changes required - handled through existing `success` field logic.

## Logging

### Success Case
```
INFO: Translation completed successfully
```

### Gibberish
```
WARNING: AI could not translate: The input appears to be random characters
INFO: Translation failed. Please try again.
```

## Migrations

No migrations required - this is only change in AI response processing logic.

## Monitoring

In production logs look for:
- `WARNING: AI could not translate/rephrase/shorten` - AI refused
- Frequency of such warnings shows input data quality

## Recommendations

- Use frontend validation before sending to AI
- Minimum text length: 2 characters
- Prohibit sending only spaces/special characters
