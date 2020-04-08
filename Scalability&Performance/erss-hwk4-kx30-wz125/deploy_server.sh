#!/bin/bash

config_core(){
    core=$(cat /code/configuration.json | grep core | grep -v grep | awk '{print $2}' | awk -F, '{print $1}')
    if [ $core == 1 ];
    then
	task="taskset --cpu-list 0"
    elif [ $core == 2 ];
    then
	task="taskset --cpu-list 0,1"
    elif [ $core == 3 ];
    then
	task="taskset --cpu-list 0,1,2"
    else
	task="taskset --cpu-list 0,1,2,3"
    fi
}

task="taskset --cpu-list 0"
config_core
echo running with $task
$task ./gradlew run-server
