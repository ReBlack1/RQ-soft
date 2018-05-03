# -*- coding: utf-8 -*-

import ctypes
from ctypes import *
from ctypes.wintypes import *
import os, psutil
import win32process
import win32api as wa
import pymem
import codecs
import time

"""
get procees ID
"""
def _get_pid(proc_name = 'rqmain.exe'):
    for proc in psutil.process_iter():
        if proc_name in str(proc.name):
            return proc.pid
    return None

def convert_base(num, to_base=10, from_base=10):
    # first convert to decimal number
    if isinstance(num, str):
        n = int(num, from_base)
    else:
        n = int(num)
    # now convert decimal to 'to_base' base
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n < to_base:
        return alphabet[n]
    else:
        return convert_base(n // to_base, to_base) + alphabet[n % to_base]

"""
Input - list with 0x-type or int-type move for pointer from base address

TODO check empty list
"""
def _getAddress(move_list, pid=None):
    #VARIABLE:
    if pid == None:
        pid = _get_pid('rqmain.exe')
    base_address = pymem.process.base_address(pid)
##    print(hex(base_address))
    move_address = base_address
    for j in range(len(move_list)-1):
        move_address += move_list[j]
        move_address = _getValue_In_Address(move_address)
    last_address = move_address + move_list[-1]
    return last_address
"""
Input: INT-type address of value!
"""
def _getValue_In_Address(address, pid=None):
    if pid == None:
        pid = _get_pid('rqmain.exe')
    PROCESS_VM_READ = 0x0010
    buffer_size = 4
    buffer = ctypes.create_string_buffer(buffer_size)
    process = windll.kernel32.OpenProcess(PROCESS_VM_READ,0,pid)
    reader_memory = windll.kernel32.ReadProcessMemory

    if reader_memory(process, address, buffer, buffer_size, 0):
            return int.from_bytes(buffer.raw, byteorder='little')

def get_move_dict():
    MOVE_DICTIONARY = {
    "hp" : [0x7CBFD4, 0x4, 0x204],
    "fight" : [0x684888, 0x8, 0x8, 0x14, 0x8, 0xD8],
    "target_on_screen" : [0x9DD128],
    'mob_num' : [0x7CBFD4, 0x18, 0xB4494, 0x2D4],
    'cum_value' : [0x7CBFE4, 0x54, 0x44],
    'x_pos' : [0x9E0714],
    'y_pos' : [0x9E0718],
    'z_pos' : [0x9E071C]
    }
    return MOVE_DICTIONARY

def _getAddress_dict(MOVE_DICT = None,pid = None):
    if pid== None:
        pid = _get_pid('rqmain.exe')
    if MOVE_DICT == None:
        MOVE_DICT = get_move_dict()
    for i in MOVE_DICT:
        MOVE_DICT[i] = _getAddress(MOVE_DICT[i], pid)
    return MOVE_DICT

def _write_to_address(address, input_data,data_size=4 ,pid=None):
    PROCESS_ALL_ACCESS = ( 0x000F0000 | 0x00100000 | 0xFFF )
    if pid == None:
        pid = _get_pid('rqmain.exe')
    h_process = windll.kernel32.OpenProcess( PROCESS_ALL_ACCESS, False, int(pid) )
    written = c_int(1)
    BufferLocal = ctypes.create_string_buffer(data_size)
    if type(input_data) == int:
        BufferLocal.value = input_data.to_bytes(data_size, byteorder='little')
    elif type(input_data) == bytes:
        BufferLocal.value = input_data
    ans = windll.kernel32.WriteProcessMemory(h_process, address, BufferLocal, data_size, byref(written))
