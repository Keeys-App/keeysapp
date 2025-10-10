# Language Progress Bars Feature

## Обзор
Добавлена возможность отображения прогресса переводов для каждого языка отдельно на странице проекта.

## Изменения

### Backend

#### 1. Новый метод в ProjectService (`backend/app/services/project_service.py`)
```python
@staticmethod
def get_language_progress(db: Session, project_id: int) -> dict:
    """
    Get translation progress for each language in the project.
    
    Returns:
        Dict mapping language code to progress percentage and counts
    """
```

Метод эффективно вычисляет прогресс для каждого языка с помощью одного SQL-запроса:
- Получает общее количество ключей
- Подсчитывает заполненные переводы для каждого языка
- Вычисляет процент завершения

#### 2. Новый GraphQL тип (`backend/app/schemas/project.py`)
```python
@strawberry.type
class LanguageProgressType:
    """
    GraphQL type for language translation progress.
    """
    code: str              # Код языка (en, ru, de и т.д.)
    progress: int          # Процент завершения (0-100)
    completed: int         # Количество завершенных переводов
    total: int            # Общее количество ключей
```

#### 3. Обновлен ProjectType
Добавлено новое поле:
```python
language_progress: List[LanguageProgressType]
```

#### 4. Обновлена функция build_project_type
- Добавлен параметр `db: Optional[Session]`
- При наличии сессии БД вызывается `get_language_progress()`
- Для всех настроенных языков создаются объекты `LanguageProgressType`
- Если язык не имеет переводов, возвращается прогресс 0%

### Frontend

#### 1. Обновлен GraphQL запрос (`frontend/src/graphql/projects.ts`)
```graphql
languageProgress {
  code
  progress
  completed
  total
}
```

#### 2. Добавлен новый TypeScript тип
```typescript
export interface LanguageProgress {
  code: string;
  progress: number;
  completed: number;
  total: number;
}
```

#### 3. Обновлен интерфейс Project
```typescript
interface Project {
  // ... existing fields
  languageProgress: LanguageProgress[];
}
```

#### 4. Обновлен компонент ProjectPage (`frontend/src/pages/ProjectPage.tsx`)
Карточка "Languages" теперь отображает для каждого языка:
- Флаг и название языка
- Badge "Default" для языка по умолчанию
- Код языка и локаль
- **Прогресс-бар** с процентом завершения
- Количество завершенных переводов из общего числа

## UI Изменения

### До:
```
🇬🇧 English                    [Default]
    en · en-US123
```

### После:
```
🇬🇧 English [Default]          20%
    en · en-US123
    [████░░░░░░░░░░░░░░░░] 
    5 of 25 translations
```

## Производительность

- Используется эффективный SQL-запрос с GROUP BY
- Данные загружаются только когда запрашивается детальная информация о проекте
- Не влияет на скорость списка проектов
- Все расчеты выполняются на стороне базы данных

## Совместимость

- ✅ Обратно совместимо с существующими проектами
- ✅ Корректно обрабатывает проекты без переводов (0%)
- ✅ Корректно обрабатывает новые языки без переводов
- ✅ Все изменения покрыты TypeScript типами

## Тестирование

Рекомендуется протестировать:
1. Проект без ключей (все языки должны показывать 0%)
2. Проект с частично заполненными переводами
3. Проект с полностью заполненными переводами (100%)
4. Добавление нового языка к существующему проекту
5. Удаление переводов и обновление прогресса

