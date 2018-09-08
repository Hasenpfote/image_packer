PACKAGE_NAME=image_packer

HAS_PIPENV=$(shell python -c "exec('try:\n    import pipenv\n    print(\'true\')\nexcept ImportError:\n    print(\'false\')')")
ifeq ($(HAS_PIPENV), true)
	PIPENV_RUN=pipenv run
else
	PIPENV_RUN=
endif

VERSION=$(shell $(PIPENV_RUN) python -c "import $(PACKAGE_NAME); print($(PACKAGE_NAME).__version__)")

SPHINX_WORKING_DIR=./sphinx

SPHINX_APIDOC_OUTPUTDIR=$(SPHINX_WORKING_DIR)/source
SPHINX_APIDOC_SOURCEDIR=./$(PACKAGE_NAME)
SPHINX_APIDOC_PATHNAMES=./$(PACKAGE_NAME)/version.py ./test

SPHINX_BUILD_SOURCEDIR=$(SPHINX_WORKING_DIR)/source
SPHINX_BUILD_BUILDDIR=$(SPHINX_WORKING_DIR)/build


.PHONY: default
default:
	@echo $(PACKAGE_NAME) $(VERSION)


.PHONY: test
test: ./test/.noserc
	cd ./test/ && $(PIPENV_RUN) nosetests -c .noserc


.PHONY: tag
tag:
ifeq ("$(shell git rev-parse --abbrev-ref HEAD)", "master")
	git tag v$(VERSION)
	git push origin --tags
else
	@echo Current branch is not master.
	exit 1
endif


.PHONY: clean
clean:
ifeq ($(OS), Windows_NT)
	@if exist "$(PACKAGE_NAME).egg-info" rd /Q /S "$(PACKAGE_NAME).egg-info"
	@if exist "build" rd /Q /S "build"
	@if exist "dist" rd /Q /S "dist"
else
	@rm -rf *.egg-info/ build/ dist/
endif


.PHONY: setup
setup: setup.py
	@make clean
	$(PIPENV_RUN) python setup.py sdist
	$(PIPENV_RUN) python setup.py bdist_wheel


.PHONY: upload_to_testpypi
upload_to_testpypi: setup
	$(PIPENV_RUN) twine upload --repository testpypi dist/*


.PHONY: upload_to_pypi
upload_to_pypi: setup
	$(PIPENV_RUN) twine upload --repository pypi dist/*


.PHONY: sphinx-apidoc
sphinx-apidoc:
ifneq ($(wildcard $(SPHINX_WORKING_DIR)/.),)
	$(PIPENV_RUN) sphinx-apidoc -f -o $(SPHINX_APIDOC_OUTPUTDIR) $(SPHINX_APIDOC_SOURCEDIR) $(SPHINX_APIDOC_PATHNAMES)
else
	@echo "$(SPHINX_WORKING_DIR)" directory not found.
	exit 1
endif


.PHONY: sphinx-build
sphinx-build: $(SPHINX_BUILD_SOURCEDIR)/conf.py
ifneq ($(wildcard $(SPHINX_WORKING_DIR)/.),)
	$(PIPENV_RUN) sphinx-build -b html $(SPHINX_BUILD_SOURCEDIR) $(SPHINX_BUILD_BUILDDIR)
else
	@echo "$(SPHINX_WORKING_DIR)" directory not found.
	exit 1
endif
