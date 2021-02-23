all: build

lock:
	cd backend && pipenv lock --requirements > requirements.txt

build: lock
	COMPOSE_PROJECT_NAME=eurotoken docker-compose build

up:
	COMPOSE_PROJECT_NAME=eurotoken docker-compose up

upb: lock
	COMPOSE_PROJECT_NAME=eurotoken docker-compose up --build

run:
	COMPOSE_PROJECT_NAME=eurotoken docker-compose -H ssh://bloodyfool@161.97.114.29 -f docker-compose-deploy.yml up -d

stop:
	COMPOSE_PROJECT_NAME=eurotoken docker-compose -H ssh://bloodyfool@161.97.114.29 -f docker-compose-deploy.yml stop

restart:
	COMPOSE_PROJECT_NAME=eurotoken docker-compose -H ssh://bloodyfool@161.97.114.29 -f docker-compose-deploy.yml restart

deploy: lock
	COMPOSE_PROJECT_NAME=eurotoken docker-compose -H ssh://bloodyfool@161.97.114.29 -f docker-compose-deploy.yml up -d --build


