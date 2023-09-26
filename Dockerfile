FROM python:3.11-slim

WORKDIR /root/IoTuring

COPY . .

RUN pip install --no-cache-dir .

ARG IOTURING_CONFIG_DIR=/config
ENV IOTURING_CONFIG_DIR=${IOTURING_CONFIG_DIR}

VOLUME ${IOTURING_CONFIG_DIR}

CMD ["IoTuring"]