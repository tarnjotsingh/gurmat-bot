FROM borda/docker_python-opencv-ffmpeg:cpu-py3.9-cv4.5.1

# set the working directory in the container
RUN mkdir /gurmat-bot
RUN mkdir /gurmat-bot/src
WORKDIR /gurmat-bot

# copy the dependencies file to the working directory
COPY requirements.txt /gurmat-bot
COPY .env /gurmat-bot

# install dependencies
RUN pip install -r requirements.txt
