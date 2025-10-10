# Error Handling Best Practices

## Критически важно ⚠️

**НИКОГДА не показывайте технические ошибки пользователю напрямую!**

Это нарушение безопасности и плохой UX.

## Принципы обработки ошибок

### ❌ Неправильно

```typescript
onError: (error) => {
  toast(`Error: ${error.message}`);
  // Технические детали попадают к пользователю!
}

// Или
catch (err) => {
  setError(err.message);
  // SQL ошибки, стектрейсы - все видит пользователь!
}
```

### ✅ Правильно

```typescript
import { getUserFriendlyErrorMessage } from '@/lib/utils';

onError: (error) => {
  const message = getUserFriendlyErrorMessage(
    error, 
    'Failed to update. Please try again.'
  );
  toast.error(message);
}
```

## Функция getUserFriendlyErrorMessage

Централизованная функция в `lib/utils.ts` для обработки всех ошибок GraphQL.

### Что она делает

1. **Логирует технические детали** в консоль для разработчиков
2. **Обрабатывает специфичные коды ошибок** (UNAUTHENTICATED, FORBIDDEN, и т.д.)
3. **Фильтрует безопасные сообщения** (например "already exists")
4. **Возвращает fallback** для всех остальных случаев

### Использование

```typescript
import { getUserFriendlyErrorMessage } from '@/lib/utils';

const message = getUserFriendlyErrorMessage(
  error,
  'Fallback message if nothing specific matches'
);
toast.error(message);
```

## Что НЕ должно попадать пользователю

- ❌ Стектрейсы
- ❌ SQL запросы/ошибки
- ❌ Названия таблиц БД
- ❌ Названия переменных GraphQL
- ❌ Пути к файлам сервера
- ❌ Версии библиотек
- ❌ IP адреса
- ❌ Любые технические детали реализации

## Что МОЖНО показывать

- ✅ "Failed to create project"
- ✅ "Invalid input data"
- ✅ "This key already exists"
- ✅ "Unable to connect to server"
- ✅ "Please try again later"

## Правила для всех компонентов

### 1. Apollo Client Mutations

```typescript
const [mutation] = useMutation(MUTATION, {
  onCompleted: () => {
    toast.success('Operation completed successfully');
  },
  onError: (error) => {
    // ✅ ВСЕГДА используем getUserFriendlyErrorMessage
    const message = getUserFriendlyErrorMessage(error, 'Operation failed');
    toast.error(message);
  },
});
```

### 2. Try-Catch блоки

```typescript
try {
  // ... code
} catch (err) {
  // ✅ ВСЕГДА обрабатываем через getUserFriendlyErrorMessage
  const message = getUserFriendlyErrorMessage(
    err as Error, 
    'Operation failed'
  );
  setError(message);
}
```

### 3. Логирование для разработчиков

```typescript
// ✅ Логируем ВСЁ для разработки
console.error('Technical details:', error);
console.error('Stack:', error.stack);
console.error('GraphQL errors:', error.graphQLErrors);

// ❌ Но пользователю показываем только безопасное
toast.error(getUserFriendlyErrorMessage(error, fallback));
```

## Backend: Безопасные сообщения об ошибках

### ✅ Хорошие сообщения от бэкенда

```python
raise ValueError("Project with this name already exists")
raise ValueError("Invalid language code")
raise PermissionError("You don't have permission to edit this project")
```

### ❌ Плохие сообщения от бэкенда

```python
raise Exception(f"Variable '$input' got invalid value...")  # Технические детали
raise Exception(f"SQL Error: {str(e)}")  # SQL ошибки
raise Exception(f"Failed at line 145 in service.py")  # Пути к файлам
```

## Проверка перед commit

Перед каждым коммитом проверяйте:

```bash
# Поиск прямого использования error.message
grep -r "error\.message" frontend/src/components/

# Поиск toast с error
grep -r "toast.*error\." frontend/src/components/

# Поиск console.error без getUserFriendlyErrorMessage после
grep -r "console\.error" frontend/src/components/
```

## Существующие реализации

Все следующие компоненты уже используют правильную обработку ошибок:

- ✅ `TranslationEditor.tsx`
- ✅ `CreateKeyDialog.tsx`
- ✅ `CreateProjectDialog.tsx`
- ✅ `EditProjectDialog.tsx`
- ✅ `ProjectList.tsx`
- ✅ `LoginForm.tsx`
- ✅ `RegisterForm.tsx`

Используйте их как reference при создании новых компонентов.

## Тестирование

При тестировании проверяйте:

1. **Отключите бэкенд** - должно показываться "Unable to connect to server"
2. **Невалидные данные** - должны показываться понятные сообщения
3. **Ошибки БД** - НЕ должны показываться технические детали
4. **GraphQL ошибки** - должны быть обработаны и показаны user-friendly

## Дополнительная безопасность

### Apollo Client errorLink

В `lib/apollo.ts` настроен errorLink, который:

1. Автоматически ловит ошибки аутентификации
2. Очищает токены при 401/403
3. Редиректит на страницу логина

Это дополнительный уровень защиты, но **НЕ заменяет** обработку в компонентах!

## Контрольный список

- [ ] Все mutations используют `getUserFriendlyErrorMessage` в `onError`
- [ ] Все try-catch блоки обрабатывают ошибки через `getUserFriendlyErrorMessage`
- [ ] Технические ошибки логируются через `console.error` для разработки
- [ ] Пользователь видит только понятные сообщения
- [ ] Нет прямого использования `error.message` в toast/alert
- [ ] Бэкенд не отдает технические детали в сообщениях об ошибках

---

**Помните:** Каждая техническая ошибка, показанная пользователю - это:
1. **Вектор атаки** для хакеров
2. **Плохой UX** для пользователей
3. **Потенциальная утечка данных**

Всегда обрабатывайте ошибки правильно!

