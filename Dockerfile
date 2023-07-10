FROM python:3.10-bullseye

# RUN mkdir -p /PingBot

USER root

RUN git clone https://github.com/BadCat83/PingBot.git

WORKDIR /PingBot

# COPY . .

RUN pip install -r /PingBot/requirements.txt

#CMD ["python", "/PingBot/main.py"]
