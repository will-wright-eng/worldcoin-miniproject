FROM python:3.9-slim

RUN mkdir /app
WORKDIR /app

# RUN apt update
ENV MONGODB_URI=mongodb://mongo:27017/machine_learning_pipeline

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
