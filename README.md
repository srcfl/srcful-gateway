# Srcful eGW
Architectural overview of the Sourceful Energy Gateway (eGW) project. Perhaps also add an image here. 
* [Srcful eGW](#srcful-egw)
* [Getting started](#getting-started)
  * [Services](#services)
    * [server](#server)
    * [bluetooth](#bluetooth)
        * [Windows](#windows)
    * [client](#client)
    * [modbus_slave](#modbus_slave)
  * [Rest API](#rest-api)
* [Testing](#testing)
* [Design](#design)
* [Other](#other-1)

# Getting started
To get started you need to install `balena-cli` and setup the development environment as described in [this guide](https://open-balena.pages.dev/getting-started/#install-the-balena-cli-on-the-local-machine). This tool is used to deploy the firmware to the open-balena server. Then you need to login to the server to be able to deploy. This is done with the following command:  
```
balena login
```

and select Credentials and use the email and password avaiable in bitwarden. 

More on how to monitor, build and deploy [here](balena.md).


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

## Rest API
The rest API is documented in [api.md](api.md)

# Testing
We use the pytest testing framework for automated testing (https://docs.pytest.org/en/7.2.x/getting-started.html#get-started).

Test modules are placed under `/test` and mirror the structure of the main project. Tests are executed by running:  
`pytest server`

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

## Report test coverage
To see overall test coverage you can run:
```
pytest --cov-report=html --cov=server server/test/
```
from the root folder. Then open `index.html` in `htmlcov` in any browser. 

## REST api integration tests
Automatic integration testing of the REST endpoints can also be done using pytest. However this is more involved as it requires a running server, and an inverter. This can be done either locally or on a rpi.  

Tests are located in a separate folder `server_rest_test`

run with `pytset server_rest_test` or in vscode provided the folder is added to the `.vscode/settings.json`

```json
{
  "python.testing.pytestArgs": [
    "server",
    "server_rest_test"
  ],
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true,
  "python.formatting.provider": "none"
}
```

# Design
The current design is task bases with a priority queue. The idea is that a task is scheduled to happen at a certain time. This allows for fine grained control and adjustment of task times/delays etc. The downside is that tasks cannot be blocking so IO operations typically need threading. Though this is rater easy to do and there are also some helper classes for common tasks that require threading.

On top of the task-engine we can put a state machine so that it becomes easier to know what tasks are high prio in different contexts.

# Other
