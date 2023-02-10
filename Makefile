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
APP_VERSION ?= 0.4.4

# docker
APP_DOCKER_REPO := pavics/canarieapi
APP_DOCKER_TAG  := $(APP_DOCKER_REPO):$(APP_VERSION)
APP_LATEST_TAG  := $(APP_DOCKER_REPO):latest
APP_DOCKER_TEST := canarieapi-test

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
clean: clean-build clean-docs clean-pyc clean-test  ## remove all build, test, coverage and Python artifacts

.PHONY: clean-build
clean-build:  ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -type f -name '*.egg-info' -exec rm -fr {} +
	find . -type f -name '*.egg' -exec rm -f {} +

# rm without quotes important below to allow regex
.PHONY: clean-docs
clean-docs:		## remove doc artifacts
	@echo "Cleaning doc artifacts..."
	@-find "$(APP_ROOT)/docs/" -type f -name "$(APP_NAME)*.rst" -delete
	@-rm -f "$(APP_ROOT)/docs/modules.rst"
	@-rm -f "$(APP_ROOT)/docs/api.json"
	@-rm -rf "$(APP_ROOT)/docs/autoapi"
	@-rm -rf "$(APP_ROOT)/docs/_build"

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

## --- Static code check targets ---

REPORTS_DIR ?= $(APP_ROOT)/reports

.PHONY: mkdir-reports
mkdir-reports:
	@mkdir -p "$(REPORTS_DIR)"

# autogen check variants with pre-install of dependencies using the '-only' target references
CHECKS := pep8 lint quotes security security-code security-deps doc8 docf links imports css
CHECKS := $(addprefix check-, $(CHECKS))

$(CHECKS): check-%: install-dev check-%-only

.PHONY: check
check: install-dev $(CHECKS)  ## run code checks (alias to 'check-all' target)

# undocumented to avoid duplicating aliases in help listing
.PHONY: check-only
check-only: check-all-only

.PHONY: check-all-only
check-all-only: $(addsuffix -only, $(CHECKS))  ## run all code checks
	@echo "All checks passed!"

.PHONY: check-pep8-only
check-pep8-only: mkdir-reports		## run PEP8 code style checks
	@echo "Running PEP8 code style checks..."
	@-rm -fr "$(REPORTS_DIR)/check-pep8.txt"
	@bash -c '$(CONDA_CMD) \
		flake8 --config="$(APP_ROOT)/setup.cfg" --output-file="$(REPORTS_DIR)/check-pep8.txt" --tee'

.PHONY: check-lint-only
check-lint-only: mkdir-reports		## run linting code style checks
	@echo "Running linting code style checks..."
	@-rm -fr "$(REPORTS_DIR)/check-lint.txt"
	@bash -c '$(CONDA_CMD) \
		pylint \
			--rcfile="$(APP_ROOT)/.pylintrc" \
			--reports y \
			"$(APP_ROOT)/$(APP_NAME)" "$(APP_ROOT)/docs" "$(APP_ROOT)/tests" \
		1> >(tee "$(REPORTS_DIR)/check-lint.txt")'

.PHONY: check-quotes-only
check-quotes-only: mkdir-reports	## run quotes style checks
	@echo "Running quotes style checks..."
	@-rm -fr "$(REPORTS_DIR)/check-quotes.txt"
	@bash -c '$(CONDA_CMD) \
		unify \
			--check-only \
			--recursive \
			--quote \" \
			"$(APP_ROOT)/$(APP_NAME)" "$(APP_ROOT)/docs" "$(APP_ROOT)/tests" \
		1> >(tee "$(REPORTS_DIR)/check-quotes.txt")'

.PHONY: check-security-only
check-security-only: check-security-code-only check-security-deps-only  ## run security checks

# ignored codes:
#	42194: https://github.com/kvesteri/sqlalchemy-utils/issues/166  # not fixed since 2015
.PHONY: check-security-deps-only
check-security-deps-only: mkdir-reports  ## run security checks on package dependencies
	@echo "Running security checks of dependencies..."
	@-rm -fr "$(REPORTS_DIR)/check-security-deps.txt"
	@bash -c '$(CONDA_CMD) \
		safety check \
			-r "$(APP_ROOT)/requirements.txt" \
			-r "$(APP_ROOT)/requirements-dev.txt" \
			-r "$(APP_ROOT)/requirements-doc.txt" \
			-r "$(APP_ROOT)/requirements-sys.txt" \
			-i 42194 \
		1> >(tee "$(REPORTS_DIR)/check-security-deps.txt")'

.PHONY: check-security-code-only
check-security-code-only: mkdir-reports  ## run security checks on source code
	@echo "Running security code checks..."
	@-rm -fr "$(REPORTS_DIR)/check-security-code.txt"
	@bash -c '$(CONDA_CMD) \
		bandit -v --ini "$(APP_ROOT)/setup.cfg" -r \
		1> >(tee "$(REPORTS_DIR)/check-security-code.txt")'

