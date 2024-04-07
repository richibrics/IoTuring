# Development

## Install

### Editable install

[Pip documentation](https://pip.pypa.io/en/stable/topics/local-project-installs/)

```shell
git clone https://github.com/richibrics/IoTuring
cd IoTuring
pip install -e .
```

Then run it like in the non-editable mode.

Warning: sometimes to run the module in editable mode you need to cd into the upper IoTuring folder.


### Editable install with venv from git

```shell
git clone https://github.com/richibrics/IoTuring
cd IoTuring
mkdir .venv
python -m venv .venv
. ./.venv/bin/activate
pip install --upgrade pip
pip install -e .
IoTuring -c
```

## Versioning

The project uses [calendar versioning](https://calver.org/):

`YYYY.M.n`:

- `YYYY`: Full year: 2022, 2023 ...
- `M`: Month: 1, 2 ... 11, 12
- `n`: Build number in the month: 1, 2 ...

## Tests

### Run tests in docker:

```shell
docker run --rm -it -v .:/srv/IoTuring:ro python:3.8.17-slim-bullseye /srv/IoTuring/tests/run_tests.sh
```

### Run tests in a venv

```shell
pip install -e ".[test]"
python -m pytest
```

## Docker

To build docker image:

```
docker build -t ioturing:latest .
```

## Tips

### InquirerPy

Current InquirerPy release on Pypi doesn't export classes properly, so type checking gives false positives. To fix this, remove the version installed from Pypi, and install it from Github:

```shell
pip uninstall InquirerPy
pip install git+https://github.com/kazhala/InquirerPy
```

### Docstrings

To generate nice docstrings quickly in VSCode, use the [autoDocstring extension](https://github.com/NilsJPWerner/autoDocstring)