FROM python:3.10-slim-buster

WORKDIR /workspace/app

RUN apt update \
    && apt install -yf ffmpeg

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./app ./

ENTRYPOINT [ "./entrypoint.sh" ]
CMD [ "bot" ]
