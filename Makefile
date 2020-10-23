reset-cluster:
	docker-compose -f test/docker-compose.yml rm -f

boot-cluster: reset-cluster
	docker-compose -f test/docker-compose.yml up --force-recreate -d --remove-orphans

shutdown-cluster:
	docker-compose -f test/docker-compose.yml down

run-full-tests: boot-cluster
	poetry run pytest --integration --doctest-modules

run-tests:
	poetry run pytest --doctest-modules
