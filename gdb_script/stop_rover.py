import sys
import os
# working_dir = '/app'
sys.path.append(os.path.dirname(__file__))
# sys.path.append(f'{working_dir}/src/gdb_interface')
# sys.path.append('/tiff/src/gdb_interface')

import gdb
from gdb_helper import *
import motor

START_ADDRESS = 0x4890
log = open('/tmp/gdb_log', 'w')

class ThrottleWatchpoint(gdb.Breakpoint):
    def __init__(self, address, name):
        super(ThrottleWatchpoint, self).__init__(f"*{address}", type=gdb.BP_WATCHPOINT, wp_class=gdb.WP_ACCESS)
        self.address = address
        self.name = name
        motor.set(204)

    def stop(self):
        # This is very hacky.
        # 000048D2                 STRB            R3, [R2,#(throttle_2000049A - 0x20000498)]
        # 000047E8                 STRB            R2, [R3,#(throttle_2000049A - 0x20000498)]
        pc = get_register(Register.R15)
        if pc == 0x47ea:
            value = get_register(Register.R2)
        else:
            value = get_register(Register.R3)
        # value = gdb.parse_and_eval(f"*{self.address}")
        # print(f"New {self.name} is 0x{value:x} at 0x{pc:x}")
        log.write(f"New {self.name} is 0x{value:x} at 0x{pc:x}\n")
        motor.set(value)
        if value == 0:
            log.close()
            gdb.execute('quit', to_string=True)
        # return True
        return False # Continue execution

class ServoBreakpoint(gdb.Breakpoint):
    def __init__(self, address, name):
        super(ServoBreakpoint, self).__init__(f"*{address}", type=gdb.BP_BREAKPOINT)
        self.address = address
        self.name = name

    def stop(self):
        frame = gdb.selected_frame()
        r1_value = frame.read_register("r1")
        print(f"Breakpoint hit at 0x{self.address:x}. New {self.name} is {r1_value}")
        log.write(f"Breakpoint hit at 0x{self.address:x}. New {self.name} is {r1_value}\n")
        # return True  # DisContinue execution
        return False # Continue execution


# whenver arrive 0x4770, go back to the 0x4890
class HopBreakpoint(gdb.Breakpoint):
    def __init__(self, src, dst):
        super(HopBreakpoint, self).__init__(f"*{src}", type=gdb.BP_BREAKPOINT)
        self.src = src
        self.dst = dst

    def stop(self):
        set_register(Register.R15, self.dst)
        print(f"Breakpoint hit at 0x{self.src:x}. Jump to 0x{self.dst:x}.")
        log.write(f"Breakpoint hit at 0x{self.src:x}. Jump to 0x{self.dst:x}.\n")
        # return True  # DisContinue execution
        return False # Continue execution


def init_value():
    set_byte(0x20000514, 0)
    set_byte(0x200003fd, 0)
    set_byte(0x20000504, 0)
    set_byte(0x2000049a, 0)

def reset_r15():
    set_register(Register.R15, START_ADDRESS)


def function_execute():
    rover_name = 'r1_rover'
    motor.init(rover_name)
    print("Setting up for throttle and servo value interception")
    # set up a read watch points for throttle
    watchpoint = ThrottleWatchpoint(0x2000049a, 'Throttle Value')
    print(f"Access watchpoint set at address 0x{watchpoint.address:x}")
    # Create the breakpoint
    breakpoint = ServoBreakpoint(0x6784, 'Servo Value')
    print(f"Breakpoint set at address 0x{breakpoint.address:x}")

    HopBreakpoint(0x4770, 0x4890)
    init_value()
    print('Setting r15')
    reset_r15()
    

    gdb.execute('continue')

if __name__ == "__main__":
    gdb.execute(f"interpreter-exec mi \"-target-select remote :1234\"")
    function_execute()
