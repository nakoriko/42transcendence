FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .

RUN pip install -r requirements.txt
COPY . .

CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 core.asgi:application"]