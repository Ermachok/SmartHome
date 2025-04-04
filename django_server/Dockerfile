FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc python3-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir netifaces

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/media/photos
RUN chmod -R 777 /app/media

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

