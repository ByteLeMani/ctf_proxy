FROM python:3.10

RUN apt-get update && apt-get install netcat-openbsd

WORKDIR /proxy
COPY proxy/requirements.txt .

RUN pip install -r requirements.txt

COPY proxy .

CMD ["bash", "init.sh"]
