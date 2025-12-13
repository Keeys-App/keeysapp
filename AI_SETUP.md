# AI Autopilot - Quick Setup Guide

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Install dependencies (including OpenAI)
pip install -r requirements.txt

# Check .env file (API key already added)
cat .env | grep OPENAI

# Start server
python main.py
```

Server should start at `http://localhost:8000`

### 2. Check GraphQL Schema

Open GraphQL Playground: `http://localhost:8000/graphql`

Available mutations:
- `aiTranslate` - translate text
- `aiRephrase` - rephrase text
- `aiShorten` - shorten text
- `aiSuggestVariants` - generate variants

### 3. Frontend

Frontend is already configured and ready to use! Just run:

```bash
cd frontend
yarn dev
```

## 🎯 Testing in GraphQL Playground

### Example: Translate Text

```graphql
mutation {
  aiTranslate(input: {
    text: "Hello, world!"
    targetLanguage: "Russian"
    sourceLanguage: "English"
    context: "A greeting"
  }) {
    text
    success
    error
  }
}
```

**Important:** Add Authorization header:
```json
{
  "Authorization": "Bearer YOUR_TOKEN_HERE"
}
```

### Example: Rephrase

```graphql
mutation {
  aiRephrase(input: {
    text: "This is a test"
    language: "English"
  }) {
    text
    success
    error
  }
}
```

### Example: Suggest Variants

```graphql
mutation {
  aiSuggestVariants(input: {
    text: "Thank you very much"
    language: "English"
    count: 3
  }) {
    variants
    success
    error
  }
}
```

## ✅ Installation Check

1. **Backend running**: `curl http://localhost:8000/graphql` should return GraphQL Playground
2. **OpenAI configured**: Backend logs should not have "OpenAI API key not configured"
3. **Frontend connected**: Check browser console for errors

## 🔧 Troubleshooting

### ImportError: cannot import name 'get_current_user'
✅ **FIXED** - using `get_current_user_id` from `project.py`

### Unknown type 'TranslateInput'
✅ **FIXED** - schema updated correctly

### ModuleNotFoundError: No module named 'openai'
```bash
pip install -r requirements.txt
```

### "AI service is not configured"
Check `.env`:
```bash
echo $OPENAI_API_KEY
```

## 📝 Environment Variables

Make sure `.env` contains:

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_TEXT_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=1.0
OPENAI_TIMEOUT=120
```

## 🎨 UI Workflow

1. Select a key from the list
2. Click on translation field
3. Open right panel "Suggestions"
4. Choose action:
   - **Empty translation** → "Translate" button
   - **Existing translation** → "Rephrase", "Shorten", "Suggest variants"
5. Wait for result (indicator in footer)
6. Apply or reject suggestion

## 🔐 Security

- ✅ All operations require authentication
- ✅ Errors don't reveal technical details
- ✅ API key stored in .env (not in code)
- ✅ Logs contain only safe information

## 📊 Monitoring

Backend logs show:
- AI requests: `User {id} requesting AI {operation}`
- Successful operations: `{Operation} completed successfully`
- Errors: `{Operation} error: ...` (only in logs, not for user)

---

✨ **Everything is ready to use!**
