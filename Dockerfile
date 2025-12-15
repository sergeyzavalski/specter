FROM python:3.13-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt update \
    && apt install -y \
        gcc  \
        libc-dev \
    && pip3 install --no-cache-dir -r requirements.txt \
    && apt clean

COPY app/ ./

CMD ["python", "manage.py"]


