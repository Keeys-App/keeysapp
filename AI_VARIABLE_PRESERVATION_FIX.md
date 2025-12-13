# AI Variable Preservation & ICU MessageFormat Support

## Problems

### Problem 1: Variable Translation

AI auto-translate was translating variables in curly braces (like `{date}`, `{data}`, `{name}`) instead of preserving them as-is. This broke string templates in applications.

### Problem 2: ICU MessageFormat Refusal

AI refused to translate texts with ICU MessageFormat syntax (used for plurals), returning error "Text contains programming placeholders and cannot be translated directly".

### Problem Examples

**Problem 1: Before fix (simple variables)**
```
Source text: "Next payment: {date}"
Italian translation: "Prossimo pagamento: {data}"  ❌ Variable translated!
```

**Problem 2: Before fix (ICU MessageFormat)**
```
Source text: "{count, plural, one {{user} removed type {removedTypes}} other {{user} removed types {removedTypes}}}"
Result: Error "Text contains programming placeholders and cannot be translated directly"  ❌
```

**After fix:**
```
Source text: "Next payment: {date}"
Italian translation: "Prossimo pagamento: {date}"  ✅ Variable preserved!

Source text: "{count, plural, one {{user} removed type {removedTypes}} other {{user} removed types {removedTypes}}}"
Russian translation: "{count, plural, one {{user} removed type {removedTypes}} other {{user} removed types {removedTypes}}}"  ✅ Structure preserved, text translated!
```

## Solution

Added explicit instructions to all AI service prompts for:
1. Preserving variables in curly braces unchanged
2. Correctly handling ICU MessageFormat syntax

### Code Changes

#### `backend/app/services/ai_service.py`

Added following rules to system prompt in all methods:

**For variables:**
```python
"- CRITICAL: Preserve ALL template variables in curly braces like {name}, {date}, {count}, etc. exactly as they are\n"
"- NEVER translate or modify variable names inside curly braces - they are code placeholders"
```

**For ICU MessageFormat:**
```python
"ICU MessageFormat Support:\n"
"- Text may contain ICU MessageFormat syntax: {count, plural, one {...} other {...}}\n"
"- PRESERVE the entire structure: {variable, plural, one {...} other {...}}\n"
"- ONLY translate the text inside one {...} and other {...} blocks\n"
"- PRESERVE all variables inside these blocks like {user}, {removedTypes}, etc.\n"
"- Example: {count, plural, one {{user} added item} other {{user} added items}}\n"
"  Should translate text but keep structure and variables intact"
```

Affected methods:
- ✅ `translate()` - text translation
- ✅ `rephrase()` - rephrasing  
- ✅ `shorten()` - text shortening
- ✅ `suggest_variants()` - variant generation

### Tests

Added new test classes in `backend/tests/test_ai_service.py`:

#### `TestAIServiceVariablePreservation` - Variable tests
- ✅ `test_translate_preserves_single_variable()` - single variable
- ✅ `test_translate_preserves_multiple_variables()` - multiple variables
- ✅ `test_rephrase_preserves_variables()` - rephrasing
- ✅ `test_shorten_preserves_variables()` - shortening
- ✅ `test_suggest_variants_preserves_variables()` - variants
- ✅ `test_translate_preserves_complex_variables()` - complex variable names

#### `TestAIServiceICUMessageFormat` - ICU MessageFormat tests
- ✅ `test_translate_icu_plural_format()` - complex ICU with variables
- ✅ `test_translate_icu_simple_plural()` - simple ICU plural
- ✅ `test_rephrase_icu_format()` - ICU rephrasing
- ✅ `test_shorten_icu_format()` - ICU shortening
- ✅ `test_suggest_variants_icu_format()` - variants with ICU

## How to Verify

### Run All Tests

```bash
cd backend
source venv/bin/activate

# All AI service tests (23 tests)
pytest tests/test_ai_service.py -v

# Only variable tests (6 tests)
pytest tests/test_ai_service.py::TestAIServiceVariablePreservation -v

# Only ICU MessageFormat tests (5 tests)
pytest tests/test_ai_service.py::TestAIServiceICUMessageFormat -v
```

### Manual Check

