build: 
	sudo docker build . --file Dockerfile-db --tag postgres:latest
	sudo docker build . --file Dockerfile-app --tag energy:latest
run:
	sudo docker run -d -p 5432:5432 --name postgres postgres:latest && echo "Sleeping for 20 seconds" && sleep 20
	sudo docker run -d --name energy-app energy:latest
cleanup:
	sudo docker rm -f energy-app postgres
	sudo docker image rm postgres:latest
	sudo docker image rm energy:latest
logs:
	sudo docker exec -it energy-app cat /var/log/energy.log
rebuild:
	make cleanup && make build && make run
