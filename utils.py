import socket
from constants import *
from datetime import datetime
from random import randrange
from threading import Event, Lock, Thread
from time import sleep


def log_message(file_name, operation, global_time, logical_time, message_contents="N/A"):
    """Helper function to log messages"""

    with log_file_lock:
        with open(file_name, 'a') as log_file:
            log_file.write(f"{operation},{global_time},{logical_time},{message_contents}\n")


def formatted_curr_global_time():
    """Returns formatted current global time"""

    return datetime.now().strftime(TIME_FORMAT)


def machine(config, tick_rate=None, max_op_code=MAX_OPERATION_CODE):
    """Configures virtual machines by initializing both server-side logic
    and creating producers to connect to other machines"""

    # Define locks
    global queue_lock       # For reading/updating queue
    queue_lock = Lock()
    global log_file_lock    # For writing to log file
    log_file_lock = Lock()
    global clock_lock       # For reading/updating logical clock time
    clock_lock = Lock()
    global op_lock          # For reading/updating the operation code
    op_lock = Lock()

    # Define events
    global tick            # For ticks (tells threads when to start again)
    tick = Event()
    global receive         # For receiving messages (two threads per machine, but only one should perform an receive per tick)
    receive = Event()
    global not_receive     # For not receiving messages (if first thread doesn't receive, other must not either)
    not_receive = Event()

    # Declare (global) message queue for machine
    global queue
    queue = []

    # Initialize logical clock
    global logical_time
    logical_time = 0

    # Determine tick duration using RNG if rate not given as parameter
    TICK_DURATION = \
        1 / (tick_rate if tick_rate else randrange(MIN_OPERATION_CODE, MAX_TICKS_RATE + 1))
    print(config[0], TICK_DURATION)

    # Initialize server-side logic
    server_thread = Thread(target=server, args=(config,))
    server_thread.start()

    # Initial delay for other machines to complete
    sleep(INITIAL_WAIT_TIME)

    # Clear log file
    log_file = open(config[2], 'w')

    # Initialize log file
    log_file.write("Operation,Global Time,Logical Time,Length of Message Queue\n")
    log_file.close()

    # Create and connect all producers (stored in `config[1]`)
    for (i, client) in enumerate(config[1]):
        t = Thread(target=producer, args=(config[0], client, config[2], i + 1))
        t.start()

    # Declare operation code variable
    global op_code

    # Busy loop generating operation code and ticks
    while True:
        # Generate operation code
        with op_lock:
            op_code = randrange(MIN_OPERATION_CODE, max_op_code + 1)

        # Increment logical time
        with clock_lock:
            logical_time += 1

        # Release threads by setting tick event
        tick.set()

        # Sleep for tick duration
        sleep(TICK_DURATION)


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
    """Function to continually load messages received into the message queue"""

    # Continually receive messages
    while True:
        data = conn.recv(BUFSIZE)
        if data:
            queue.append(data.decode())


def producer(client_info, server_info, log_file, thread_num):
    """Defines producer (client) logic; i.e., reading from message queue or otherwise performing randomly determined operations"""

    # Use machine's (global) logical clock variable
    global logical_time

    # Chosen thread -- this thread will deal with all logging when duplication may occur
    CHOSEN_THREAD = 1

    try:
        # Create and connect socket
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect(server_info)
        print(f"Client-side connection success from {client_info} to {server_info}")

        while True:
            # Wait for tick
            tick.wait()

            # Get current operation number
            with op_lock:
                op_code_copy = op_code

            # If one thread receives, make sure other doesn't do anything
            queue_lock.acquire()
            if receive.is_set():
                tick.clear()
                queue_lock.release()
                continue

            # If message queue is not empty for the fastest thread, receive message
            if queue and not not_receive.is_set():
                # Mark that this thread is receiving on this tick
                receive.set()

                # Record queue length before popping and message timestamps
                queue_len = len(queue)
                timestamp = int(queue.pop(0))
                queue_lock.release()

                # Reset logical time to maximum of timestamp and logical time minus 1 (since logical time is preincremented in tick loop), plus 1
                # This implements the Lamport Algorithm
                with clock_lock:
                    logical_time = max(timestamp, logical_time - 1) + 1
                    logical_time_copy = logical_time

                # Log that a message was received
                log_message(
                    log_file,
                    "Receive",
                    formatted_curr_global_time(),
                    logical_time_copy,
                    queue_len
                )

            # Else, use RNG to determine which operation to perform
            else:
                # Mark that slower thread(s) should not receive even if queue is non-empty
                not_receive.set()
                queue_lock.release()

                # Obtain logical time
                with clock_lock:
                    logical_time_copy = logical_time

                # If operation number greater than 3, simply log an internal event
                # Second condition ensures that the event is only logged once
                if op_code_copy > 3 and thread_num == CHOSEN_THREAD:
                    log_message(
                        log_file,
                        "Internal Event",
                        formatted_curr_global_time(),
                        logical_time_copy
                    )

                # Else, send message if operation code is equal to the thread number or 3
                elif op_code_copy == thread_num or op_code_copy == 3:
                    # Send message with logical time as its contents
                    s.send(str(logical_time_copy).encode())

                    # Log that a message was sent, avoiding duplicate log when operation code is 3
                    if op_code_copy != 3 or thread_num == CHOSEN_THREAD:
                        log_message(
                            log_file,
                            f"Send ({op_code_copy})",
                            formatted_curr_global_time(),
                            logical_time_copy
                        )

            # Clear all events
            tick.clear()
            receive.clear()
            not_receive.clear()

    except socket.error as e:
        print (f"Error connecting producer: {e}")