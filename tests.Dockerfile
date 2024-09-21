FROM python:3.8.17-slim-bullseye

WORKDIR /root/IoTuring

COPY . .

RUN pip install --no-cache-dir .[test]

CMD python -m pytest

# docker run --rm -it $(docker build -q -f tests.Dockerfile .)