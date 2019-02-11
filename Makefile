build:
	docker-compose up --build -d

clean:
	docker-compose down
	docker system prune -fa

deploy:
	docker-machine create --driver digitalocean --digitalocean-access-token $DO_TOKEN --digitalocean-region=ams2 42rides