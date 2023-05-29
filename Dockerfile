#FROM borda/docker_python-opencv-ffmpeg:cpu-py3.9-cv4.5.1
FROM python:buster
# set the working directory in the container
RUN mkdir /gurmat-bot
RUN mkdir /gurmat-bot/src
WORKDIR /gurmat-bot

# Install python dependencies
COPY requirements.txt /gurmat-bot
RUN pip install -r requirements.txt

COPY .env /gurmat-bot
