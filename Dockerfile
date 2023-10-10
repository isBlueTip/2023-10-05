FROM python:3.12.0-slim

COPY . .
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
