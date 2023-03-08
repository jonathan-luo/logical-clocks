import os
import unittest
import csv
from multiprocessing import Process
from unittest.mock import patch
from utils import machine, server
from time import sleep
from constants import *


class TestProgram(unittest.TestCase):
    def setUp(self):
        self.log_paths = ["p1_log.csv", "p2_log.csv", "p3_log.csv"]

        config1 = [
        (LOCALHOST, PORT_1),
        [(LOCALHOST, PORT_2), (LOCALHOST, PORT_3)],
        self.log_paths[0]
        ]
        self.p1_process = Process(target=machine, args=(config1,))
        
        
        config2 = [
            (LOCALHOST, PORT_2),
            [(LOCALHOST, PORT_1), (LOCALHOST, PORT_3)],
            self.log_paths[1]
        ]
        self.p2_process = Process(target=machine, args=(config2,))
        
        config3 = [
            (LOCALHOST, PORT_3),
            [(LOCALHOST, PORT_1), (LOCALHOST, PORT_2)],
            self.log_paths[2]
        ]
        self.p3_process = Process(target=machine, args=(config3,))
        
        self.p1_process.start()
        self.p2_process.start()
        self.p3_process.start()
        
        # Wait for everything to initialize
        sleep(INITIAL_WAIT_TIME)
        
        # Stop the processes after we have sizeable log files
        sleep(10)
        self.p1_process.terminate()
        self.p2_process.terminate()
        self.p3_process.terminate()
        
    
    def tearDown(self):
        for log_path in self.log_paths:
            if os.path.exists(log_path):
                os.remove(log_path)
        
        
    def test_log_files_exists(self):   
        # Check if log files are created and not empty
        for log_path in self.log_paths:
            self.assertTrue(os.path.exists(log_path))
            self.assertGreater(os.path.getsize(log_path), 0)


    def test_log_file_format(self):
        for log_path in self.log_paths:
            with open(log_path, 'r') as file:
                reader = csv.reader(file)
                
                # Check header row
                header_row = next(reader)
                expected_header = ["Operation", "Global Time", "Logical Time", "Length of Message Queue"]
                self.assertEqual(header_row, expected_header)
                
                # Check number of columns in each row
                for row in reader:
                    expected_num_columns = len(expected_header)
                    self.assertEqual(len(row), expected_num_columns)

      
    def test_log_file_content(self):
        # Check if log file contains the correct operations
        for log_path in self.log_paths:
            with open(log_path, 'r') as file:
                reader = csv.reader(file)
                
                # Skip header row
                next(reader)
                
                # Check if each row contains the correct operation
                for row in reader:
                    operation, global_time, logical_time, queue_len = row
                    self.assertIn(operation, ["Send (1)", "Send (2)", "Send (3)", "Internal Event", "Receive"])
                    
                    if operation == "Receive":
                        self.assertNotEqual(global_time, "N/A")
                    else:
                        self.assertEqual(queue_len, "N/A")

if __name__ == '__main__':
    unittest.main()
    