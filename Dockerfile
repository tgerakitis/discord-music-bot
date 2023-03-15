FROM python:3.9-slim-buster

WORKDIR /app

COPY ./app/ ./
RUN apt update \
    && apt install -yf ffmpeg youtube-dl \
    && pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./bot.py" ]
