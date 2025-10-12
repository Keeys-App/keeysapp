# AI Variable Preservation

## Overview

AI translation service automatically preserves template variables (placeholders) in curly braces during all operations.

## What are Template Variables?

Template variables are placeholders in translation strings that get replaced with dynamic values at runtime:

```
"Hello {name}, next payment: {date}"
"Your order {orderId} has {count} items"
```

## How it Works

The AI service (`backend/app/services/ai_service.py`) has explicit instructions in system prompts to:
1. **Never translate** variable names inside curly braces
2. **Preserve them exactly** as they appear in the source text
3. Treat them as code placeholders, not translatable content

## Examples

### Translation
```
EN: "Welcome {username}!"
ES: "¡Bienvenido {username}!"  ✅ Variable preserved
```

### Rephrasing
```
Original: "Your payment of {amount} is due"
Rephrased: "Payment due: {amount}"  ✅ Variable preserved
```

### Shortening
```
Original: "Please pay {amount} by {date}"
Shortened: "Pay {amount} by {date}"  ✅ Variables preserved
```

### Variants
All generated variants keep the same variables:
```
"Thanks {name}!"
"Thank you {name}!"
"Appreciate it {name}!"
```

## Supported Variable Formats

- Simple: `{name}`, `{date}`, `{count}`
- With underscores: `{user_id}`, `{order_number}`
- With numbers: `{item1}`, `{value2}`
- CamelCase: `{orderId}`, `{userName}`

## Testing

Run tests to verify variable preservation:

```bash
cd backend
source venv/bin/activate
pytest tests/test_ai_service.py::TestAIServiceVariablePreservation -v
```

## Implementation Details

### Methods Affected

All AI service methods preserve variables:
- `translate()` - Translation between languages
- `rephrase()` - Rephrasing text
- `shorten()` - Shortening text
- `suggest_variants()` - Generating alternative wordings

### System Prompt Rules

Each method includes these critical rules:

```python
"- CRITICAL: Preserve ALL template variables in curly braces like {name}, {date}, {count}, etc. exactly as they are\n"
"- NEVER translate or modify variable names inside curly braces - they are code placeholders"
```

## When to Use Variables

Use template variables when:
- You need dynamic values (dates, names, counts, etc.)
- The same translation works in multiple contexts with different values
- You want to maintain consistency across languages

Example:
```json
{
  "welcome_message": "Welcome back, {username}!",
  "order_status": "Order {orderId} is {status}",
  "items_count": "You have {count} items in your cart"
}
```

## Related

- [[AI Service]] - Main AI service documentation
- [[Testing Guide]] - How to run tests
- See `AI_VARIABLE_PRESERVATION_FIX.md` for detailed fix documentation

