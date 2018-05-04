# -*- coding: utf-8 -*-

import memory
import math

#Апроксимация: погрешность +- 3 м.
def _convert_cord(cord):
    del1 = 1049986912
    del2 = 3197134336
    if cord < 2000000000:
        cord -= del1
        cord /= 1000
        return int(0.00000000000127141154 * math.pow(cord, 3) - 0.00000009052023104661 * math.pow(cord, 2) + 0.00156103066680002289 * cord - 1.62538467533931907383)
    else:
        cord -= del2
        cord /= 1000
        return -1 * int(0.00000000000127141154 * math.pow(cord, 3) - 0.00000009052023104661 * math.pow(cord, 2) + 0.00156103066680002289 * cord - 1.62538467533931907383)

def _pred_proc(pid=None, ADDR=None):
    if pid == None:
        pid = memory._get_pid('rqmain.exe')
    if ADDR == None:
        ADDR = memory._getAddress_dict(pid=pid)
    addr_target_func = memory._make_my_target_func(pid) #подготовка функции таргетирования
    if addr_target_func != None:
        ADDR['target_func'] = addr_target_func
    return ADDR

def _kill_id(ADDR, BASE, id, pid=None):
    if pid == None:
        pid = memory._get_pid('rqmain.exe')
    target_func_addr = ADDR['target_func'] + 0xA #Cмещение до цели таргета
    my_target_addr = ADDR['my_person_base'] + BASE['target']
    mov = b'\xB8'
    if type(id) == int:
        id = id.to_bytes(4, byteorder='little')
    new_tagret = mov + id
    memory._write_to_address(my_target_addr, b'\x00\x00\x00\x00', pid=pid)
    #Могут быть проблемы с агрящимся на меня мобом
    memory._write_to_address(target_func_addr, new_tagret, 5, pid=pid)
    return True

def _save_id(ADDR, BASE, pid=None):
    if pid == None:
        pid = memory._get_pid('rqmain.exe')
    old_target = b'\x83\xC0\xEC\x90\x90'
    target_func_addr = ADDR['target_func'] + 0xA
    my_target_addr = ADDR['my_person_base'] + BASE['target']
    my_id = ADDR['my_person_base'] + BASE['id']
##    memory._write_to_address(my_target_addr, my_id, pid=pid)
    memory._write_to_address(target_func_addr, old_target, 5, pid)
    memory._write_to_address(my_target_addr, b'\x00\x00\x00\x00', pid=pid)


pid = memory._get_pid()
ADDR = _pred_proc(pid)
BASE = memory.get_move_obj()
mob_bases = memory._getAddress_from_bytesEx(b'\x7C\x3B\x8F\x01', pid, 4)
##print(hex(mob_bases))
for i in mob_bases:
    print(hex(i))
exit()

my_id = ADDR['my_person_base'] + BASE['id']
my_target_addr = ADDR['my_person_base'] + BASE['target']
print(hex(my_target_addr))

exit()
_kill_id(ADDR, BASE, my_id, pid)
_save_id(ADDR, BASE, pid)