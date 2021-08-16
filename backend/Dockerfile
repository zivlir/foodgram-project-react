FROM python:3.8.5-slim

WORKDIR /code

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r /code/requirements.txt

COPY . /code

CMD gunicorn foodgram_api.wsgi:application --bind 0.0.0.0:8000
