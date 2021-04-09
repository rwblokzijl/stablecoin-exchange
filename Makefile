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
	COMPOSE_PROJECT_NAME=eurotoken docker-compose -H ssh://bloodyfool@161.97.114.29 -f docker-compose-deploy.yml up -d --build

deploya: lock
	COMPOSE_PROJECT_NAME=eurotoken docker-compose -H ssh://bloodyfool@161.97.114.29 -f docker-compose-deploy.yml up -d --build app

clear:
	rm backend/eval/keys/* || true

eval1: clear
	# touch backend/eval/keys/1
	docker-compose -f docker-compose-eval.yml up --scale client=1 --build

eval2: clear
	docker-compose -f docker-compose-eval.yml up --scale client=2 --build

eval4: clear
	docker-compose -f docker-compose-eval.yml up --scale client=4 --build

eval8: clear
	docker-compose -f docker-compose-eval.yml up --scale client=8 --build

