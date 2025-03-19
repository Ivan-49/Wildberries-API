FROM python:3.9-slim-buster

WORKDIR /app

COPY src/API/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/API .

CMD ["python", "main.py"]  # Или другой файл запуска
