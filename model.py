from config import *
from virtual_machine import *

def run_model():
    HOST = socket.gethostbyname(socket.gethostname())
    vm1 = VirtualMachine("vm1", HOST, PORT_1)
    vm2 = VirtualMachine("vm2", HOST, PORT_2)
    vm3 = VirtualMachine("vm3", HOST, PORT_3)

    vm1.connect(vm2)
    vm1.connect(vm3)


if __name__ == "__main__":
    run_model()