.PHONY: check-docs-only
check-docs-only: check-doc8-only check-docf-only	## run every code documentation checks

.PHONY: check-doc8-only
check-doc8-only: mkdir-reports		## run PEP8 documentation style checks
	@echo "Running PEP8 doc style checks..."
	@-rm -fr "$(REPORTS_DIR)/check-doc8.txt"
	@bash -c '$(CONDA_CMD) \
		doc8 --config "$(APP_ROOT)/setup.cfg" "$(APP_ROOT)/docs" \
		1> >(tee "$(REPORTS_DIR)/check-doc8.txt")'

# FIXME: move parameters to setup.cfg when implemented (https://github.com/myint/docformatter/issues/10)
# NOTE: docformatter only reports files with errors on stderr, redirect trace stderr & stdout to file with tee
# NOTE:
#	Don't employ '--wrap-descriptions 120' since they *enforce* that length and rearranges format if any word can fit
#	within remaining space, which often cause big diffs of ugly formatting for no important reason. Instead only check
#	general formatting operations, and let other linter capture docstrings going over 120 (what we really care about).
.PHONY: check-docf-only
check-docf-only: mkdir-reports	## run PEP8 code documentation format checks
	@echo "Checking PEP8 doc formatting problems..."
	@-rm -fr "$(REPORTS_DIR)/check-docf.txt"
	@bash -c '$(CONDA_CMD) \
		docformatter \
			--pre-summary-newline \
			--wrap-descriptions 0 \
			--wrap-summaries 120 \
			--make-summary-multi-line \
			--check \
			--recursive \
			"$(APP_ROOT)" \
		1>&2 2> >(tee "$(REPORTS_DIR)/check-docf.txt")'

.PHONY: check-links-only
check-links-only: mkdir-reports		## run check of external links in documentation for integrity
	@echo "Running link checks on docs..."
	@bash -c '$(CONDA_CMD) $(MAKE) -C "$(APP_ROOT)/docs" linkcheck'

.PHONY: check-imports-only
check-imports-only: mkdir-reports	## run imports code checks
	@echo "Running import checks..."
	@-rm -fr "$(REPORTS_DIR)/check-imports.txt"
	@bash -c '$(CONDA_CMD) \
	 	isort --check-only --diff $(APP_ROOT) \
		1> >(tee "$(REPORTS_DIR)/check-imports.txt")'

.PHONY: check-css-only
check-css-only: mkdir-reports install-npm
	@echo "Running CSS style checks..."
	@npx stylelint \
		--config "$(APP_ROOT)/.stylelintrc.json" \
		--output-file "$(REPORTS_DIR)/fixed-css.txt" \
		"$(APP_ROOT)/**/*.css"

# autogen fix variants with pre-install of dependencies using the '-only' target references
FIXES := imports lint quotes docf css
FIXES := $(addprefix fix-, $(FIXES))

$(FIXES): fix-%: install-dev fix-%-only

.PHONY: fix
fix: fix-all    ## run all fixes (alias for 'fix-all' target)

# undocumented to avoid duplicating aliases in help listing
.PHONY: fix-only
fix-only: $(addsuffix -only, $(FIXES))

.PHONY: fix-all-only
fix-all-only: fix-only  ## fix all code check problems automatically
	@echo "All fixes applied!"

.PHONY: fix-imports-only
fix-imports-only: 	## fix import code checks corrections automatically
	@echo "Fixing flagged import checks..."
	@-rm -fr "$(REPORTS_DIR)/fixed-imports.txt"
	@bash -c '$(CONDA_CMD) \
		isort $(APP_ROOT) \
		1> >(tee "$(REPORTS_DIR)/fixed-imports.txt")'

.PHONY: fix-lint-only
fix-lint-only: mkdir-reports	## fix some PEP8 code style problems automatically
	@echo "Fixing PEP8 code style problems..."
	@-rm -fr "$(REPORTS_DIR)/fixed-lint.txt"
	@bash -c '$(CONDA_CMD) \
		autopep8 -v -j 0 -i -r $(APP_ROOT) \
		1> >(tee "$(REPORTS_DIR)/fixed-lint.txt")'

.PHONY: fix-quotes-only
fix-quotes-only: mkdir-reports	## fix quotes style problems automatically
	@echo "Fixing quotes style problems..."
	@-rm -fr "$(REPORTS_DIR)/fixed-quotes.txt"
	@bash -c '$(CONDA_CMD) \
		unify \
			--in-place \
			--recursive \
			--quote \" \
			"$(APP_ROOT)/$(APP_NAME)" "$(APP_ROOT)/docs" "$(APP_ROOT)/tests" \
		1> >(tee "$(REPORTS_DIR)/fixed-quotes.txt")'

