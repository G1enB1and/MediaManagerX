.PHONY: setup test run

setup:
	python3 scripts/setup.py

test:
	python3 scripts/dev_check.py

run:
	python3 -m app.mediamanager.main
