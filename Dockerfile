FROM python:3.10

COPY proxy /proxy

WORKDIR /proxy

RUN pip install -r requirements.txt

CMD ["bash", "init.sh"]
