FROM python:3.10
RUN apt-get update && apt-get install netcat -y

COPY proxy /src/proxy

WORKDIR /src/proxy

RUN pip install -r requirements.txt

CMD ["python3", "proxy.py"]