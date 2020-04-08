#!/bin/bash
# first terminate any old ones
docker kill testing-568
docker rm testing-568
# build a new container
sudo docker build --build-arg LOCAL_USER_ID=`id -u`  --tag testing-568 .
# now run the new one
sudo docker run --name testing-568 -t testing-568 ./gradlew run-testing
