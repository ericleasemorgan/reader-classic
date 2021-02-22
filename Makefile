
.PHONY: docker web-run

docker: config/Dockerfile-web config/httpd.conf
	docker build --file config/Dockerfile-web  --tag reader-web .

web-run: docker
	docker run -d -p 8000:80 reader-web
