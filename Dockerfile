FROM python:3.10-slim-bookworm

RUN apt update -y && apt install -y awscli
WORKDIR /app

COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python3", "app.py"]