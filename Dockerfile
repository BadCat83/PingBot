FROM python:3.10-bullseye

RUN mkdir -p /PingBot

USER root

WORKDIR /PingBot

RUN git clone https://github.com/BadCat83/PingBot.git

# COPY . .

RUN pip install -r requirements.txt

#CMD ["python", "/PingBot/main.py"]
