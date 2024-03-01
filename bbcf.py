# Made by Vii for WAVE
# Updated 2024-03-01

# Balance dictionary
chars = {
  #                  v-- Leave at 0 to not change
  # ID: (Name, new maximum HP, original maximum HP)
  #                                       ^-- Please do not touch
     0: ("Ragna", 0, 10_000),
     1: ("Jin", 0, 11_000),
     2: ("Noel", 0, 11_000),
     3: ("Rachel", 0, 11_000),
     4: ("Taokaka", 0, 10_000),
     5: ("Tager", 0, 13_000),
     6: ("Litchi", 0, 11_000),
     7: ("Arakune", 0, 10_500),
     8: ("Bang", 0, 11_500),
     9: ("Carl", 0, 10_000),
    10: ("Hakumen", 0, 12_000),
    11: ("Nu-13", 0, 10_000),
    12: ("Tsubaki", 0, 11_000),
    13: ("Hazama", 0, 11_000),
    14: ("Mu-12", 0, 10_000),
    15: ("Makoto", 0, 11_000),
    16: ("Valkenhayn", 0, 11_500),
    17: ("Platinum", 0, 11_000),
    18: ("Relius", 0, 11_000),
    19: ("Izayoi", 0, 11_000),
    20: ("Amane", 0, 10_500),
    21: ("Bullet", 0, 11_500),
    22: ("Azrael", 0, 12_000),
    23: ("Kagura", 0, 11_500),
    24: ("Kokonoe", 0, 10_500),
    25: ("Terumi", 0, 10_500),
    26: ("Celica", 0, 10_000),
    27: ("Lambda-11", 0, 10_500),
    28: ("Hibiki", 0, 11_000),
    29: ("Nine", 0, 10_500),
    30: ("Naoto", 0, 11_500),
    31: ("Izanami", 0, 10_500),
    32: ("Susanoo", 0, 12_500),
    33: ("Es", 0, 10_500),
    34: ("Mai", 0, 11_000),
    35: ("Jubei", 0, 11_000),
}

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
P1Jubei   = 0xE3F97C
P2Jubei   = 0xE3F980
P1Char    = 0x8919F8
P2Char    = P1Char + 0x20
P1HPCurr  = 0x892998 
P2HPCurr  = 0x89299C
HPOffsetC = 0x9D4
P1HPMax   = 0xE3A9E0
P2HPMax   = 0xE3A9E4
HPOffsetM = 0x9D8

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

def get_value_from_address(process, address, offsets=[]):
    pointer = process.get_pointer(address, offsets=offsets)
    return process.read(pointer)

def set_value_at_address(process, address, value, offsets=[]):
    pointer = process.get_pointer(address, offsets=offsets)
    process.write(pointer, value)

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

# Globals for threads
global_p1 = get_value_from_address(process, base_address + P1Control)
global_p2 = get_value_from_address(process, base_address + P2Control)
global_diff = get_value_from_address(process, base_address + CPU_diff)
global_slide = get_value_from_address(process, base_address + CPU_slide)
global_jubei = 35
jubei_setter1 = False
jubei_setter2 = False
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
		
def func_jubei1():
    while thread_runner:
        while jubei_setter1:
            set_value_at_address(process, base_address + P1Jubei, global_jubei)
            
def func_jubei2():
    while thread_runner:
        while jubei_setter2:
            set_value_at_address(process, base_address + P2Jubei, global_jubei)
        
def func_hp1():
    while thread_runner:
        char_p1 = get_value_from_address(process, base_address + P1Char)
        _, target_hp, max_hp = chars[char_p1]
        if target_hp != 0:
            current_hp = get_value_from_address(process, base_address + P1HPCurr, offsets=[HPOffsetC])
            if current_hp == max_hp:
                set_value_at_address(process, base_address + P1HPMax, target_hp, offsets=[HPOffsetM])
                set_value_at_address(process, base_address + P1HPCurr, target_hp, offsets=[HPOffsetC])
        time.sleep(thread_interval)

def func_hp2():
    while thread_runner:
        char_p2 = get_value_from_address(process, base_address + P2Char)
        _, target_hp, max_hp = chars[char_p2]
        if target_hp != 0:
            current_hp = get_value_from_address(process, base_address + P2HPCurr, offsets=[HPOffsetC])
            if current_hp == max_hp:
                set_value_at_address(process, base_address + P2HPMax, target_hp, offsets=[HPOffsetM])
                set_value_at_address(process, base_address + P2HPCurr, target_hp, offsets=[HPOffsetC])
        time.sleep(thread_interval)

thread_p1 = Thread(target = func_p1)
thread_p2 = Thread(target = func_p2)
thread_diff = Thread(target = func_diff)
thread_slide = Thread(target = func_slide)
thread_jubei1 = Thread(target = func_jubei1)
thread_jubei2 = Thread(target = func_jubei2)
thread_hp1 = Thread(target = func_hp1)
thread_hp2 = Thread(target = func_hp2)
threads = [thread_p1, thread_p2, thread_diff, thread_slide, thread_jubei1, thread_jubei2, thread_hp1, thread_hp2]
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
    
    A) P1 Jubei: {'ON' if jubei_setter1 else 'OFF'}
    S) P2 Jubei: {'ON' if jubei_setter2 else 'OFF'}
    
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
    elif key == 'A' or key == 'a':
	    jubei_setter1 = not jubei_setter1
    elif key == 'S' or key == 's':
	    jubei_setter2 = not jubei_setter2
    elif key == 'Z' or key == 'z':
        process.close()
        b = False
        jubei_setter1 = False
        jubei_setter2 = False
        thread_runner = False
        for t in threads:
            t.join()
