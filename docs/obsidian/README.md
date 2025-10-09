# Locales Documentation

Добро пожаловать в документацию проекта Locales!

## 📚 Содержание

### Начало работы
- [[Quick Start]] - Быстрый старт проекта
- [[Project Structure]] - Структура проекта

### Авторизация
- [[Authentication Setup]] - Полная документация системы авторизации
- [[Authentication Cheatsheet]] - Шпаргалка по авторизации
- [[Security Best Practices]] - Рекомендации по безопасности
- [[Testing Guide]] - Руководство по тестированию

### Разработка
- [[Backend Development]] - Разработка backend
- [[Backend Organization]] - Организация папок backend
- [[Frontend Development]] - Разработка frontend
- [[Railway Deployment]] - Деплой на Railway

## 🚀 Быстрый старт

1. Клонируйте репозиторий
2. Следуйте инструкциям в [[Quick Start]]
3. Изучите [[Authentication Setup]] для понимания системы авторизации

## 🏗️ Архитектура

```
Locales/
├── backend/          # FastAPI + GraphQL + PostgreSQL
│   ├── app/         # Основной код приложения
│   └── tests/       # Тесты
└── frontend/        # React + Radix UI + Apollo Client
    └── src/         # Исходный код frontend
```

## 📖 Основные технологии

**Backend:**
- FastAPI
- Strawberry GraphQL
- PostgreSQL
- SQLAlchemy
- JWT (pyjwt)
- bcrypt

**Frontend:**
- React 19
- TypeScript
- Radix UI
- Apollo Client
- React Router

## 🔐 Система авторизации

Полноценная система регистрации и авторизации с JWT токенами и UUID для безопасности.

**Особенности:**
- ✅ UUID вместо автоинкремента (защита от enumeration)
- ✅ Безопасная обработка ошибок (SQL никогда не показывается пользователям)
- ✅ JWT токены с истечением
- ✅ bcrypt хэширование паролей

Подробнее: [[Authentication Setup]] | [[Security Best Practices]]

## 🧪 Тестирование

51 автоматический тест покрывают систему авторизации и безопасности.

**Включает:**
- Тесты моделей и сервисов
- Тесты JWT токенов
- Тесты UUID
- **Тесты обработки ошибок** (SQL никогда не попадает на frontend)
- **Тесты защиты от SQL injection**

Подробнее: [[Testing Guide]]

## 📝 Соглашения

- Код на английском
- Комментарии на английском
- UI/UX на английском
- Документация на русском (Obsidian)

## 🤝 Вклад в проект

1. Создайте feature branch
2. Внесите изменения
3. Напишите тесты
4. Создайте Pull Request

---

*Документация обновлена: 2025-10-09*

