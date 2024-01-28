# pull official base image
FROM python:3.12.0-alpine

# set work directory

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/backend

RUN apk update
# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
ENV FLASK_APP = 'manage.py'
ENV FLASK_ENV = 'development'
ENV FLASK_DEBUG = 1

ENTRYPOINT ["python"]
CMD ["manage.py"]