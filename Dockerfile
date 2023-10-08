FROM python:3.12.0-slim

WORKDIR ./

COPY ./ ./
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
