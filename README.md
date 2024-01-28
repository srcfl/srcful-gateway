# Srcful eGW
Architectural overview of the Sourceful Energy Gateway (eGW) project. Perhaps also add an image here. 
* [Srcful eGW](#srcful-egw)
* [Getting started](#getting-started)
  * [Services](#services)
    * [server](#server)
    * [bluetooth](#bluetooth)
        * [Windows](#windows)
  * [Rest API](#rest-api)
* [Testing](#testing)
  * [Report test coverage](#report-test-coverage)
  * [REST api integration tests](#rest-api-integration-tests)
  * [ble REST api integration tests](#ble-rest-api-integration-tests)
* [Code standard](#code-standard)
* [Design](#design)
* [Other](#other-1)

# Getting started
To get started you need to install `balena-cli` and setup the development environment as described in [this guide](https://open-balena.pages.dev/getting-started/#install-the-balena-cli-on-the-local-machine). This tool is used to deploy the firmware to the open-balena server. Then you need to login to the server to be able to deploy. This is done with the following command:  
```
balena login
```

and select Credentials and use the email and password avaiable in bitwarden. 

More on how to monitor, build and deploy [here](balena.md).


## Branching strategy
In general one issue is one branch. For smaller issues you can work directly in eg. Dev.

*main* is stable branch for development. Basically this branch should be safe to create working branches from. This branch would be "locked" at some point then things are tested and finally merged into a fleet release branch.

*fleet-x* is deploy branch connected to a particular fleet (x would be the fleet name e.g. beta). It is ok to have your own fleet and branch for that particular fleet if you feel the need for it.


## Services 
The gateway is composed of two services that are deployed as docker containers. Only web and bluetooth are deployed to the gateway. The other services are for testing and development.

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

## Rest API
The rest API is documented in [api.md](api.md) but this documentation is always one step behind so use the gateway REST endpoint `doc` to get the latest version.

# Testing
We use the pytest testing framework for automated testing (https://docs.pytest.org/en/7.2.x/getting-started.html#get-started).

Unit test modules are placed under `/server_unit_test` and mirror the structure of the main project. Tests are executed by running:  
`pytest server_unit_test`

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

For vscode add test folders to the `.vscode/settings.json`

```json
{
  "python.testing.pytestArgs": [
    "server_unit_test",
    "server_rest_test",
    "ble_rest_test"
  ],
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true,
  "python.formatting.provider": "none"
}
```

## Report test coverage
pytest can issue a coverage report using the plugin pytest-cov. Install with

```
pip install pytest-cov
```

To see overall test coverage you can run:
```
pytest --cov-report=html --cov=server server_unit_test
```
from the root folder. Then open `index.html` in `htmlcov` in any browser. 

## REST api integration tests
Automatic integration testing of the REST endpoints can also be done using pytest. However this is more involved as it requires a running server, and an inverter. This can be done either locally or on a rpi.  

Tests are located in a separate folder `server_rest_test`

## ble REST api integration tests
You can test the ble service REST endpoints using pytest. Note that this is a work in progress. As for the normal API tests this is more involved and bascially requires a running gateway so the ble service is up and running.

One caveat is that (windows specific) you cannot connect to the same ble service from the same client (eg running the tests and having the configurator connected on the same computer)

Another caveat that remains to be solved is that pytest can start running these calls in parralell. E.g. make every ble call the same time and this will not work for obvious reasons - some tests will time out.

It seems like running each file with tests separately solves this for now. I.e you run it like:

```
pytest ./ble_rest_test/get.py
```

# Code standard
Basically `flake8` with pep8 naming and `bugbear`. Use the flake8 vscode extension and also install pep8-naming (`pip install pep8-naming`) and bugbear (`pip install pip install flake8-bugbear`). There is a config file for the project (`.flake8`)

Black is a nice vscode extension to fix basic formatting.

We allow long lines as some strings etc. will become very wonky. Black will do its best and that is fine for 90% of the code. But feel free to have longer lines of code if this makes it more readable.

**pyLint** - voluntary use the vscode extension, it catches many important issues but also paints your code :P A lot of documentation for functions etc are not present and this is currently not a prio. Possibly some energy on configuration could be put here.

# Design
The current design is task bases with a priority queue. The idea is that a task is scheduled to happen at a certain time. This allows for fine grained control and adjustment of task times/delays etc. The downside is that tasks cannot be blocking so IO operations typically need threading. Though this is rater easy to do and there are also some helper classes for common tasks that require threading.

On top of the task-engine we can put a state machine so that it becomes easier to know what tasks are high prio in different contexts.

# Other
