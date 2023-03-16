FROM python:3.10-slim-buster

WORKDIR /app

RUN apt update \
    && apt install -yf ffmpeg wget \
    && wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/local/bin/youtube-dl \
    && chmod a+rx /usr/local/bin/youtube-dl

COPY ./app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./

CMD [ "python", "./bot.py" ]
