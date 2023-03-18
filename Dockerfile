FROM python:3.10-slim-buster

WORKDIR /workspace

RUN apt update \
    && apt install -yf ffmpeg

COPY ./app/requirements.txt ./app/requirements.txt
RUN pip install --no-cache-dir -r ./app/requirements.txt

COPY ./app /workspace/app/

ENTRYPOINT [ "/workspace/app/entrypoint.sh" ]
CMD [ "bot" ]
