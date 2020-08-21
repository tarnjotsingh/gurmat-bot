FROM python:3.8

# set the working directory in the container
RUN mkdir /gurmat-bot
WORKDIR /gurmat-bot

# copy the dependencies file to the working directory
COPY requirements.txt /gurmat-bot

# install dependencies
RUN pip install -r requirements.txt

# Copy environment file and source files into the workdir
COPY src/ /gurmat-bot/src
COPY .env /gurmat-bot
