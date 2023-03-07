from constants import *
from multiprocessing import Process
from utils import *


def run_model():
    """Runs model with three intercommunicating virtual machines"""

    config1 = [
        (LOCALHOST, PORT_1),
        [(LOCALHOST, PORT_2), (LOCALHOST, PORT_3)],
        "p1_log.csv"
    ]
    p1 = Process(target=machine, args=(config1,))
    config2 = [
        (LOCALHOST, PORT_2),
        [(LOCALHOST, PORT_1), (LOCALHOST, PORT_3)],
        "p2_log.csv"
    ]
    p2 = Process(target=machine, args=(config2,))
    config3 = [
        (LOCALHOST, PORT_3),
        [(LOCALHOST, PORT_1), (LOCALHOST, PORT_2)],
        "p3_log.csv"
    ]
    p3 = Process(target=machine, args=(config3,))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()


if __name__ == '__main__':
    run_model()