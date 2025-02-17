.PHONY: build

PIP = pip
PYTHON = python

build:
	${PYTHON} scripts/multi_build.py

install-editable:
	${PIP} install -e .[dev] --config-settings editable_mode=compat

test:
	ruff check .
	pytest -v