FROM debian:stable-slim

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
    python3-pip \
    firefox-esr \
    tshark \
    tcpdump \
    xvfb \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install selenium pyvirtualdisplay netunicorn-executor

ARG TARGETARCH
RUN echo "TARGETARCH: $TARGETARCH" && sleep 10
RUN if [ "$TARGETARCH" = "arm64" ]; then carch="-aarch64"; else carch="64"; fi && \
    wget "https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux$carch.tar.gz" -O /tmp/geckodriver$carch.tar.gz && \
    tar -xf /tmp/geckodriver$carch.tar.gz -C /usr/local/bin/
RUN wget https://addons.mozilla.org/firefox/downloads/file/4047353/ublock_origin-1.46.0.xpi -O /tmp/ublock_origin.xpi

ENTRYPOINT ["python3", "-m", "netunicorn.executor"]