FROM python:3.10

COPY proxy /proxy

WORKDIR /proxy

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install netcat-openbsd

CMD ["bash", "init.sh"]
