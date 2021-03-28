
.PHONY: docker web-run

docker: config/Dockerfile-web config/httpd.conf webui/test-db.sqlite3
	docker build --file config/Dockerfile-web  --tag reader-web .

web-run: docker
	docker run -d -p 8000:80 reader-web

test-database: webui/test-db.sqlite3

webui/test-db.sqlite3:
	cd webui && pipenv run yoyo apply -b -d sqlite:///test-db.sqlite3
	sqlite3 webui/test-db.sqlite3 < webui/test/test_data.sql

