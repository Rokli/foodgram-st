# Foodgram - Российский сервис для любителей кулинарии! 
 
## О проекте 
Foodgram - это платформа, где каждый может делиться своими рецептами, добавлять понравившиеся блюда в избранное, следить за кулинарными авторами и составлять список покупок для выбранных рецептов. 
 
Проект представляет собой REST API, упакованный в Docker для простого и быстрого развертывания. 
 
## Технологии 
- Python 
- Django 
- Django REST Framework 
- PostgreSQL 
- Nginx 
- Docker 
- GitHub Actions (для CI/CD) 
 
## Требования 
- Установленный Docker 
- Docker Compose 
 
## Установка и запуск 
 
### 1. Клонируем репозиторий 
```bash 
git clone https://github.com/Rokli/foodgram-st.git 
cd foodgram-st 
``` 
 
### 2. Настройка .env 
Создайте файл .env в корневой папке проекта и заполните его следующими переменными: 
 
DJANGO_SETTINGS_MODULE=foodgram.settings 
SECRET_KEY=ваш_ключ 
DEBUG=False 
ALLOWED_HOSTS="localhost 127.0.0.1 backend frontend foodgram.ru" 
POSTGRES_DB=foodgram 
POSTGRES_USER=foodgram 
POSTGRES_PASSWORD=foodpass 
DB_HOST=foodgram-db 
DB_PORT=5432 
 
### 3. Запуск проекта 
 
docker-compose up --build         # Сборка и запуск контейнеров 
 
### Конец! 
Foodgram готов к работе! 
Погрузитесь в мир кулинарии, делитесь рецептами и вдохновляйтесь новыми идеями! 
