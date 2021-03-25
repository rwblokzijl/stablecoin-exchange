.PHONY: all test run

all: run

clean:
	find . -type d -name  "__pycache__" -exec rm -r {} +

test:
	pipenv run python -m unittest

run:
	pipenv run python run_coin.py

coveragea:
	SLOW=1; cd stablecoin && pipenv run coverage run -m pytest --ignore pyipv8 && pipenv run coverage html -i && brave-browser htmlcov/index.html

coverage:
	cd stablecoin && pipenv run coverage run -m pytest --ignore pyipv8 && pipenv run coverage html -i && brave-browser htmlcov/index.html
