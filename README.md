# vet_clinic_system

Система управления ветеринарной клиникой

## Описание

Данное приложение предназначено для автоматизации работы ветеринарной клиники: управление приёмами, учёт животных, сотрудников, формирование отчётов и многое другое. Используются две базы данных — PostgreSQL (для персонала, приёмов и других сущностей) и MongoDB (для хранения информации о животных). Интерфейс реализован на PyQt5.

## Архитектура проекта

```
vet_clinic_system/
│
├── main.py                      # Точка входа
├── .env                         # Настройки подключения
├── requirements.txt             # Зависимости
│
├── database/
│   ├── postgres_connector.py    # Подключение к PostgreSQL
│   ├── mongodb_connector.py     # Подключение к MongoDB
│   ├── models_pg.py             # Классы и SQL-запросы к PostgreSQL
│   └── models_mongo.py          # Операции с MongoDB (животные)
│
├── ui/
│   ├── login_window.py          # Окно входа
│   ├── main_window.py           # Главное окно
│   ├── animals_widget.py        # Работа с животными
│   ├── appointments_widget.py   # Приёмы
│   ├── staff_widget.py          # Сотрудники
│   └── reports_widget.py        # Отчёты
│
├── logic/
│   ├── auth_manager.py          # Авторизация и роли
│   ├── reports_generator.py     # Генерация PDF/CSV
│   ├── calendar_utils.py        # Работа с календарём приёмов
│   └── file_handler.py          # Загрузка и хранение файлов
│
└── assets/
    ├── icons/                   # Иконки
    ├── uploads/                 # Прикреплённые файлы
    └── styles.qss               # Стили Qt (если есть)
```

## Быстрый старт

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/Vegas30/vet_clinic_system.git
    cd vet_clinic_system
    ```

2. Создайте и настройте файл `.env` на основе примера, укажите параметры подключения к PostgreSQL и MongoDB.

3. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

4. Запустите приложение:
    ```bash
    python main.py
    ```

## Основные возможности

- Авторизация пользователей и разграничение ролей
- Учёт животных (MongoDB)
- Управление приёмами, сотрудниками, отчётами (PostgreSQL)
- Генерация отчётов в формате PDF/CSV
- Загрузка и хранение файлов (например, фото животных)
- Современный интерфейс на PyQt6

## Контакты

Разработчик: [ваше имя или ссылка на GitHub]

## Лицензия

[Укажите лицензию проекта, если требуется]