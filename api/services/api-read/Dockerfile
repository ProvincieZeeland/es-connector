###########
# BUILDER #
###########

# pull official base image
#FROM python:3.10.7-slim-buster as builder
FROM python:3.12-rc-slim as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Update pip
RUN pip install --upgrade pip

# install dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

#########
# FINAL #
#########
#FROM python:3.10.7-slim-buster
FROM python:3.12-rc-slim

# create directories
RUN mkdir -p /data/api

# create the app user
RUN addgroup --system flaskuser && adduser --system --group flaskuser

# create the appropriate directories
ENV HOME=/data/api
ENV APP_HOME=/data/api/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends netcat
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# clean up
RUN apt-get autoremove -y && apt-get clean -y

# Copy project
COPY . $APP_HOME

# Set ownerships
RUN chown -R flaskuser:flaskuser $APP_HOME

# Change user
USER flaskuser
