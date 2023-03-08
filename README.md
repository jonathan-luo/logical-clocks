# Scale Models and Logical Clocks ###

Created by Michael Hu, Jonathan Luo and Matt Kiley.

## Description
This is a model of three intercommunicating virtual machines, each of which implement a logical clock using the Lamport timestamp algorithm.

## Usage

### Requirements
To make sure you have all the required modules for this application, run `pip install -r requirements.txt` before continuing!

### Running Model
Run `python model.py`. Logs of the interprocess communication and internal events for virtual machine 1, 2, and 3 will be stored in `p1_log.txt`, `p2_log.txt`, and `p3_log.txt`, respectively.

### Running Tests
Run `python tests.py` to run the unit tests for this program.