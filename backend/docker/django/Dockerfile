FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    sudo && \
    curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash - && apt-get install -y \
    gcc \
    git

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app
