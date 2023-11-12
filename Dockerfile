FROM python:3

WORKDIR /code

COPY req_old.txt /code/

RUN pip install -r /code/requirements.txt

COPY . .
