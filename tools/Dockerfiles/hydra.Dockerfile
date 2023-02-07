FROM python:3.9-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

RUN    apt-get update -y \
    && apt-get install -y git libgpg-error-dev libgcrypt-dev libpcre3-dev libidn11-dev libssh-dev libssl-dev make curl gcc \
    && git clone https://github.com/vanhauser-thc/thc-hydra.git ./src \
    && cd ./src \
    && make clean && ./configure && make && make install \
    && apt-get purge -y make gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf ./src


RUN curl https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/darkweb2017-top10000.txt -o passwords.txt
RUN pip3 install netunicorn-base netunicorn-executor requests aiohttp nest_asyncio

ENTRYPOINT ["python3", "-m", "netunicorn.executor"]
