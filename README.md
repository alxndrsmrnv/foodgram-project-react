51.250.76.255
adminka
email:practicum@yandex.ru
password:q1q1q1q1q1q1q1q1q1q


FoodgramProject это социальная сеть для тех кто любит готовить. Здесь можно просматривать рецепты авторов или опубликовать свой рецепт.

## Стек технологий:

- Python
- Django REST Framework
- PostgresSQL
- Docker
- NGINX
- Gunicorn
- React


## Установка

Склонируйте образ на свою машину
```sh
git clone https://github.com/alxndrsmrnv/foodgram-project-react.git
```
Перейдите в папку infra и создайте .env файл. Пример:
```sh
DB_ENGINE=django.db.backends.postgresql
POSTGRES_NAME=postgres
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
DB_HOST=db
DB_PORT=5432
SECRET_KEY='secret_Key'
HOST=0:8000
```
Выполните команду:
```sh
docker-compose up
```
# Автор
Александр Смирнов