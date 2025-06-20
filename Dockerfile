FROM python:3.13.3-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src:${PYTHONPATH}"

RUN groupadd -r bot && useradd -r -g bot bot

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R bot:bot /app

USER bot

CMD ["python", "-m", "bot.main"]
