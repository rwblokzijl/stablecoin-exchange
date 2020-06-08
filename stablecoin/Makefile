.PHONY: all test run

all: run

clean:
	find . -type d -name  "__pycache__" -exec rm -r {} +

test:
	pipenv run python -m unittest

run:
	pipenv run python run_coin.py


