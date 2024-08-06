FROM python:3.12.0-alpine
LABEL authors="agrytsai"

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /files/mediafiles

RUN adduser \
    --disabled-password \
    --no-create-home \
    user

RUN chown -R maine_us:user /files
RUN chmod -R 777 /files


USER user
