# erss-hwk4-kx30-wz125
We use Java for both "scalable server" and "testing infrastructure", so to be convenient, we build a root project(that's why you can see some `.gradle` file in root directory) which contains two sub-projects(server & testing).

## Scripts Introduction
Since there are several scripts in our project, we want to briefly introduce them.
* `auto_testing.sh` --- this is used to run the server multiple times with different arguments combination
    * this is mainly used by ourselves for testing, so to make it simple(and fast), it doesn't use docker and need java environment 
* `deploy_server.sh` --- this is used to deploy the scalable server (used in `docker-compose`)
* `deploy_testing.sh` --- this is used to deploy the testing infrastructure (in case you don't have java environment, this use docker instead)
* `config.sh` --- this is used to config the server (e.g. bucket size, thread strategy)

**(1) How to run scalable server?**

**1.1 config the server**

To config the server, we strongly recommend you use the script we wrote (you can modify the `configuration.json`directly  if you want). Run `config.sh`

**1.2 run the server**

```shell
sudo docker-compose up
```

or without docker

```shell
./gradlew run-server
```

**(2) How to run testing infrastructure?**

You need to go to the `configuration.json` file, and specify the host of your server(default is `localhost`). Then run

```shell
./deploy_testing
```

NOTE: don't run this command with sudo!!!

or without docker

```shell
./gradlew run-testing
```

**(3) How to get some experiment result quickly?**

To facilitate the testing process(for us), we write a simple script to automate it in some extents. Run

```shell
./auto_testing
```
NOTE: this script will run & rerun the server multiple times with different combination of arguments, in case you don't want to run each time too long, you can modify the first line of this script to control how long will server will run each time.

You can open another terminal, config and run the client (just let it keep running), it will send data to server constantly(re-try if there is an exception), but if you let the client run too long the performance of client will degrade.

After finish all rounds, you should see a directory name `logs`, and contains all the log file we have generated during this experiment.

**(4) How to get the result image?**

We write a simple python script which can parse the data log generates by server and visualize it.

To run this you need to have python3 install on your domputer(not VM, VM doesn't have GUI)

* go to analysis directory --- `cd analysis`
* install a virtual environment --- `python3 -m venv venv`
* activate the virtual environment --- `source venv/bin/activate`
* install all libraries --- `pip3 install -r requirements`
* run the program and specify the log file --- `python main.py <data1.log> <data2.log>`