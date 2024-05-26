import subprocess

import logging
log = logging.getLogger(__name__)


def as_process():
    # Specify the script and arguments
    command = ['python', './server/crypto/revive.py']

    # Run the command as a subprocess and capture the output
    result = subprocess.run(command, capture_output=True, text=True, check=False)    # Check if the subprocess executed successfully
    log.debug("Revive Script output: %s", result.stdout)
    if result.returncode != 0:
        log.error("Revive Script Error: %s", result.stderr)

    return result.stdout
