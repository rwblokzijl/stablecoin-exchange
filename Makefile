all: build

lock:
	cd backend && pipenv lock --requirements > requirements.txt

build: lock
	docker-compose build

up:
	docker-compose up

upb: lock
	docker-compose up --build

