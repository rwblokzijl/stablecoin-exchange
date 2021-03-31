.PHONY: all test run

all: run

clean:
	find . -type d -name  "__pycache__" -exec rm -r {} +

test:
	pipenv run python -m unittest

run:
	cd stablecoin && pipenv run python run_coin.py

coveragea:
	SLOW=1; cd stablecoin && pipenv run coverage run -m pytest --ignore pyipv8 && pipenv run coverage html -i && (brave-browser htmlcov/index.html & disown)

coverage:
	cd stablecoin && pipenv run coverage run -m pytest --ignore pyipv8 && pipenv run coverage html -i && (brave-browser htmlcov/index.html & disown)
