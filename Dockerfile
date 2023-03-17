FROM python:3.10-slim-buster

WORKDIR /app

RUN apt update \
    && apt install -yf ffmpeg

COPY ./app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/

ENTRYPOINT [ "entrypoint.sh" ]
CMD [ "bot.py" ]