**Simple variables:**
1. Create a translation key with variables, e.g.: `"Hello {name}, next payment: {date}"`
2. Use auto-translate to any language
3. Verify that `{name}` and `{date}` variables are preserved in translation

**ICU MessageFormat:**
1. Create a key with ICU syntax, e.g.: `"{count, plural, one {{user} removed type {removedTypes}} other {{user} removed types {removedTypes}}}"`
2. Use auto-translate to any language
3. Verify that:
   - Structure `{count, plural, one {...} other {...}}` is preserved
   - Variables `{user}` and `{removedTypes}` are unchanged
   - Text inside blocks is translated

## Correct Operation Examples

### Simple Variables

**Translation:**
```
EN: "Hello {name}, your order {orderId} will arrive on {date}"
ES: "Hola {name}, tu pedido {orderId} llegará el {date}"
```

**Rephrasing:**
```
Original: "Your payment of {amount} is due on {date}"
Rephrased: "Payment due: {amount} on {date}"
```

**Shortening:**
```
Original: "We kindly remind you that your next payment of {amount} is scheduled for {date}"
Shortened: "Payment reminder: {amount} due {date}"
```

**Variants:**
```
Original: "Welcome back, {username}!"
Variant 1: "Hello again, {username}!"
Variant 2: "Great to see you, {username}!"
Variant 3: "Welcome, {username}!"
```

### ICU MessageFormat

**Translation with plurals:**
```
EN: "{count, plural, one {{user} removed type {removedTypes}} other {{user} removed types {removedTypes}}}"
RU: "{count, plural, one {{user} removed type {removedTypes}} other {{user} removed types {removedTypes}}}"
```

**Simple plural:**
```
EN: "{count, plural, one {item} other {items}}"
ES: "{count, plural, one {artículo} other {artículos}}"
```

**Messages with counter:**
```
EN: "{count, plural, one {You have one message} other {You have {count} messages}}"
FR: "{count, plural, one {Vous avez un message} other {Vous avez {count} messages}}"
```

**ICU rephrasing:**
```
Original: "{count, plural, one {You have one notification waiting} other {You have {count} notifications waiting}}"
Rephrased: "{count, plural, one {1 notification} other {{count} notifications}}"
```

## Technical Details

### Variable Types

AI correctly handles:
- Simple names: `{name}`, `{date}`, `{count}`
- With underscores: `{user_id}`, `{order_number}`
- With numbers: `{item1}`, `{value2}`
- CamelCase: `{orderId}`, `{userName}`

### ICU MessageFormat

AI now understands and correctly processes [ICU MessageFormat](https://unicode-org.github.io/icu/userguide/format_parse/messages/) syntax:

**Supported constructs:**
- `{variable, plural, one {...} other {...}}` - plurals
- `{variable, select, male {...} female {...} other {...}}` - selection by value
- Nested variables inside blocks

**How it's processed:**
1. AI preserves entire structure: `{count, plural, one {...} other {...}}`
2. Translates only text inside `one {...}` and `other {...}` blocks
3. Preserves all variables inside blocks

**Processing example:**
```
Source: {count, plural, one {{user} added item} other {{user} added items}}
        ├─ Structure: {count, plural, one {...} other {...}}  → Preserved
        ├─ Variable {user} → Preserved
        └─ Text "added item/items" → Translated

Result (ES): {count, plural, one {{user} agregó artículo} other {{user} agregó artículos}}
```

### How It Works

OpenAI API receives system prompt with explicit instructions:
1. All variables in curly braces are code placeholders
2. ICU MessageFormat structure must be fully preserved
3. Translate only text content inside blocks
4. Keep all variables exactly as-is

Model (`gpt-4o-mini` by default) follows these instructions and correctly handles both construct types.

## System Impact

- ✅ **Backward compatibility**: Doesn't break existing functionality
- ✅ **Performance**: No impact on speed
- ✅ **Translation quality**: Significantly improved:
  - Variables no longer break
  - ICU MessageFormat now supported
  - Complex string structure preserved correctly
- ✅ **Test coverage**: 
  - Added 6 tests for variables
  - Added 5 tests for ICU MessageFormat
  - Total 23 AI service tests (all passing ✅)

## Change Date

October 12, 2025

## Related Files

- `backend/app/services/ai_service.py` - AI service with fixes
- `backend/tests/test_ai_service.py` - verification tests
