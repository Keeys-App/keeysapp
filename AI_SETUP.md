# AI Autopilot - Quick Setup Guide

## 🚀 Быстрый запуск

### 1. Backend Setup

```bash
cd backend

# Активировать virtual environment
source venv/bin/activate

# Установить зависимости (включая OpenAI)
pip install -r requirements.txt

# Проверить .env файл (API key уже добавлен)
cat .env | grep OPENAI

# Запустить сервер
python main.py
```

Сервер должен запуститься на `http://localhost:8000`

### 2. Проверка GraphQL Schema

Откройте GraphQL Playground: `http://localhost:8000/graphql`

Доступные мутации:
- `aiTranslate` - перевод текста
- `aiRephrase` - перефразирование
- `aiShorten` - сокращение текста
- `aiSuggestVariants` - генерация вариантов

### 3. Frontend

Frontend уже настроен и готов к работе! Просто запустите:

```bash
cd frontend
yarn dev
```

## 🎯 Тестирование в GraphQL Playground

### Пример: Перевод текста

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

**Важно:** Добавьте Authorization header:
```json
{
  "Authorization": "Bearer YOUR_TOKEN_HERE"
}
```

### Пример: Rephrase

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

### Пример: Suggest Variants

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

## ✅ Проверка установки

1. **Backend запущен**: `curl http://localhost:8000/graphql` должен вернуть GraphQL Playground
2. **OpenAI настроен**: В логах backend не должно быть "OpenAI API key not configured"
3. **Frontend подключён**: Проверьте браузер консоль на ошибки

## 🔧 Troubleshooting

### ImportError: cannot import name 'get_current_user'
✅ **ИСПРАВЛЕНО** - использован `get_current_user_id` из `project.py`

### Unknown type 'TranslateInput'
✅ **ИСПРАВЛЕНО** - schema обновлена правильно

### ModuleNotFoundError: No module named 'openai'
```bash
pip install -r requirements.txt
```

### "AI service is not configured"
Проверьте `.env`:
```bash
echo $OPENAI_API_KEY
```

## 📝 Переменные окружения

Убедитесь, что в `.env` есть:

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_TEXT_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=1.0
OPENAI_TIMEOUT=120
```

## 🎨 UI Workflow

1. Выберите ключ из списка
2. Кликните на поле перевода
3. Откройте правую панель "Suggestions"
4. Выберите действие:
   - **Пустой перевод** → кнопка "Translate"
   - **Существующий перевод** → "Rephrase", "Shorten", "Suggest variants"
5. Дождитесь результата (индикатор в footer)
6. Примените или отклоните предложение

## 🔐 Безопасность

- ✅ Все операции требуют аутентификации
- ✅ Ошибки не раскрывают технические детали
- ✅ API key хранится в .env (не в коде)
- ✅ Логи содержат только безопасную информацию

## 📊 Мониторинг

Логи backend показывают:
- Запросы к AI: `User {id} requesting AI {operation}`
- Успешные операции: `{Operation} completed successfully`
- Ошибки: `{Operation} error: ...` (только в логах, не для пользователя)

---

✨ **Всё готово к использованию!**

