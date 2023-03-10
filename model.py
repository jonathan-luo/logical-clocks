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
    CONSTANTS = None, None, None
    MAXOPS = MAX_OPERATION_CODE, MAX_OPERATION_CODE, MAX_OPERATION_CODE
    if len(argv) >= 1:
        try:
            RUN_DURATION = int(argv[1])
        except ValueError:
            print("Usage: python model.py <run_duration: int>")
            sys.exit(1)
            
    if len(argv) >= 4:
        try:
            CONSTANTS = int(argv[2]), int(argv[3]), int(argv[4])
        except ValueError:
            print("Usage: python model.py <run_duration: int> <constant1: int> <constant2: int> <constant3: int>")
            sys.exit(1)
    
    if len(argv) >= 7:
        try:
            MAXOPS = int(argv[5]), int(argv[6]), int(argv[7])
        except ValueError:
            print("Usage: python model.py <run_duration: int> <constant1: int> <constant2: int> <constant3: int> <maxop1: int> <maxop2: int> <maxop3: int>")
            sys.exit(1)
    

    # Define configs and start each virtual machine as independent Processes
    config1 = [
        (LOCALHOST, PORT_1),
        [(LOCALHOST, PORT_2), (LOCALHOST, PORT_3)],
        LOG_FILE_1,
    ]
    p1 = Process(target=machine, args=(config1, CONSTANTS[0], MAXOPS[0]))

    config2 = [
        (LOCALHOST, PORT_2),
        [(LOCALHOST, PORT_1), (LOCALHOST, PORT_3)],
        LOG_FILE_2,
    ]
    p2 = Process(target=machine, args=(config2, CONSTANTS[1], MAXOPS[1]))

    config3 = [
        (LOCALHOST, PORT_3),
        [(LOCALHOST, PORT_1), (LOCALHOST, PORT_2)],
        LOG_FILE_3,
    ]
    p3 = Process(target=machine, args=(config3, CONSTANTS[2], MAXOPS[2]))

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