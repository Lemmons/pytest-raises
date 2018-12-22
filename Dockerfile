FROM python:3.6-alpine

RUN apk add --no-cache git
# gcc and musl-dev now required to build pylint's dependencies since
# python:3.6-alpine does not satisfy 'manylinux' distribution.
# See: https://github.com/PyCQA/pylint/issues/2291
RUN apk add gcc musl-dev

# Install dependencies first before copying full tree so docker does not
# re-install everything each time a test file is changed.  If setup.py changes
# dependencies, these must be updated as well!
RUN mkdir -p /src/pytest-raises
RUN python3 -m pip install pytest>=3.2.2
RUN python3 -m pip install pylint
RUN python3 -m pip install pytest-cov

# Changes to source should have docker build cached up to here
WORKDIR /src/pytest-raises
COPY . /src/pytest-raises
RUN python3 -m pip install -e .[develop]
