
FROM python:3.8
ENV PYTHONBUFFERED 1

WORKDIR /app
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install python3-dev default-libmysqlclient-dev build-essential -y

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

RUN python src/manage.py collectstatic --noinput
CMD gunicorn core.wsgi --chdir src --bind 0.0.0.0 --workers=4 -t 0 --preload --log-file -
