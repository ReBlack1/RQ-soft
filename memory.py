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
import config


"""
get procees ID
"""
def _get_pid():
    for proc in psutil.process_iter():
        if config.proc_name in str(proc.name):
            return proc.pid
    return None

"""
Input - list with 0x-type or int-type move for pointer from base address

TODO check empty list
"""
def _getAddress(move_list):
    base_address = pymem.process.base_address(config.pid)
    move_address = base_address
    for j in range(len(move_list)-1):
        move_address += int(move_list[j])
        move_address = _getValue_In_Address(move_address)
    last_address = move_address + move_list[-1]
    return last_address
"""
Input: INT-type address of value!
"""
def _getValue_In_Address(address, buffer_size = 4):
    PROCESS_VM_READ = 0x0010
    buffer = ctypes.create_string_buffer(buffer_size)
    process = windll.kernel32.OpenProcess(PROCESS_VM_READ,0,config.pid)
    reader_memory = windll.kernel32.ReadProcessMemory

    if reader_memory(process, address, buffer, buffer_size, 0):
            return int.from_bytes(buffer.raw, byteorder='little')

#Возвращает адрес первой такой функции
def _getAddress_from_bytes(_bytes):
    buffer_size = len(_bytes)
    base_address = pymem.process.base_address(config.pid)
    PROCESS_VM_READ = 0x0010
    buffer = ctypes.create_string_buffer(100000000)
    process = windll.kernel32.OpenProcess(PROCESS_VM_READ,0,config.pid)
    reader_memory = windll.kernel32.ReadProcessMemory
    reader_memory(process, base_address, buffer, 100000000, 0)
    move = buffer.raw.find(_bytes)
    if move != -1:
        return base_address + move
#Мб попробовать numpy массивы
#Учесть кучность (???)
#Сделать генератором, а не массиом
#Автоподбор размера буфера по производительности
def _getAddress_from_bytesEx(_bytes, max_len = 10):
    ret_list = []
    base_address = pymem.process.base_address(config.pid)
    PROCESS_VM_READ = 0x0010
    buffer = ctypes.create_string_buffer(config.buffer_size)
    process = windll.kernel32.OpenProcess(PROCESS_VM_READ,0,config.pid)
    reader_memory = windll.kernel32.ReadProcessMemory
    move_sub = base_address + 0x10000000
    move = 0
    count = 0
    up_checker = base_address + 1000000000
    while move_sub < up_checker:
##        print(move_sub)
##        st = time.time()
        reader_memory(process, LPVOID(move_sub), buffer, config.buffer_size, 0)
##        count += 1
        move = buffer.raw.find(_bytes)

        if move == -1:
            move_sub += buffer_size
        else:
            move_sub += move
            ret_list.append(move_sub)
            move_sub += 1

        if len(ret_list) >= max_len:
##            print(count, "count")
            return ret_list
##        print(time.time()-st, 'такт')

    return ret_list

def get_move_dict():
    MOVE_DICTIONARY = {
    "hp"                 :               [0x7CBFD4, 0x4, 0x204],
    "fight"              :               [0x684888, 0x8, 0x8, 0x14, 0x8, 0xD8],
    "target_on_screen"   :               [0x9DD128],
    'cum_value'          :               [0x7CBFE4, 0x54, 0x44],
    'my_person_base'     :               [0x7CBFD4, 0x18, 0xB4494, 0x0],
    'x_pos'              :               [0x9E0714],
    'y_pos'              :               [0x9E0718],
    'z_pos'              :               [0x9E071C],
    'x_ang'              :               [0x9DCEAC],
    'y_ang'              :               [0x9DD064],
    }
    return MOVE_DICTIONARY

def get_move_obj():
    return {
    'id'                 :               0x14,
    'magic_cast'         :               0x18,
    'all_cast'           :               0x58,
    'x_pos'              :               0xF4,
    'y_pos'              :               0xF8,
    'z_pos'              :               0xFC,
    'hp'                 :               0x218,
    'anim'               :               0x21C,
    'target'             :               0x2D4,
    }

def _getAddress_dict(MOVE_DICT = None):
    if MOVE_DICT == None:
        MOVE_DICT = get_move_dict()
    for i in MOVE_DICT:
        MOVE_DICT[i] = _getAddress(MOVE_DICT[i])
    return MOVE_DICT

def _write_to_address(address, input_data,data_size=4):
    PROCESS_ALL_ACCESS = ( 0x000F0000 | 0x00100000 | 0xFFF )
    h_process = windll.kernel32.OpenProcess( PROCESS_ALL_ACCESS, False, int(config.pid) )
    written = c_int(1)
    if type(input_data) == int: #Запись числа
        BufferLocal = ctypes.create_string_buffer(data_size)
        BufferLocal.value = input_data.to_bytes(data_size, byteorder='little')
    elif type(input_data) == bytes: #Запись байтов
        data_size = len(input_data)
        BufferLocal = ctypes.create_string_buffer(data_size)
        BufferLocal.value = input_data
    ans = windll.kernel32.WriteProcessMemory(h_process, address, BufferLocal, data_size, byref(written))

def _make_my_target_func():
    target_func = b'\x8B\x80\xD4\x02\x00\x00\x85\xC0\x74\x04\x83\xC0\xEC\xC3\x33\xC0'
    my_target_func = b'\x8B\x80\xD4\x02\x00\x00\x85\xC0\x74\x0B\x83\xC0\xEC\x90\x90\x90\x90\x90\x90\x90\xC3\x90\x90\xC3'
    addr_target_func = _getAddress_from_bytes(target_func)
    if addr_target_func:
        _write_to_address(addr_target_func, my_target_func) #Если адрес нашелся - меняем переписываем функцию
    else:
        addr_target_func = _getAddress_from_bytes(my_target_func) #Или уже заменял, тогда вернет новый адрес, или ошибка-вернет None
    return addr_target_func

def _find_mobs(_bytes):
    base_address = pymem.process.base_address(config.pid)
    PROCESS_VM_READ = 0x0010
    buffer = ctypes.create_string_buffer(config.buffer_size)
    process = windll.kernel32.OpenProcess(PROCESS_VM_READ,0,config.pid)
    reader_memory = windll.kernel32.ReadProcessMemory
    count = 0
    while config.FIND_MOB_FLAG and config.FARM_FLAG:
        move_sub = base_address + 0x10000000
        while move_sub < base_address + 1000000000:
            reader_memory(process, LPVOID(move_sub), buffer, config.buffer_size, 0)
            move = buffer.raw.find(_bytes)
##            print("Ищу на", move_sub)
            if move == -1:
                move_sub += config.buffer_size
            else:
                move_sub += move
                ln = len(config.public_mob_set)
                config.public_mob_set.add(move_sub)
                if not(config.public_mob_list.__contains__(move_sub)):
                    config.public_mob_list.append(move_sub)
                    print('len list:', len(config.public_mob_list))
                if ln == len(config.public_mob_set):
                    count += 1
                else:
                    print('add',hex(move_sub))
##                if count > 300:
##                    config.FIND_MOB_FLAG = False
                move_sub += 1