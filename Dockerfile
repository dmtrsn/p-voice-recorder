# Dockerfile

# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apk update && apk add libpq
RUN apk add --virtual .build-deps gcc python3-dev musl-dev

RUN pip install --upgrade pip

# Allows docker to cache installed dependencies between builds
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Mounts the application code to the COPY . code
WORKDIR /app

RUN apk del .build-deps

# Копирование проекта
COPY . .

# Настройка записи и доступа
RUN chmod -R 777 ./


