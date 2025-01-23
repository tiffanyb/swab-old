import sys
import os
# working_dir = '/app'
sys.path.append(os.path.dirname(__file__))
# sys.path.append(f'{working_dir}/src/gdb_interface')
sys.path.append('/tiff/src/gdb_interface')
import gdb
from gdb_helper import *
import servo
import motor
import sys
from gz.transport13 import Node

START_ADDRESS = 0x4890
log = open('/tmp/gdb_log', 'w')

UPDATE_COMPASS = 0x200003fe
CALLER_UPDATE_COMPASS = 0x478c
ADDRESS_COMPASS = 0x200002DC

class ThrottleWatchpoint(gdb.Breakpoint):
    def __init__(self, address, name):
        super(ThrottleWatchpoint, self).__init__(f"*{address}", type=gdb.BP_WATCHPOINT, wp_class=gdb.WP_ACCESS)
        self.address = address
        self.name = name

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


class ArgPrintBreakpoint(gdb.Breakpoint):
    def __init__(self, address, name):
        super(ArgPrintBreakpoint, self).__init__(f"*{address}", type=gdb.BP_BREAKPOINT)
        self.address = address
        self.name = name

    def stop(self):
        frame = gdb.selected_frame()
        r1_value = frame.read_register("r1")
        # print(f"Breakpoint hit at 0x{self.address:x}. New {self.name} is {r1_value}")
        log.write(f"Breakpoint hit at 0x{self.address:x}. New {self.name} is {r1_value}\n")
        log.flush()
        servo.set('r1_rover', r1_value)
        # return True  # DisContinue execution
        return False # Continue execution


class HopBreakpoint(gdb.Breakpoint):
    def __init__(self, src, dst):
        super(HopBreakpoint, self).__init__(f"*{src}", type=gdb.BP_BREAKPOINT)
        self.src = src
        self.dst = dst

    def stop(self):
        # print(f"Breakpoint hit at 0x{self.src:x}. Jump to 0x{self.dst:x}.")
        log.write(f"Breakpoint hit at 0x{self.src:x}. Jump to 0x{self.dst:x}.\n")
        # gdb.execute(f"jump *{self.dst}")
        gdb.post_event(lambda: gdb.execute(f"jump *{self.dst}"))
        # gdb.execute("continue")
        # I have no idea why, but you need to return True for gdb.post_event
        return True  # DisContinue execution
        # return False # Continue execution

class LoopBreakpoint(gdb.Breakpoint):
    def __init__(self, address):
        super(LoopBreakpoint, self).__init__(f"*{address}", type=gdb.BP_BREAKPOINT)
        self.address = address
        self.hit = 0

    def stop(self):
        set_register(Register.LR, self.address)
        set_register(Register.XPSR, 0x41000000)
        msg = f"Infinite loop hit at 0x{self.address:x}.\n"
        # print(msg)
        # log.write(msg)
        if self.hit == 0:
            msg = "initial setup"
            # print(msg)
            set_byte(0x20000514, 1)
            set_byte(0x200003fd, 0)
            set_byte(UPDATE_COMPASS, 1)
        self.hit += 1

        if self.hit > 300:
            log.close()
            gdb.execute('quit', to_string=True)
        # return True  # DisContinue execution
        return False # Continue execution


class NormalBreakpoint(gdb.Breakpoint):
    def __init__(self, address):
        super(NormalBreakpoint, self).__init__(f"*{address}", type=gdb.BP_BREAKPOINT)
        self.address = address

    def stop(self):
        # gdb.execute('stepi')
        set_float(ADDRESS_COMPASS, 100.0)
        # jumpto(0x4790)
        log.write("Setting Compass value to 100 degree\n")
        print("Setting Compass value to 100 degree")
        gdb.post_event(lambda: gdb.execute(f"jump *0x4790"))
        # gdb.execute(f"jump *0x4790")
        return True  # DisContinue execution
        # return False # Continue execution



def function_execute():
    rover_name = 'r1_rover'
    servo.init('default', rover_name)
    motor.init(rover_name)
    print("Setting up for throttle and servo value interception")
    # set up a read watch points for throttle
    watchpoint = ThrottleWatchpoint(0x2000049a, 'Throttle Value')
    print(f"Access watchpoint set at address 0x{watchpoint.address:x}")
    # Create the breakpoint
    breakpoint = ArgPrintBreakpoint(0x6784, 'Servo Value')
    print(f"Breakpoint set at address 0x{breakpoint.address:x}")
    
    """
    1. B 0x1f54, callback: Set $r15 = 0x46f0
    2. B 0x46f0: set $lr = 0x46f0, set $xpsr = 0x41000000
    3. Set 0x20000514 = 1 (autodrive)
    4. Set 0x200003FD = 0 (don’t check position)
    5. Set 200003FE = 1 (update compass)
    6. B 0x478c, callback: set *(float*)200002DC = 100.0 (random value), Set $r15 = 0x4790
    """

    print("Setting up floating point enabling setting")
    HopBreakpoint(0x1f54, 0x46f0)

    print("Setting up looped process_motors")
    msg = f"Infinite loop set at 0x46f0.\n"
    print(msg)
    log.write(msg)
    LoopBreakpoint(0x46f0)

    print("Setting up hooked compass update value")
    NormalBreakpoint(CALLER_UPDATE_COMPASS)    # 0x478c

    gdb.execute('continue')


if __name__ == "__main__":
    gdb.execute(f"interpreter-exec mi \"-target-select remote :1234\"")
    function_execute()