# FIXME: move parameters to setup.cfg when implemented (https://github.com/myint/docformatter/issues/10)
.PHONY: fix-docf-only
fix-docf-only: mkdir-reports	## fix some PEP8 code documentation style problems automatically
	@echo "Fixing PEP8 code documentation problems..."
	@-rm -fr "$(REPORTS_DIR)/fixed-docf.txt"
	@bash -c '$(CONDA_CMD) \
		docformatter \
			--pre-summary-newline \
			--wrap-descriptions 0 \
			--wrap-summaries 120 \
			--make-summary-multi-line \
			--in-place \
			--recursive \
			$(APP_ROOT) \
		1> >(tee "$(REPORTS_DIR)/fixed-docf.txt")'

.PHONY: fix-css-only
fix-css-only: mkdir-reports install-npm		## fix CSS styles problems automatically
	@echo "Fixing CSS style problems..."
	@npx stylelint \
		--fix \
		--config "$(APP_ROOT)/.stylelintrc.json" \
		--output-file "$(REPORTS_DIR)/fixed-css.txt" \
		"$(APP_ROOT)/**/*.css"


## --- Testing targets --- ##

.PHONY: test-only
test-only:  ## run tests without dependencies pre-installation
	python setup.py test

.PHONY: test
test: install-req install-dev test-only  ## run tests quickly with the default Python

.PHONY: test-all
test-all: install-req install-dev  ## run tests on every Python version with tox
	tox

.PHONY: test-docker
test-docker: docker-test  ## run test with docker (alias for 'docker-test' target) - WARNING: build image if missing

# for consistency only with other test
test-docker-only: test-docker ## run test with docker (alias for 'docker-test' target) - WARNING: build image if missing

.PHONY: coverage-only
coverage-only:  ## check code coverage without dependencies pre-installation
	coverage run --source "$(APP_NAME)" setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

.PHONY: coverage
coverage: install-req install-dev coverage-only  ## check code coverage quickly with the default Python

## --- Documentation targets --- ##

DOC_LOCATION := $(APP_ROOT)/docs/_build/html/index.html
$(DOC_LOCATION):
	@echo "Building docs..."
	@bash -c '$(CONDA_CMD) \
		sphinx-apidoc -o "$(APP_ROOT)/docs/" "$(APP_ROOT)/$(APP_NAME)"; \
		"$(MAKE)" -C "$(APP_ROOT)/docs" html;'
	@-echo "Documentation available: file://$(DOC_LOCATION)"

.PHONY: _force_docs
_force_docs:
	@-rm -f "$(DOC_LOCATION)"

.PHONY: docs-only
docs-only: _force_docs $(DOC_LOCATION) 	## generate documentation without requirements installation or cleanup

# NOTE: we need almost all base dependencies because magpie package needs to be parsed to generate OpenAPI
.PHONY: docs
docs: install-docs install clean-docs docs-only	## generate Sphinx HTML documentation, including API docs

.PHONY: docs-show
docs-show: $(DOC_LOCATION)	## display HTML webpage of generated documentation (build docs if missing)
	@-test -f "$(DOC_LOCATION)" || $(MAKE) -C "$(APP_ROOT)" docs
	$(BROWSER) "$(DOC_LOCATION)"

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

.PHONY: install-docs
install-docs:  ## install package requirements for documentation generation
	pip install -r "$(APP_ROOT)/requirements-doc.txt"

# install locally to ensure they can be found by config extending them
.PHONY: install-npm
install-npm:    		## install npm package manager if it cannot be found
	@[ -f "$(shell which npm)" ] || ( \
		echo "Binary package manager npm not found. Attempting to install it."; \
		apt-get install npm \
	)
	@[ `npm ls -only dev -depth 0 2>/dev/null | grep -V "UNMET" | grep stylelint-config-standard | wc -l` = 1 ] || ( \
		echo "Install required libraries for style checks." && \
		npm install stylelint@13.13.1 stylelint-config-standard@22.0.0 --save-dev \
	)

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
	-docker rmi "$(docker images -f "reference=$(APP_DOCKER_REPO)" -q)"

.PHONY: docker-stop
docker-stop:
	@echo "Stopping test docker container: $(APP_DOCKER_TEST)"
	-docker container stop "$(APP_DOCKER_TEST)" 2>/dev/null || true
	-docker rm $(APP_DOCKER_TEST) 2>/dev/null || true

.PHONY: docker-test
docker-test: docker-build docker-stop docker-clean
	@echo "Smoke test of docker image: $(DOCKER_TAG)"
	docker run --pull never --name "$(APP_DOCKER_TEST)" -p 2000:2000 -d "$(APP_DOCKER_TAG)"
	@sleep 2
	@echo "Testing docker image..."
	(curl http://localhost:2000 | grep "Canarie API" && \
	  $(MAKE) docker-stop --no-print-directory || \
	 ($(MAKE) docker-stop --no-print-directory && \
	  echo "Failed to obtain expected response from CanarieAPI docker"; exit 1 ))
