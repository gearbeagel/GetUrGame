runserver:
	poetry run python backend/manage.py runserver

app:
	poetry run python backend/manage.py startapp $(name)

migrate:
	poetry run python backend/manage.py migrate

makemigrations:
	poetry run python backend/manage.py makemigrations

install-pre-commit:
	poetry run pre-commit uninstall
	poetry run pre-commit install

lint:
	poetry run pre-commit run --all-files
