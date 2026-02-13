.PHONY: setup test run push-branch

setup:
	python3 scripts/setup.py

test:
	python3 scripts/dev_check.py

run:
	python3 -m app.mediamanager.main

push-branch:
	bash scripts/push_subtree_branch.sh
