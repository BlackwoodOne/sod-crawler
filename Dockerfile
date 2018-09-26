FROM python:3.6-alpine

RUN apk update && apk add gcc linux-headers g++ make git musl-dev ffmpeg nano openjdk8-jre-base

ADD . /app
WORKDIR /app

RUN wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-02-27.zip
RUN unzip stanford-corenlp-full-2018-02-27.zip
RUN rm stanford-corenlp-full-2018-02-27.zip
RUN mv stanford-corenlp-full-2018-02-27 /app/coreNLP

RUN pip install --no-cache-dir -r requirements.txt

CMD crond -l 5 -f
