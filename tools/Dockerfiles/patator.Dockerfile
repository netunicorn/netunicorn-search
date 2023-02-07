FROM python:3.9-slim

ENV DEBIAN_FRONTEND=noninteractive 

RUN printf "paramiko\npycurl\najpy\nimpacket\npyopenssl\npycryptodomex\ndnspython\nIPy\npysnmp\npyasn1\npysqlcipher3\naiohttp\nnest_asyncio" > requirements.txt

RUN apt-get update \
  && apt-get install -y \
    libssl-dev \
    curl \
    build-essential git \
    libcurl4-openssl-dev \
  && python3 -m pip install --upgrade pip \
  && python3 -m pip install -r requirements.txt \
  && apt-get purge -y build-essential \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/lanjelot/patator.git /opt/patator
WORKDIR /opt/patator

# password list
RUN curl https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/darkweb2017-top10000.txt -o passwords.txt

# install netunicorn executor
RUN pip install netunicorn-base
RUN pip install netunicorn-executor

# set netunicorn executor as entrypoint
ENTRYPOINT ["python3", "-m", "netunicorn.executor"]

