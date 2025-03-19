FROM python:3.9-slim-buster

WORKDIR /app

COPY src/bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/bot .

CMD ["python", "main.py"]  # Или другой файл запуска
