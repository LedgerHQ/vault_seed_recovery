FROM python:3.10-slim

COPY . /app
WORKDIR /app
RUN apt update && apt upgrade && apt install -y \
    build-essential
RUN pip install -r requirements.txt
CMD python ./recoverMasterSeed.py
