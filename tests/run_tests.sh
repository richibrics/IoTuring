#!/bin/bash

# docker run --rm -it -v .:/srv/IoTuring:ro python:3.8.17-slim-bullseye /srv/IoTuring/tests/run_tests.sh

apt update
apt install git -y
git clone /srv/IoTuring
pip install "./IoTuring[test]"
pytest IoTuring