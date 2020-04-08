#!/bin/bash

# $1 --- thread strategy
# $2 --- bucket size
# $3 --- core size
config(){
    cat > configuration.json <<EOF
{
  "server": {
    "preCreateThread": $1,
    "core": $3,
    "comment": "preCreateThread vs. thread per request"
  },

  "client": {
    "port": 12345,
    "host": "localhost",
    "maxDelay": 3,
    "comment": "1. replace the host with your VM(e.g. vcm-xxxx.vm.duke.edu); 2. delayBound, the maximum delay time"
  },

  "bucketSize": $2,
  "threadCnt": 100,
  "comment": "both server and client need to know bucketSize(bucket size on server) & threadCnt(client will open how many threads to send request), which can bring us some convenient to automatically testing"
}
EOF
}

kill_server(){
    ps -ef | grep run-server | grep -v grep | awk '{print $2}' | xargs kill
}

echo "Configuring server"

echo "Which strategy do you want to use?"
echo "1. pre-create thread"
echo "2. thread per request"
read th

threadChoice=true
if [ $th == "1" ]
then
    threadChoice=true
else
    threadChoice=false
fi

echo "Please specify the bucket size."
echo "1. 32"
echo "2. 128"
echo "3. 512"
echo "4. 2048"
read bu

bucketSize=32
if [ $bu == "1" ]
then
    bucketSize=32
elif [ $bu == "2" ]
then
    bucketSize=128
elif [ $bu == "3" ]
then
    bucketSize=512
else
    bucketSize=2048
fi

echo "Please specify the core number(1-4)."
read core

config $threadChoice $bucketSize $core

echo "Successfully config the server."
echo "Now please use \"sudo docker-compose up\" to run the server"
