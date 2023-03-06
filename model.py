import os
import socket
import time
from config import *
from datetime import datetime
from multiprocessing import Process
from random import randrange
from threading import Thread, Lock


def log_message(operation, global_time, logical_time, file_name, message_contents=""):
    """Helper function to log messages"""

    with log_file_lock:
        with open(file_name, 'a') as log_file:
            print_func = log_file.write

            print_func(f"Operation: {operation}\n")
            print_func(f"Global Time: {global_time}\n")
            print_func(f"Logical Time: {logical_time}\n")

            if message_contents != "":
                print_func(f"{message_contents}\n")

            print_func("\n")


def formatted_curr_global_time():
    """Returns formatted current global time"""

    return datetime.now().strftime(TIME_FORMAT)


def machine(config):
    """Configures virtual machines by initializing both server-side logic
    and creating producers to connect to other machines"""

    # Thread locks for queue, writing to log file, and updating logical clock time
    global queue_lock
    queue_lock = Lock()
    global log_file_lock
    log_file_lock = Lock()
    global clock_lock
    clock_lock = Lock()

    # Record process ID
    config.append(os.getpid())

    # Initialize server-side logic and wait for other machines to complete
    server_thread = Thread(target=server, args=(config,))
    server_thread.start()
    time.sleep(5)

    # Clear log file
    log_file = open(config[2], 'w')
    log_file.close()

    # Initialize logical clock
    global logical_time
    logical_time = 0

    # Create and connect all producers (stored in `config[1]`)
    for client in config[1]:
        t = Thread(target=producer, args=(config[0], client, config[2]))
        t.start()


def server(config):
    """Configures server-side logic for machines"""

    server_info = config[0]
    print(f"Starting server at {server_info}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(server_info)
    s.listen()

    # Continue accepting new connections
    while True:
        conn, _ = s.accept()
        t = Thread(target=consumer, args=(conn,))
        t.start()


def consumer(conn):
    print(f"Consumer accepted connection `{conn}`\n")

    global queue
    queue = []

    while True:
        data = conn.recv(BUFSIZE)
        msg = data.decode()
        if msg != '':
            with queue_lock:
                queue.append(msg)


def producer(server_info, client_info, log_file):
    global logical_time
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    # Determine tick duration using RNG
    TICK_DURATION = 1 / randrange(MIN_OPERATION_NUM, MAX_TICKS_PER_SEC + 1)

    try:
        s.connect(server_info)
        print(f"Client-side connection success from {client_info} to {server_info}\n")

        while True:
            # Sleep for tick duration
            time.sleep(TICK_DURATION)

            # If message queue is not empty, receive message
            queue_lock.acquire()
            if queue:
                timestamp = int(queue.pop(0))
                queue_len = len(queue)
                queue_lock.release()

                with clock_lock:
                    logical_time = max(timestamp, logical_time) + 1

                    # Log that a message was received
                    log_message(
                        "Receive" + f" {server_info}",
                        formatted_curr_global_time(),
                        logical_time,
                        log_file,
                        f"Length of Message Queue: {queue_len}"
                    )

            # Else, use RNG to determine which operation to perform
            else:
                queue_lock.release()
                # Generate operation number
                op = randrange(MIN_OPERATION_NUM, MAX_OPERATION_NUM + 1)

                with clock_lock:
                    # Update logical time
                    logical_time += 1

                    # If operation number greater than 3, simply log an internal event
                    if op > 3:
                        log_message(
                            "Internal Event" + f" {server_info}",
                            formatted_curr_global_time(),
                            logical_time,
                            log_file
                        )

                    # Else, handle operation accordingly
                    else:
                        s.send(str(logical_time).encode())

                        # TODO: Implement behavior according to 1, 2, 3

                        # Log that a message was sent
                        log_message(
                            "Send" + f" {server_info}",
                            formatted_curr_global_time(),
                            logical_time,
                            log_file
                        )

    except socket.error as e:
        print (f"Error connecting producer: {e}")


def run_model():
    port1 = 2056
    port2 = 3056
    port3 = 4056

    config1 = [
        (LOCALHOST, port1),
        [(LOCALHOST, port2), (LOCALHOST, port3)],
        "p1_log.txt"
    ]
    p1 = Process(target=machine, args=(config1,))
    config2 = [
        (LOCALHOST, port2),
        [(LOCALHOST, port1), (LOCALHOST, port3)],
        "p2_log.txt"
    ]
    p2 = Process(target=machine, args=(config2,))
    config3 = [
        (LOCALHOST, port3),
        [(LOCALHOST, port1), (LOCALHOST, port2)],
        "p3_log.txt"
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