# -*- coding: utf-8 -*-

import memory
import math
import controler
import datetime, time
import win32gui as wg, win32con as wc

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
    my_id = ADDR['my_person_base'] + BASE['id']
##    print(hex(memory._getAddress([0x7CBFD4, 0x18, 0xB4494, 0x0],pid=pid)))
##    print(hex(my_id))
    if type(id) == int:
        base = id - 0x14
        base = base.to_bytes(4, byteorder='little')
    new_tagret = mov + base
##    print(base)
    memory._write_to_address(my_target_addr, b'\x00\x00\x00\x00', pid=pid)
    #Могут быть проблемы с агрящимся на меня мобом
    memory._write_to_address(target_func_addr, new_tagret, 5, pid=pid)
    memory._write_to_address(my_target_addr, my_id, pid=pid)
    return True

def _save_id(ADDR, BASE, pid=None):
    if pid == None:
        pid = memory._get_pid('rqmain.exe')
    old_target = b'\x83\xC0\xEC\x90\x90'
    target_func_addr = ADDR['target_func'] + 0xA
    my_target_addr = ADDR['my_person_base'] + BASE['target']
    my_id = ADDR['my_person_base'] + BASE['id']
    memory._write_to_address(my_target_addr, b'\x00\x00\x00\x00', pid=pid)
##    memory._write_to_address(my_target_addr, my_id, pid=pid)
    memory._write_to_address(target_func_addr, old_target, 5, pid)
    memory._write_to_address(my_target_addr, b'\x00\x00\x00\x00', pid=pid)

#Проверка моб ли это через хп и анимацию
#TODO проверка на расстояние
def _check_id(id, BASE, ADDR, pid=None):
    if pid == None:
        pid = memory._get_pid('rqmain.exe')
    base = id - 0x14
    hp = memory._getValue_In_Address(base + BASE['hp'])
    animation = memory._getValue_In_Address(base + BASE['anim'])

    #Поиск и конвертирование своих и чужих координат для сравнения
    x_pos = memory._getValue_In_Address(base + BASE['x_pos'], pid)
    y_pos = memory._getValue_In_Address(base + BASE['y_pos'], pid)
    x_pos = _convert_cord(x_pos)
    y_pos = _convert_cord(y_pos)
    my_x_pos = memory._getValue_In_Address(ADDR['my_person_base'] + BASE['x_pos'], pid)
    my_y_pos = memory._getValue_In_Address(ADDR['my_person_base'] + BASE['y_pos'], pid)
    my_x_pos = _convert_cord(my_x_pos)
    my_y_pos = _convert_cord(my_y_pos)

    mob = memory._getValue_In_Address(base, pid, 2)
    if mob != 15228 and mob != None:
##        print(mob)
##        print(hex(base))
##        print(hp)
##        print(animation)
        return False
    if hp == None or animation == None or mob == None:
        return False
    hp_flag = hp < 300 and hp > 0 #> 0 and hp < 1000000
    anim_flag = animation > 0 and animation < 6
    mob_flag = mob == 15228 #Первые 2 байта каждого моба
    pos_flag = math.fabs(my_x_pos - x_pos) < 15 and math.fabs(my_y_pos - y_pos) < 15 #10м это примерно на экране

    if hp_flag and anim_flag and mob_flag and pos_flag:
        return True
    return False

def _make_mob_bytes(ADDR, BASE, pid=None):
    if pid == None:
        pid = memory._get_pid('rqmain.exe')
    a = b'\x7C\x3B'
    b = memory._getValue_In_Address(ADDR['my_person_base'] + 0x2,pid,2)
    b = int.to_bytes(b, 2, byteorder='little')
    return a + b

def _print_id(id, BASE, ADDR, pid=None):
    if pid == None:
        pid = memory._get_pid('rqmain.exe')
    base = id - 0x14
    hp = memory._getValue_In_Address(base + BASE['hp'])
    animation = memory._getValue_In_Address(base + BASE['anim'])

    #Поиск и конвертирование своих и чужих координат для сравнения
    x_pos = memory._getValue_In_Address(base + BASE['x_pos'], pid)
    y_pos = memory._getValue_In_Address(base + BASE['y_pos'], pid)
    x_pos = _convert_cord(x_pos)
    y_pos = _convert_cord(y_pos)
    my_x_pos = memory._getValue_In_Address(ADDR['my_person_base'] + BASE['x_pos'], pid)
    my_y_pos = memory._getValue_In_Address(ADDR['my_person_base'] + BASE['y_pos'], pid)
    my_x_pos = _convert_cord(my_x_pos)
    my_y_pos = _convert_cord(my_y_pos)
    print("hp =", hp)
    print('animation = ', animation)
    print('x_pos =', x_pos)
    print('y_pos =', y_pos)
    print('sub x_pos =',math.fabs(my_x_pos - x_pos))
    print('sub y_pos =',math.fabs(my_y_pos - y_pos))
#Вылет при атаке другого моба в режиме KILL_ID
#Вылет при открытии карты в режиме KILL_ID
#Не найдет функцию таргета в режиме KILL_ID
#Заблокировать бы смену цели в этом режиме
#Доп безопасность анализом расстояния до моба
#Блокировка определенных действий в игре во время фарма
#Попробовать настойщий id моба как катализатор (Какое-то время работает, а потом ошибка)
#Возможно мой адрес иногда изменяется (не замечено)
#Ошибка: сесть от бездействия, выбрать цель, не смочь атаковать из-за неактивность навыков, цель уходит и пропадает
pid = memory._get_pid()
game_handle = wg.FindWindow(None ,"Royal Quest")
ADDR = _pred_proc(pid)
BASE = memory.get_move_obj()
mob_bytes = _make_mob_bytes(ADDR, BASE, pid)


##get_mob_addr = 0x257995C0

my_id = ADDR['my_person_base'] + BASE['id']
my_target_addr = ADDR['my_person_base'] + BASE['target']
print(hex(my_target_addr))
##print(hex(ADDR['target_func']))
print(time.localtime())
##exit()
for i in range(10000000):
    mob_get_list = memory._getAddress_from_bytesEx(mob_bytes,pid, max_len = 15, buffer_size=100000)
##    print(mob_get_list)
    mob_addr = -1
    for i in mob_get_list:
        print(hex(i+0x14))
        if _check_id(i+0x14, BASE, ADDR, pid):
            mob_addr = i + 0x14
            break
    if mob_addr == -1:
        continue

    _kill_id(ADDR, BASE, mob_addr, pid)
    print('kill')
    _print_id(mob_addr, BASE, ADDR, pid)
    count = 0
    while _check_id(mob_addr, BASE, ADDR, pid):
        controler._press_key('1', game_handle)
        count += 1
##        if count > 100:
##            break
    _save_id(ADDR, BASE, pid)
    print("Кол-во ударов:", count)
    print('save')
    controler._press_key(wc.VK_SPACE, game_handle)
    controler._press_key(wc.VK_SPACE, game_handle)
    controler._press_key(wc.VK_SPACE, game_handle)

def main():
    pass

if __name__ == '__main__':
    main()