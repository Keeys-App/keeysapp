# AI Autopilot Feature

## Overview

The AI Autopilot feature provides intelligent translation assistance powered by OpenAI GPT models. It helps users translate, rephrase, shorten, and generate variants of translations.

## Features

### 1. **Translate** 🌐
Automatically translate text from the default language to the target language.
- Uses context from key description
- Preserves natural language flow
- Supports all project languages

### 2. **Rephrase** ✏️
Improve existing translations by rephrasing them.
- Maintains original meaning
- Makes text more natural and fluent
- Context-aware

### 3. **Shorten** ✂️
Create concise versions of translations.
- Preserves key meaning
- Reduces text length
- Maintains clarity

### 4. **Suggest Variants** 🔄
Generate multiple alternative versions of a translation.
- Provides 3 different variants
- Each with slightly different tone or wording
- Helps choose the best option

## Configuration

### Backend Setup

1. Add OpenAI API key to your `.env` file:

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_TEXT_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=1.0
OPENAI_TIMEOUT=120
```

2. Install dependencies:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Setup

No additional configuration needed. The frontend automatically uses the GraphQL API.

## Architecture

### Backend

- **Service**: `app/services/ai_service.py`
  - `AIService` class with async methods
  - Error handling with user-friendly messages
  - Logging for debugging

- **GraphQL Schema**: `app/schemas/ai.py`
  - `TranslateInput`, `RephraseInput`, `ShortenInput`, `SuggestVariantsInput`
  - `TranslationResult`, `VariantsResult`
  - `AIMutation` class with resolvers

- **Config**: `app/core/config.py`
  - OpenAI settings
  - Model configuration
  - Timeout and token limits

### Frontend

- **GraphQL**: `frontend/src/graphql/ai.ts`
  - Mutations: `AI_TRANSLATE`, `AI_REPHRASE`, `AI_SHORTEN`, `AI_SUGGEST_VARIANTS`
  - Type definitions

- **Components**:
  - `AutopilotCard`: Main action buttons
  - `AutopilotSuggestion`: Display AI suggestions
  - `KeySuggestions`: Main container with logic

## Usage

### User Flow

1. **Select a translation key** from the keys list
2. **Click on a translation field** to edit
3. **Open the Suggestions panel** (right sidebar)
4. **Choose an action**:
   - Empty translation → "Translate" button
   - Existing translation → "Rephrase", "Shorten", "Suggest variants"
5. **Review AI suggestion**
6. **Apply or discard** the suggestion

### UI States

- **Disabled**: No language selected
- **Translate**: Empty translation field
- **Enhance**: Existing translation with improvement options

## Error Handling

### Backend

- Generic user-friendly error messages (security rule #1)
- Detailed logging for debugging
- Exception handling for API failures

### Frontend

- Toast notifications for success/error
- Global saving indicator
- Disabled buttons during loading

## Performance

- **Loading states**: Global saving indicator in footer
- **Async operations**: Non-blocking UI
- **Smart caching**: Clear suggestions on language change

## Security

- **Authentication required**: All AI operations check user authentication
- **Error messages**: Never expose technical details to users
- **API key**: Stored securely in environment variables

## Limitations

- Requires OpenAI API key
- Internet connection needed
- API rate limits apply
- Costs per API call

## Future Enhancements

- [ ] Context editing interface
- [ ] Apply suggestion directly to translation field
- [ ] Batch translation for multiple keys
- [ ] Custom AI prompts
- [ ] Alternative AI providers (Anthropic, etc.)
- [ ] Translation memory integration

## Troubleshooting

### "AI service is not configured"
- Check that `OPENAI_API_KEY` is set in `.env`
- Restart backend server

### "Translation failed. Please try again."
- Check internet connection
- Verify API key is valid
- Check OpenAI API status
- Review backend logs for details

### Slow responses
- Increase `OPENAI_TIMEOUT` in config
- Consider using a faster model
- Check network connection

## Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest tests/test_ai_service.py
```

### Manual Testing
1. Set up valid OpenAI API key
2. Create a test project with keys
3. Try each AI operation
4. Verify error handling with invalid inputs

## Costs

OpenAI API charges per token. Approximate costs with `gpt-4o-mini`:
- Translate: ~$0.0001 - $0.0005 per request
- Rephrase: ~$0.0001 - $0.0003 per request
- Shorten: ~$0.0001 - $0.0003 per request
- Variants: ~$0.0002 - $0.0008 per request

Monitor usage via OpenAI dashboard.

