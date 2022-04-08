FROM python:3.9.5
WORKDIR /app
COPY . .
RUN ls
RUN pip install -r /app/foodgram/requirements.txt
CMD gunicorn foodgram_project.wsgi:application --bind 0.0.0.0:8000