# pull official base image
FROM python:3.9

# set work directory
WORKDIR /usr/src

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH src

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements/base.txt .
COPY ./requirements/test.txt .
COPY ./requirements/dev.txt .
COPY ./requirements/prod.txt .
RUN pip install -r prod.txt
RUN pip install -r dev.txt

# copy project
COPY . .

# collect files
RUN python src/manage.py collectstatic --clear --noinput
