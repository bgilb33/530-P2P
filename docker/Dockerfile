FROM python:3.10

WORKDIR /app

RUN pip install redis

COPY . .

CMD ["python", "client.py"]
