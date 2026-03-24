# Новости ЦОО ФИСТ УлГТУ

Production-friendly Django 5 приложение для публикации новостей подразделения.

## Стек
- Python 3.12
- Django 5
- PostgreSQL
- Celery + Redis
- Bootstrap 5 + Django Templates
- Docker Compose

## Возможности
- Публичный список новостей с поиском, пагинацией и фильтром по тегам.
- Страница новости с просмотрами, лайками и документами.
- Подписка на конкретные теги без регистрации.
- Безопасная отписка по токену.
- Асинхронная отправка email-уведомлений при публикации новости.
- Управление новостями, тегами, файлами и подписками через Django Admin.

## Запуск
```bash
cp .env.example .env
docker-compose up --build
```

После запуска приложение доступно на `http://localhost:8000`, Mailhog — `http://localhost:8025`.

## Миграции и суперпользователь
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Тесты
```bash
docker-compose exec web pytest
```

## Celery
Worker запускается отдельным сервисом `celery` в `docker-compose.yml`.

## Сценарий работы
1. Администратор входит в `/admin/`.
2. Создает теги.
3. Создает новость и прикрепляет документы.
4. Публикует новость.
5. Celery отправляет уведомления по подписчикам тегов.
6. Гость читает новости, ставит лайки, подписывается на теги.
7. Гость может отписаться по ссылке из письма.
