FROM python:3.8.10

MAINTAINER Lauri Elias <laurileet@gmail.com>

RUN apt-get update && apt-get install -y cmake build-essential gfortran git wget curl graphicsmagick \
    libgraphicsmagick1-dev libatlas-base-dev libavcodec-dev libavformat-dev libgtk2.0-dev libjpeg-dev liblapack-dev \
    libswscale-dev pkg-config python3-dev python3-numpy software-properties-common zip

RUN pip3 install dlib
