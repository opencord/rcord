REGISTRY          ?=
REPOSITORY        ?=
DOCKER_BUILD_ARGS ?=
SERVICE           ?= rcord
MAKEFILE_DIR      := $(dir $(realpath $(firstword $(MAKEFILE_LIST))))
TAG               ?= $(shell cat ${MAKEFILE_DIR}/VERSION)
IMAGENAME         := ${REGISTRY}${REPOSITORY}${SERVICE}-synchronizer:${TAG}
SHELL             := /bin/bash

all: build push

build:
	docker build $(DOCKER_BUILD_ARGS) -t ${IMAGENAME} -f Dockerfile.synchronizer .

push:
	docker push ${IMAGENAME}

test:
	source ../../xos/venv-xos/bin/activate && cd xos && nose2 --verbose --coverage-report term || echo "Please install the XOS virtual environment"

migrate:
	source ../../xos/venv-xos/bin/activate && cd xos && xos-migrate -s $(SERVICE)