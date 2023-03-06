# Design Notebook: Scale Models and Logical Clocks ###

## Overall Design
As inspired by the code presented in section, we decided to design our model to consist of three Processes (representing intercommunicating virtual machines), each of which spawned server/consumer and producer threads to receive and send messages, respectively. Furthermore, the producer threads also perform the four operations noted in the assignment specification (send message to another machine, send message to the other machine, send message to both other machines, and internal event), as determined by a random number generator (Python's `random.randrange` function) per clock tick (clock tick duration is also randomly determined, using `1 / random.randrange(1, 7)`).

To enhance organization and modularity, constants in our code are stored in `config.py`.

## Thread Safety
To ensure clean logging, mutex locks were used. This prevent multiple threads from writing to the logging file at once, and thereby resulting in overlapping, jumbled log messages. Similarly, to prevent race conditions with the message queue and the logical clock variable, a lock is required whenever an update or read operation is performed on either one of them (and in the case of the message queue, when an item is popped from the queue).

## Unit Testing
TODO