# pull official base image
FROM python:3.10

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
RUN --mount=type=cache,id=custom-pip,target=/root/.cache/pip pip cache list
RUN --mount=type=cache,id=custom-pip,target=/root/.cache/pip pip install -r prod.txt
RUN --mount=type=cache,id=custom-pip,target=/root/.cache/pip pip install -r dev.txt

# copy project
COPY . .

# collect files
RUN python src/manage.py collectstatic --clear --noinput
