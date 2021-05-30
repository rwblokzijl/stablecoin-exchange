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
	COMPOSE_PROJECT_NAME=eurotoken docker-compose -H ssh://bloodyfool@161.97.114.29 -f docker-compose-deploy.yml up

runb:
	COMPOSE_PROJECT_NAME=eurotoken docker-compose -H ssh://bloodyfool@161.97.114.29 -f docker-compose-deploy.yml up --build

start:
	COMPOSE_PROJECT_NAME=eurotoken docker-compose -H ssh://bloodyfool@161.97.114.29 -f docker-compose-deploy.yml up -d

stop:
	COMPOSE_PROJECT_NAME=eurotoken docker-compose -H ssh://bloodyfool@161.97.114.29 -f docker-compose-deploy.yml stop

restart:
	COMPOSE_PROJECT_NAME=eurotoken docker-compose -H ssh://bloodyfool@161.97.114.29 -f docker-compose-deploy.yml restart

deploy: lock
	cd frontend && npm run build
	COMPOSE_PROJECT_NAME=eurotoken docker-compose -H ssh://bloodyfool@161.97.114.29 -f docker-compose-deploy.yml up -d --build

deploya: lock
	COMPOSE_PROJECT_NAME=eurotoken docker-compose -H ssh://bloodyfool@161.97.114.29 -f docker-compose-deploy.yml up -d --build app

clear:
	@(rm backend/eval/keys/*          || true) > /dev/null 2>&1
	@(rm backend/eval/keys/sync/*     || true) > /dev/null 2>&1
	@(rm backend/eval/keys/database/* || true) > /dev/null 2>&1

eval: clear
	bash ./run_eval.sh

