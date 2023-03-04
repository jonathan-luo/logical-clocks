import socket
import threading
import time
from config import *
from random import randrange
from textwrap import dedent


def log_message(operation, global_time, logical_time, message_contents=""):
    """Helper function to log messages"""

    print(dedent(f'''\
        Operation: {operation}
        Global Time: {global_time}
        Logical Time: {logical_time}
    '''))

    if message_contents != "":
        print(message_contents)


def formatted_curr_global_time():
    """Returns formatted current global time"""

    return time.strftime(TIME_FORMAT, time.localtime())


class VirtualMachine:
    def __init__(self, name, host, port):
        self.queue = []  # Message queue

        self.NAME = name
        self.HOST = host
        self.PORT = port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        print(f"Socket started on host {host} and port {port}")

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def connect(self, other):
        """Connect this virtual machine to an `other` machine"""

        self.client.connect((other.HOST, other.PORT))
        print(f"Connected to VirtualMachine `{other.NAME}`.")

        # Start message process thread
        message_process_thread = threading.Thread(
            target=self.process_messages, args=())
        message_process_thread.start()

        # Allow other virtual machine to accept connection
        other.accept_connection()


    def accept_connection(self):
        """Accept a connection"""

        client, address = self.server.accept()
        print(f"Accepted connection from {address}")

        # Start receive thread
        message_receive_thread = threading.Thread(
            target=self.receive_messages, args=(client, address))
        message_receive_thread.start()


    def receive_messages(self, client, address):
        """Function to continually receive messages from `client` socket"""

        # Wait for everything to initialize
        time.sleep(INITIAL_WAIT_TIME)

        while True:
            message = client.recv(BUFSIZE).decode()

            if message:
                self.queue.append(message)


    def process_messages(self):
        """Function to handle processing messages from queue and sending messages"""

        # Determine tick duration using RNG
        TICK_DURATION = 1 / randrange(MIN_OPERATION_NUM, MAX_TICKS_PER_SEC + 1)
        logical_time = 0

        # Wait for everything to initialize
        time.sleep(INITIAL_WAIT_TIME)

        while True:
            # Sleep for tick duration
            time.sleep(TICK_DURATION)

            # If message queue is not empty, receive message
            if self.queue:
                timestamp = int(self.queue.pop(0))
                logical_time = max(timestamp, logical_time) + 1

                # Log that a message was received
                log_message(
                    "Receive" + f" ({self.NAME})",
                    formatted_curr_global_time(),
                    logical_time,
                    f"Length of Message Queue: {len(self.queue)}"
                )

            # Else, use RNG to determine which operation to perform
            else:
                # Generate operation number and update logical time
                op = randrange(MIN_OPERATION_NUM, MAX_OPERATION_NUM + 1)
                logical_time += 1

                # If operation number greater than 3, simply log an internal event
                if op > 3:
                    log_message(
                        "Internal Event" + f" ({self.NAME})",
                        formatted_curr_global_time(),
                        logical_time
                    )

                # Else, handle operation accordingly
                else:
                    self.client.send(f"{logical_time}".encode())

                    # TODO: Implement behavior according to 1, 2, 3

                    # Log that a message was sent
                    log_message(
                        "Send" + f" ({self.NAME})",
                        formatted_curr_global_time(),
                        logical_time
                    )

