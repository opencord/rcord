REGISTRY :=
REPOSITORY :=
TAG := candidate
SHELL := /bin/bash

all: build push

build:
	docker build $(DOCKER_BUILD_ARGS) -t ${REGISTRY}${REPOSITORY}rcord-synchronizer:${TAG} -f Dockerfile.synchronizer .

push:
	docker push ${REGISTRY}${REPOSITORY}rcord-synchronizer:${TAG}

test:
	source ../../xos/venv-xos/bin/activate && pushd xos && nose2 --verbose --coverage-report term && popd || echo "Please install the XOS virtual environment"