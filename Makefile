all: build

lock:
	cd backend && pipenv lock --requirements > requirements.txt

build: lock
	docker-compose build


