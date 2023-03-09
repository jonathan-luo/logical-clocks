import sys
from constants import *
from multiprocessing import Process
from time import sleep
from utils import *


def run_model():
    """Runs model with three intercommunicating virtual machines"""

    # Get simulation duration as command line arg if specified, default is 15 sec
    argv = sys.argv
    RUN_DURATION = 15
    if len(argv) > 1:
        try:
            RUN_DURATION = int(argv[1])
        except TypeError:
            print("Usage: python model.py <run_duration: int>")
            sys.exit(1)

    # Define configs and start each virtual machine as independent Processes
    config1 = [
        (LOCALHOST, PORT_1),
        [(LOCALHOST, PORT_2), (LOCALHOST, PORT_3)],
        LOG_FILE_1,
    ]
    p1 = Process(target=machine, args=(config1,))

    config2 = [
        (LOCALHOST, PORT_2),
        [(LOCALHOST, PORT_1), (LOCALHOST, PORT_3)],
        LOG_FILE_2,
    ]
    p2 = Process(target=machine, args=(config2,))

    config3 = [
        (LOCALHOST, PORT_3),
        [(LOCALHOST, PORT_1), (LOCALHOST, PORT_2)],
        LOG_FILE_3,
    ]
    p3 = Process(target=machine, args=(config3,))

    p1.start()
    p2.start()
    p3.start()

    # Terminate all processes after waiting for run duration + initial wait time
    sleep(RUN_DURATION + INITIAL_WAIT_TIME)
    p1.terminate()
    p2.terminate()
    p3.terminate()


if __name__ == '__main__':
    run_model()