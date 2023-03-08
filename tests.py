import os
import unittest
import socket
from multiprocessing import Process
from unittest.mock import patch
from utils import machine, server
from time import sleep
from constants import *


class TestProgram(unittest.TestCase):
    def setUp(self):
        self.p1_log_path = "p1_log.csv"
        self.p2_log_path = "p2_log.csv"
        self.p3_log_path = "p3_log.csv"

        config1 = [
        (LOCALHOST, PORT_1),
        [(LOCALHOST, PORT_2), (LOCALHOST, PORT_3)],
        "p1_log.csv"
        ]
        self.p1_process = Process(target=machine, args=(config1,))
        
        
        config2 = [
            (LOCALHOST, PORT_2),
            [(LOCALHOST, PORT_1), (LOCALHOST, PORT_3)],
            "p2_log.csv"
        ]
        self.p2_process = Process(target=machine, args=(config2,))
        
        config3 = [
            (LOCALHOST, PORT_3),
            [(LOCALHOST, PORT_1), (LOCALHOST, PORT_2)],
            "p3_log.csv"
        ]
        self.p3_process = Process(target=machine, args=(config3,))
        
        self.p1_process.start()
        self.p2_process.start()
        self.p3_process.start()
        
        # Wait for everything to initialize
        sleep(INITIAL_WAIT_TIME)
        
    
    def tearDown(self):
        self.p1_process.terminate()
        self.p2_process.terminate()
        self.p3_process.terminate()

        os.remove(self.p1_log_path)
        os.remove(self.p2_log_path)
        os.remove(self.p3_log_path)
        
        
    def test_run_model(self):   
        # Check if log files are created and not empty
        sleep(1)
        self.assertTrue(os.path.exists(self.p1_log_path))
        self.assertGreater(os.path.getsize(self.p1_log_path), 0)
        self.assertTrue(os.path.exists(self.p2_log_path))
        self.assertGreater(os.path.getsize(self.p2_log_path), 0)
        self.assertTrue(os.path.exists(self.p3_log_path))
        self.assertGreater(os.path.getsize(self.p3_log_path), 0)
        
        print("Passed test_run_model()")
        

if __name__ == '__main__':
    program = TestProgram()
    program.setUp()
    program.test_run_model()
    program.tearDown()
    