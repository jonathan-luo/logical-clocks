# Design Notebook: Scale Models and Logical Clocks ###

## Overall Design
As inspired by the code presented in section, we decided to design our model to consist of three Processes (representing intercommunicating virtual machines), each of which spawned 1 server thread, 1 consumer thread and 2 producer threads to handle clock ticking and logical clock incrementation, message receipt (through sockets) and loading into the global queue, and sending messages to each of the other machines, respectively. Otherwise put, instead of unidirectional, we made the connections bidirectional between each pair of virtual machines.

Each producer thread consists of a busy while loop containing the logic to determine which of the five operations ((1) send message to another machine, (2) send message to the other machine (i.e., not the machine from (1)), (3) send message to both other machines, (4) internal event, and (5) receive message) to perform during a given clock tick. The operation performed is as a result of a number of checks -- first, if during a tick, the message queue is not empty, then one thread will receive the message, update the logical clock, and then log the receipt of the message; otherwise, a random number generator (Python's `random.randrange` function) determines the operation per clock tick (clock tick duration is also randomly determined, using `1 / random.randrange(1, 7)`).

A busy while loop also handles clock ticking and logical clock incrementation in the server thread. In the case of message receipt, the logical clock is also updated within the `producer` function, in accordance with the message receipt portion of the Lamport Algorithm (the new logical clock value is the maximum of the timestamp of the message received and the current logical time, plus 1).

To enhance organization and modularity, constants in our code are stored in `constants.py`, and useful thread functions (e.g., `machine`, `server`, `consumer`, and `producer`, among others) are stored in `utils.py`. The code to run the model is thus quite short, and all stored in `model.py`, which can be directly run in the terminal.

## Thread Safety
To ensure clean logging, mutex locks were used. This prevent multiple threads from writing to the logging file at once, and thereby resulting in overlapping, jumbled log messages. Similarly, to prevent race conditions with the message queue, the logical clock variable, and the operation code variable, a lock is required whenever an update or read operation is performed on any one of them (and in the case of the message queue, when an item is popped from the queue).

Furthermore, numerous thread events were used to ensure that even though there are multiple producer threads per machine, only ONE event occurs per clock tick. This was rather difficult to implement, and took much trial-and-error, and involved using `Event.wait()` calls within producers to ensure that threads only began once the clock tick loop set the `tick` event. This `tick` event is then cleared whenever a producer thread completes an iteration in the busy while loop.

The `receive` event serves the purpose of notifying the slower thread to not receive when the faster thread has already received a message. It is set when the faster thread finds that the message queue is not empty during a clock tick. It is cleared once the faster thread reaches the end of its iteration (effectively the end of the clock tick).

The `not_receive` method notifies the slower thread to not receive in the case that the queue becomes non-empty between the time in which the faster thread checks that it is empty and the slower thread checks that it is empty (if we did not have this check, the faster thread may find that the queue is empty, and possibly send a message, but then, in the same clock tick, the slower thread would receive a message -- this is TWO events in one clock tick, which is not desired). This event is set when the faster thread finds that the queue is empty and is cleared once either thread reaches the end of its iteration/end of clock tick.

## Logging
To make it simple for us to later analyze the results of our simulations, we logged each of the virtual machine's operations in CSV format in CSV files.

## Unit Testing
TODO