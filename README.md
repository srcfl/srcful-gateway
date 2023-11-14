# Srcful eGW
Architectural overview of the Sourceful Energy Gateway (eGW) project. Perhaps also add an image here. 
* [Srcful eGW](#srcful-egw)
* [Getting started](#getting-started)
* [Open-Balena](#open-balena)
   * [Services](#services)
      * [server](#server)
      * [bluetooth](#bluetooth)
         * [Windows](#windows)
      * [client](#client)
      * [modbus_slave](#modbus_slave)
   * [Commnads](#commnads)
      * [Monitor](#monitor)
      * [Tunnel](#tunnel)
      * [SSH](#ssh)
      * [Build](#build)
      * [Deploy](#deploy)
      * [Other](#other)
* [Testing](#testing)
* [Design](#design)
* [Other](#other-1)

# Getting started
To get started you need to install `balena-cli` and setup the development environment as described in [this guide](https://open-balena.pages.dev/getting-started/#install-the-balena-cli-on-the-local-machine). This tool is used to deploy the firmware to the open-balena server. Then you need to login to the server to be able to deploy. This is done with the following command:  
```
balena login
```

and select Credentials and use the email and password avaiable in bitwarden. 

# Open-Balena
The gateway is deployed using open-balena. This is a self-hosted version of balena-cloud. The balena-cli is used to deploy the gateway.

## Services 
The gateway is composed of several services that are deployed as docker containers. Only web and bluetooth are deployed to the gateway. The other services are for testing and development.

### server
The crypto stuff is partially mocked and does not require the libs to be installed as this does not seem to work well in a windows based container environment (even though the container itself runs linux...). This should handle iteself gracefully in the code.

Not all functions in the crypto lib have been fixed so pay attention to possible errors you get.

To start a local dev version of the gw you can simply do:  
`docker-compose -f docker-compose-no_crypt.yml up`

or you can run the main module with python directly from the parent directory of `server` (this can be a good idea for debugging).:  
`python -m server`  

We need to run this as a module as there are dependencies between some packages/modules and they need a common root package (server).

### bluetooth
This is the bluethooth service and a test client. The service is simply started with:

`python ble_service.py`

#### Windows
The pysetupdi is needed on windows for the BLE bless library to work. This needs a separate installation:

* crate some nice folder i.e. not in the gatway project folders
```
git clone https://github.com/gwangyi/pysetupdi.git
cd pysetupdi
python setup.py install --user
```
or if using a venv
```
python setup.py install
``` 


### client
This is a simple test client that you can run locally. You would need to start a web-server (e.g. twisted) to service the page and this needs to run on https for things to work (or the ble stuff will not work in a browser on android). A generated certificate is included.

`twistd --nodaemon web --listen "ssl:8000:privateKey=key.pem:certKey=certificate.pem" --path .`

The client is not to be deployed to the gateway and is just a test for now. The real client should be on the `srcful` domain.

### modbus_slave
This is the directory that contains simulation servers of all inverters. This is started with docker-compose-no_crypt or you can start it locally using pythion (this seems painfully slow on windows for some reason). Alternativealy you run the docker container (create it with `docker-compose build` first):

`docker run -p 502:502 sourcefulgateway_inverter`

Don't forget to change the inverter host to `localhost` in `app.py`

## Commnads 
Open-balena has a set of commands that are used to manage the server and all the device

### Monitor
Show logs for a specific device. The device in logs <device> can be a UUID or a device name.

Examples:

	$ balena logs 23c73a1
	$ balena logs 23c73a1 --tail
	
	$ balena logs 192.168.0.31
	$ balena logs 192.168.0.31 --service my-service
	$ balena logs 192.168.0.31 --service my-service-1 --service my-service-2
	
	$ balena logs 23c73a1.local --system
	$ balena logs 23c73a1.local --system --service my-service

### Tunnel
Use this command to open local TCP ports that tunnel to listening sockets in a balenaOS device. This is useful for debugging purposes, or for accessing services running on the device.

Examples:

	# map remote port 22222 to localhost:22222
	$ balena tunnel myFleet -p 22222
	
	# map remote port 22222 to localhost:222
	$ balena tunnel 2ead211 -p 22222:222
	
	# map remote port 22222 to any address on your host machine, port 22222
	$ balena tunnel 1546690 -p 22222:0.0.0.0
	
	# map remote port 22222 to any address on your host machine, port 222
	$ balena tunnel myFleet -p 22222:0.0.0.0:222
	
	# multiple port tunnels can be specified at any one time
	$ balena tunnel myFleet -p 8080:3000 -p 8081:9000

* `deviceOrFleet` - the UUID of the device or the name of the fleet to tunnel to
* `-p`, `--port` - the port mapping to use, in the format: <remotePort>[:[localIP:]localPort]

### SSH

To `SSH` like this, we will need to use `proxytunnel ` on the client.  

Install `proxytunnel` and then create an API key:

```
$ balena api-key generate proxytunnel

Registered api key 'proxytunnel':

sbdfvjvsbvvbliBLJiBlJHBlJHBljhBY

This key will not be shown again, so please save it now.
```

Then configure `SSH` to use proxytunnel to connect to the balena VPN tunnelling service on your openBalena instance:

```
$ nano ~/.ssh/config

Host *.balena
  ProxyCommand proxytunnel -p vpn.balena.srcful.dev:3128 -d %h:22222 -F ~/.ssh/balena-ssh
  ServerAliveInterval 30
```

Create the permission file: 

```
$ nano ~/.ssh/balena-ssh

proxy_user=root
proxy_passwd=sbdfvjvsbvvbliBLJiBlJHBlJHBljhBY
```

Then modify the permissions: 

```
$ chmod 600 ~/.ssh/balena-ssh 
```

Once that is set up, we can SSH into our devices, if our public key is added to the device's `config.json` file. More info [here](https://docs.balena.io/reference/OS/configuration/#sshkeys). Once its added, we can SSH into the device using:

```
balena tunnel <UUID> -p 22222:22222    
```
Followed by:
```
ssh root@localhost -p 22222
```

`balena ssh UUID` is still not supported on open-balena.

### Build 
To build the gateway we use the `balena build` command. This command is used to build a single application or a fleet of devices. The command is used as follows:

```
balena build --fleet myFleet
balena build ./source/ --fleet myorg/myfleet
balena build --deviceType raspberrypi3 --arch armv7hf --emulated
balena build --docker /var/run/docker.sock --fleet myFleet   # Linux, Mac
balena build --docker //./pipe/docker_engine --fleet myFleet # Windows
balena build --dockerHost my.docker.host --dockerPort 2376 --ca ca.pem --key key.pem --cert cert.pem -f myFleet
```


### Deploy
To deploy to the devices we use the `balena deploy` command. This command is used to deploy a single application or a fleet of devices. The command is used as follows:

Examples:
```
balena deploy myFleet
balena deploy myorg/myfleet --build --source myBuildDir/
balena deploy myorg/myfleet --build --source myBuildDir/ --note "this is the note for this release"
balena deploy myorg/myfleet myRepo/myImage
balena deploy myFleet myRepo/myImage --release-tag key1 "" key2 "value2 with spaces"
``` 

The commands above will use the normal `docker-compose.yml`. 


### Other
Other commands can be found at the [balena CLI Documentation](https://github.com/balena-io/balena-cli/blob/master/docs/balena-cli.md) page. 

# Testing
We use the pytest testing framework for automated testing (https://docs.pytest.org/en/7.2.x/getting-started.html#get-started).

Test modules are placed under `/test` and mirror the structure of the main project. Tests are executed by running:  
`pytest`

Integration in VSCode can be achieved by installing *Python Test Explorer for Visual Studio Code* add the following to your `./vscode/launch.json` configuration to enable *debugging* of tests.

```
{
  "name": "Debug test",
  "type": "python",
  "request": "attach",
  "console": "externalTerminal",
  "justMyCode": false,
  "stopOnEntry": true,
  "envFile": "${workspaceFolder}/.env.test",
  "purpose": [
    "debug-test"
  ]
}
```

# Design
The current design is task bases with a priority queue. The idea is that a task is scheduled to happen at a certain time. This allows for fine grained control and adjustment of task times/delays etc. The downside is that tasks cannot be blocking so IO operations typically need threading. Though this is rater easy to do and there are also some helper classes for common tasks that require threading.

On top of the task-engine we can put a state machine so that it becomes easier to know what tasks are high prio in different contexts.

# Other
