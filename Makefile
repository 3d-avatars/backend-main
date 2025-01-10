ifeq ($(shell test -e '.env' && echo -n yes),yes)
	include .env
endif


ifndef APP_PORT
override APP_PORT = 8080
endif

ifndef APP_HOST
override APP_HOST = 127.0.0.1
endif


env: ##@ Copy env from example files
	cp .env.example .env
	cp log_conf_example.yaml log_conf.yaml

deploy: ##@ Set up docker environment
	docker-compose -f ./deployment/docker-compose.yml up --build --remove-orphans

revision:  ##@Database Create new revision file automatically with prefix (ex. 2022_01_01_14cs34f_message.py)
	alembic revision --autogenerate

migrate:  ##@Database Do all migrations in database
	alembic upgrade head
