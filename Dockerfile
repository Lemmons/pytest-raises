FROM python:3.6-alpine

RUN apk add --no-cache git

COPY . /src/pytest-raises

WORKDIR /src/pytest-raises

RUN pip install .[develop]
