dev_build:
	sudo docker-compose build

dev_up:
	sudo -E docker-compose up

dev_down:
	sudo -E docker-compose down

prod_build:
	sudo -E docker-compose -f compose/prod/docker-compose.prod.yml build

prod_up:
	sudo -E docker-compose -f compose/prod/docker-compose.prod.yml up

prod_down:
	sudo -E docker-compose -f compose/prod/docker-compose.prod.yml down

