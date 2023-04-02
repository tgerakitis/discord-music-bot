FROM python:3.11-slim-buster

WORKDIR /workspace/

RUN apt update \
    && apt install -yf ffmpeg

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./app ./app

ENTRYPOINT [ "./app/entrypoint.sh" ]
CMD [ "bot" ]
