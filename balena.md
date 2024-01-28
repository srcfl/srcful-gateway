# Open-Balena
The gateway is deployed using open-balena. This is a self-hosted version of balena-cloud. The balena-cli is used to deploy the gateway. Open-balena has a set of commands that are used to manage the server and all the device

* [Monitor](#monitor)
* [Tunnel](#tunnel)
* [SSH](#ssh)
* [SSH into a docker container](#ssh-into-a-docker-container)
* [Build](#build)
* [Deploy](#deploy)
* [Other](#other)

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

First you need the private key. This is available in bitwarden. Create a new file, copy and paste the private key and make sure you add an ending newline to it. You can save this file either in your `.ssh` directory or wherever if you use the `-i` flag in `ssh`

#### General NIX Os guide 

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

#### Windows
This part of the guide is for windows and maybe if you want to run things more locally in a directory. The setup is logically similar but in practice different because Windows.

Create a suitable directory here you will store everything and also start `ssh` from.

* Download proxytunnel (https://proxytunnel.sourceforge.io/download.php), unzip in your directory. Check that it works by running proxytunnel from a commandline.
* Create the ssh configuration file as per nix instructions. Use relative paths to proxytunnel, and to the config file. eg:   
`ProxyCommand ./proxytunnel -p vpn.balena.srcful.dev:3128 -d %h:22222 -F ./config_file`
* Create the proxytunnel config file as per above (you need the api key also)
* SSH is very sensitive to file rights of the key files - this is a breeze in nix base systems with chmod. In Windows not so much. Use file GUI properties/security. Disable inheritance of rights, add yourself and give full rights to your own user. Remove all other users. This is likely needed or the *config file* and the *private key file*.
* Tunnel as per above to the device you want to login in to
* You should now be ready and run ssh:
`ssh root@localhost -p 22222 -F config_file -i private_key_file`

It seems the powershell variant of ssh is better suited regading file permissions than git-bash.




#### SSH into a docker container

Once you've successfully accessed the host OS through SSH, you can then access the individual service (container) within the device. Balena uses Docker to run services, so you can use Docker commands for this.

To get a list of all running containers, you can use:

```
balena-engine ps
```

And to access a specific container, use the following command:

```
balena-engine exec -it <containerID> /bin/sh
```

Change to `/bin/bash` if needed.


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
