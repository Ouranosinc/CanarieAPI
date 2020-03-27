define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

# Included custom configs change the value of MAKEFILE_LIST
# Extract the required reference beforehand so we can use it for help target
MAKEFILE_NAME := $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))
# Include custom config if it is available
-include Makefile.config

# Application
APP_ROOT := $(abspath $(lastword $(MAKEFILE_NAME))/..)
APP_NAME := canarieapi
# NOTE: don't change this manually, use the make bump command to update everywhere
APP_VERSION ?= 0.4.2

# docker
APP_DOCKER_REPO := pavics/canarieapi
APP_DOCKER_TAG  := $(APP_DOCKER_REPO):$(APP_VERSION)
APP_LATEST_TAG  := $(APP_DOCKER_REPO):latest


# Auto documented help targets & sections from comments
#	- detects lines marked by double octothorpe (#), then applies the corresponding target/section markup
#   - target comments must be defined after their dependencies (if any)
#	- section comments must have at least a double dash (-)
#
# 	Original Reference:
#		https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
# 	Formats:
#		https://misc.flogisoft.com/bash/tip_colors_and_formatting
_SECTION := \033[34m
_TARGET  := \033[36m
_NORMAL  := \033[0m
.PHONY: help
# note: use "\#\#" to escape results that would self-match in this target's search definition
help:	## print this help message (default)
	@echo "$(_SECTION)=== $(APP_NAME) help ===$(_NORMAL)"
	@echo "Please use 'make <target>' where <target> is one of:"
#	@grep -E '^[a-zA-Z_-]+:.*?\#\# .*$$' $(MAKEFILE_LIST) \
#		| awk 'BEGIN {FS = ":.*?\#\# "}; {printf "    $(_TARGET)%-24s$(_NORMAL) %s\n", $$1, $$2}'
	@grep -E '\#\#.*$$' "$(APP_ROOT)/$(MAKEFILE_NAME)" \
		| awk ' BEGIN {FS = "(:|\-\-\-)+.*?\#\# "}; \
			/\--/ {printf "$(_SECTION)%s$(_NORMAL)\n", $$1;} \
			/:/   {printf "    $(_TARGET)%-24s$(_NORMAL) %s\n", $$1, $$2} \
		'

## --- Versionning targets --- ##

# Bumpversion 'dry' config
# if 'dry' is specified as target, any bumpversion call using 'BUMP_XARGS' will not apply changes
BUMP_XARGS ?= --verbose --allow-dirty
ifeq ($(filter dry, $(MAKECMDGOALS)), dry)
	BUMP_XARGS := $(BUMP_XARGS) --dry-run
endif

.PHONY: dry
dry: setup.cfg	## run 'bump' target without applying changes (dry-run)
ifeq ($(findstring bump, $(MAKECMDGOALS)),)
	$(error Target 'dry' must be combined with a 'bump' target)
endif

.PHONY: bump
bump:	## bump version using VERSION specified as user input
	@-echo "Updating package version ..."
	@[ "${VERSION}" ] || ( echo ">> 'VERSION' is not set"; exit 1 )
	@-bash -c '$(CONDA_CMD) test -f "$(CONDA_ENV_PATH)/bin/bump2version || pip install bump2version'
	@-bash -c '$(CONDA_CMD) bump2version $(BUMP_XARGS) --new-version "${VERSION}" patch;'

.PHONY: version
version:	## display current version
	@-echo "$(APP_NAME) version: $(APP_VERSION)"


## --- Cleanup targets --- ##

.PHONY: clean
clean: clean-build clean-pyc clean-test  ## remove all build, test, coverage and Python artifacts

.PHONY: clean-build
clean-build:  ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -type f -name '*.egg-info' -exec rm -fr {} +
	find . -type f -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc:  ## remove Python file artifacts
	find . -type f -name '*.pyc' -exec rm -f {} +
	find . -type f -name '*.pyo' -exec rm -f {} +
	find . -type f -name '*~' -exec rm -f {} +
	find . -type f -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-tests
clean-test:  ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

## --- Testing targets --- ##

.PHONY: lint
lint: install-req install-dev  ## check code style
	flake8 "$(APP_NAME)" tests

.PHONY: test
test: install-req install-dev  ## run tests quickly with the default Python
	python setup.py test

.PHONY: test-all
test-all: install-req install-dev  ## run tests on every Python version with tox
	tox

.PHONY: coverage
coverage: install-req install-dev  ## check code coverage quickly with the default Python
	coverage run --source "$(APP_NAME)" setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

## --- Documentation targets --- ##

.PHONY: docs
docs:  ## generate Sphinx HTML documentation, including API docs
	rm -f "docs/$(APP_NAME).rst"
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ "$(APP_NAME)"
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

.PHONY: servedocs
servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

## --- Packaging targets --- ##

.PHONY: release
release: clean  ## package and upload a release
	python setup.py sdist upload
	python setup.py bdist_wheel upload

.PHONY: dist
dist: clean  ## package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

## --- Installation targets --- ##

.PHONY: install-req
install-req:  ## install package requirements allowing to run the code
	pip install -r requirements.txt

.PHONY: install-dev
install-dev:  ## install package requirements allowing to run tests
	pip install -r requirements-dev.txt

.PHONY: install
install: clean install-req  ## install the package to the active Python's site-packages
	python setup.py install

## --- Docker targets --- ##

.PHONY: docker-info
docker-info:  ## tag version of docker image for build/push
	@echo "$(APP_NAME) image will be built, tagged and pushed as:"
	@echo "$(APP_DOCKER_TAG)"

.PHONY: docker-build
docker-build:  ## build the docker image
	docker build "$(APP_ROOT)" -t "$(APP_LATEST_TAG)"
	docker tag "$(APP_LATEST_TAG)" "$(APP_DOCKER_TAG)"

.PHONY: docker-push
docker-push: docker-build  ## push the built docker image
	docker push "$(APP_DOCKER_TAG)"

.PHONY: docker-clean
docker-clean: 	## remove any leftover images from docker target operations
	docker rmi $(docker images -f "reference=$(APP_DOCKER_REPO)" -q)
