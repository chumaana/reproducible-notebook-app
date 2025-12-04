IMAGE_TAG = r4r/test
CONTAINER_NAME = r4r-test
TARGET_DIR = result

SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c

.PHONY: all build run copy clean-docker clean

all: clean copy

build:
	@echo 'Building docker image $(IMAGE_TAG)'
	@docker build --progress=plain -t $(IMAGE_TAG) . 2>&1 | tee docker-build.log

run: build
	@echo 'Running container $(CONTAINER_NAME)'
	@docker run -t --name $(CONTAINER_NAME) $(IMAGE_TAG) 2>&1 | tee docker-run.log

copy: run
	@echo
	@echo 'Copying files'
	@mkdir -p $(TARGET_DIR)
	@echo -n '  - "/tmp/tmp3zcmrji6/notebook.html"...'
	@docker cp -L $(CONTAINER_NAME):/tmp/tmp3zcmrji6/notebook.html $(TARGET_DIR) 2>/dev/null && echo ' done' || echo ' failed'

clean-docker:
	@echo 'Cleaning previous container (if any)'
	-docker rm $(CONTAINER_NAME)
	@echo 'Cleaning previous image (if any)'
	-docker rmi $(IMAGE_TAG)

clean: clean-docker
	@echo 'Cleaning previous result (if any)'
	rm -rf $(TARGET_DIR)

