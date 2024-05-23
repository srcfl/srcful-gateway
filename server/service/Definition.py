# definition of a server

import subprocess


class Definition:
    def __init__(self, script: str, port: int):
        self.port = port
        self.script = script
        self.process = None
    
    def spawn(self) -> subprocess.Popen:
        # run the script using the python interpreter as a new process
        # return the process object
        self.process = subprocess.Popen(["python", self.script])
        return self.process

    def terminate(self):
        # terminate the process
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None


def create(script: str, port: int) -> Definition:
    # create a new Definition object
    return Definition(script, port)