import gdb
from enum import Enum
import json

class Register(Enum):
    R0 = "r0"
    R1 = "r1"
    R2 = "r2"
    R3 = "r3"
    R4 = "r4"
    R5 = "r5"
    R6 = "r6"
    R7 = "r7"
    R8 = "r8"
    R9 = "r9"
    R10 = "r10"
    R11 = "r11"
    R12 = "r12"
    R13 = "r13"
    R14 = "r14"
    R15 = "r15"
    SP = "sp"
    LR = "lr"
    XPSR = "xpsr"
    # FPSCR = "fpscr"
    # MSP = "msp"
    # PSP = "psp"
    # PRIMASK = "primask"
    # CONTROL = "control"
    # BASEPRI = "basepri"
    # FAULTMASK = "faultmask"
    # PC = "pc"

class ESP32Registers(Enum):
    PC = "pc"
    SP = "sp"
    A0 = "a0"
    A1 = "a1"
    A2 = "a2"
    A3 = "a3"
    A4 = "a4"
    A5 = "a5"
    A6 = "a6"
    A7 = "a7"
    A8 = "a8"
    A9 = "a9"
    A10 = "a10"
    A11 = "a11"
    A12 = "a12"
    A13 = "a13"
    A14 = "a14"
    A15 = "a15"
    A16 = "a16"
    A17 = "a17"
    A18 = "a18"
    A19 = "a19"
    A20 = "a20"
    A21 = "a21"
    A22 = "a22"
    A23 = "a23"
    A24 = "a24"
    A25 = "a25"
    A26 = "a26"
    A27 = "a27"
    A28 = "a28"
    A29 = "a29"
    A30 = "a30"
    A31 = "a31"
    PS = "ps"
    SAR = "sar"
    EXCCAUSE = "exccause"
    EXCVADDR = "excvaddr"
    LBEG = "lbeg"
    LEND = "lend"
    LCOUNT = "lcount"

def set_register(reg_name: Register, value):
    gdb.execute(f"set ${reg_name.value} = {value}")

def get_register(reg_name: Register):
    return int(gdb.parse_and_eval(f"${reg_name.value}"))

def set_byte(address, value):
    gdb.execute(f"set *(unsigned char *){address} = {value}")

def jumpto(address):
    gdb.post_event(lambda: gdb.execute(f"jump *{address}"))

def set_float(address, value):
    gdb.execute(f"set *(float *){address} = {value}")

def stepi():
    gdb.execute("stepi")

def step_continue():
    gdb.execute("c")

def save_esp32_registers(file_path):
    register_values = {}

    for reg in ESP32Registers:
        try:
            value = gdb.parse_and_eval(f"${reg.value}")
            register_values[reg.name] = str(value)
        except gdb.error as e:
            register_values[reg.name] = f"Error reading: {str(e)}"

    with open(file_path, "w") as f:
        json.dump(register_values, f, indent=4)

    print(f"ESP32 registers saved to {file_path}")

def save_arm_registers(file_path):
    register_values = {}

    for reg in Register:
        try:
            value = gdb.parse_and_eval(f"${reg.value}")
            register_values[reg.name] = str(value)
        except gdb.error as e:
            register_values[reg.name] = f"Error reading: {str(e)}"

    with open(file_path, "w") as f:
        json.dump(register_values, f, indent=4)

    print(f"ESP32 registers saved to {file_path}")

def restore_esp32_register(file_path):
    with open(file_path, "r") as f:
        register_values = json.load(f)

    for reg_name, value in register_values.items():
        try:
            gdb.execute(f"set ${reg_name.lower()} = {value}")
            print(f"Register {reg_name} set to {value}")
        except gdb.error as e:
            print(f"Error setting register {reg_name}: {str(e)}")

def restore_arm_register(file_path):
    with open(file_path, "r") as f:
        register_values = json.load(f)

    for reg_name, value in register_values.items():
        try:
            gdb.execute(f"set ${reg_name.lower()} = {value}")
            print(f"Register {reg_name} set to {value}")
        except gdb.error as e:
            print(f"Error setting register {reg_name}: {str(e)}")
