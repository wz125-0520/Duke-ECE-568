#!/bin/bash

# this represent how long will each server run
time=300

# $1 --- thread strategy
# $2 --- bucket size
config_server(){
    cat > configuration.json <<EOF
{
  "server": {
    "preCreateThread": $1,
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

run_server(){
    cpu=0
    if [ $1 == "1" ]
    then
	cpu=0
    elif [ $1 == "2" ]
    then
	cpu=0,1
    elif [ $1 == "3" ]
    then
	cpu=0,1,2
    else
	cpu=0,1,2,3
    fi
    echo taskset --cpu-list $cpu ./gradlew run-s
    {
	# run with specific core
	taskset --cpu-list $cpu ./gradlew run-server
    } &
}

save_log(){
    cp ./scalableServer/data.log ./logs/data_$1_$2_$3_$4.log
}

# $1 --- round number
# $2 --- true for "pre create thread"; false for "thread per request"
# $3 --- bucketSize
# $4 --- core number
round(){
    echo -e " ====== \033[31m round $1 \033[0m ====== "

    if [ $2 == true ]
    then
	th="pre create thread"
    else
	th="thread per request"
    fi
    echo "thread strategy: $th"
    echo "bucket size: $3"
    echo "core number: $4"

    config_server $2 $3
    run_server $4
    sleep $time
    kill_server
    save_log $1 $th $3 $4
}

roundNum=1
# pre create thread + 128 bucket size + 1-4 cores
for i in {1..4};
do
    round $roundNum true 128 $i
    let "roundNum++"
done

# thread per request + 128 bucket size + 1-4 cores
for i in {1..4};
do
    round $roundNum false 128 $i
    let "roundNum++"
done

# pre thread + different bucket size + 4 cores
for i in 32 128 512 2048;
do
    round $roundNum true $i 4
    let "roundNum++"
done

# thread per request + different bucket size + 4 cores
for i in 32 128 512 2048;
do
    round $roundNum false $i 4
    let "roundNum++"
done
wait
