# Made by Vii for WAVE
# Updated 2023-02-01

import os
from ReadWriteMemory import ReadWriteMemory
from threading import Thread
import time

# Get BBCF.exe
import psutil
import win32process
import win32api

not_found = True
while not_found:
    try:
        print("Searching for BBCF.exe.")
        bbcf_pid = None
        pids = psutil.pids()
        for pid in pids:
            ps = psutil.Process(pid)
            if 'BBCF.exe' in ps.name():
                bbcf_pid = ps.pid
                not_found = False
    except:
        print("BBCF.exe was not found.")
        print("Retrying in 10 seconds.")
        time.sleep(10)

# Magic code from StackOverflow
PROCESS_ALL_ACCESS = 0x1F0FFF
processHandle = win32api.OpenProcess(PROCESS_ALL_ACCESS, False, bbcf_pid)
modules = win32process.EnumProcessModules(processHandle)
processHandle.close()
base_addr = modules[0] # The first BBCF better be the right one

# Values obtained from CE
base_address = base_addr # BBCF.exe+0
P1Control = 0x891A08
P2Control = P1Control + 0x20
CPU_diff  = 0x8F85F4
CPU_slide = 0xE9A57C

# Get BBCF process
rwm = ReadWriteMemory()
not_found = True
process = None
while not_found:
    try:
        process = rwm.get_process_by_name('BBCF.exe')
        not_found = False
    except:
        print("BBCF.exe was not found.")
        print("Retrying in 10 seconds.")
        time.sleep(10)
process.open()

def get_value_from_address(process, address):
    pointer = process.get_pointer(address)
    return process.read(pointer)

def set_value_at_address(process, address, value):
    pointer = process.get_pointer(address)
    process.write(pointer, value)

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

# Globals for threads
global_p1 = get_value_from_address(process, base_address + P1Control)
global_p2 = get_value_from_address(process, base_address + P2Control)
global_diff = get_value_from_address(process, base_address + CPU_diff)
global_slide = get_value_from_address(process, base_address + CPU_slide)
thread_runner = True
thread_interval = 0.1

# Blegh code duplication but I can't think of a better way without pointers
def func_p1():
    while thread_runner:
        set_value_at_address(process, base_address + P1Control, global_p1)
        time.sleep(thread_interval)

def func_p2():
    while thread_runner:
        set_value_at_address(process, base_address + P2Control, global_p2)
        time.sleep(thread_interval)

def func_diff():
    while thread_runner:
        set_value_at_address(process, base_address + CPU_diff, global_diff)
        time.sleep(thread_interval)

def func_slide():
    while thread_runner:
        set_value_at_address(process, base_address + CPU_slide, global_slide)
        time.sleep(thread_interval)

thread_p1 = Thread(target = func_p1)
thread_p2 = Thread(target = func_p2)
thread_diff = Thread(target = func_diff)
thread_slide = Thread(target = func_slide)
threads = [thread_p1, thread_p2, thread_diff, thread_slide]
for t in threads:
    t.setDaemon(True)
    t.start()

# CLI loop
b = True
while b:
    #p1_status = get_value_from_address(process, base_address + P1Control)
    #p2_status = get_value_from_address(process, base_address + P2Control)
    #difficulty_status = get_value_from_address(process, base_address + CPU_diff)
    #slider_status = get_value_from_address(process, base_address + CPU_slide)
    p1_status = global_p1
    p2_status = global_p2
    difficulty_status = global_diff
    slider_status = global_slide
    cls()
    print("BBCF CPU vs CPU by Vii")
    print(f"""
    Q) P1 Control: {'Player' if p1_status else 'CPU'}
    W) P2 Control: {'Player' if p2_status else 'CPU'}
    E) Difficulty: {difficulty_status}/5
    R) GUI slider: {slider_status}/5
    
    Z) Exit
""")
    key = input()
    if key == 'Q' or key == 'q':
        global_p1 = 0 if p1_status else 1
        #set_value_at_address(process, base_address+P1Control, v)
    elif key == 'W' or key == 'w':
        global_p2 = 0 if p2_status else 1
        #set_value_at_address(process, base_address+P2Control, v)
    elif key == 'E' or key == 'e':
        global_diff = (difficulty_status + 1) % 6
        #set_value_at_address(process, base_address+CPU_diff, v)
    elif key == 'R' or key == 'r':
        global_slide = (difficulty_status + 1) % 6
        #set_value_at_address(process, base_address+CPU_slide, v)
    elif key == 'Z' or key == 'z':
        process.close()
        b = False
        thread_runner = False
        for t in threads:
            t.join()
