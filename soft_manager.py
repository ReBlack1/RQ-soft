# -*- coding: utf-8 -*-

import memory
import math
import controler
import datetime, time
import win32gui as wg, win32con as wc
import config
import threading

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
#Мб сюда и формирование конфиг запихать?
def _pred_proc():
    config.ADDR = memory._getAddress_dict()

    addr_target_func = memory._make_my_target_func() #подготовка функции таргетирования
    if addr_target_func != None:
        config.ADDR['target_func'] = addr_target_func
    return 1

def _kill_id(id):
    target_func_addr = config.ADDR['target_func'] + 0xA #Cмещение до цели таргета
    my_target_addr = config.ADDR['my_person_base'] + config.BASE['target']
    mov = b'\xB8'
    my_id = config.ADDR['my_person_base'] + config.BASE['id']
##    print(hex(memory._getAddress([0x7CBFD4, 0x18, 0xB4494, 0x0],pid=pid)))
##    print(hex(my_id))
    if type(id) == int:
        base = id - 0x14
        base = base.to_bytes(4, byteorder='little')
    new_tagret = mov + base
##    print(base)
    memory._write_to_address(my_target_addr, b'\x00\x00\x00\x00')
    #Могут быть проблемы с агрящимся на меня мобом
    memory._write_to_address(target_func_addr, new_tagret, 5)
    memory._write_to_address(my_target_addr, my_id)
    return True

def _save_id():
    old_target = b'\x83\xC0\xEC\x90\x90'
    target_func_addr = config.ADDR['target_func'] + 0xA #Смещение до места для моба
    my_target_addr = config.ADDR['my_person_base'] + config.BASE['target']
    my_id = config.ADDR['my_person_base'] + config.BASE['id']
    memory._write_to_address(my_target_addr, b'\x00\x00\x00\x00')
##    memory._write_to_address(my_target_addr, my_id, pid=pid)
    memory._write_to_address(target_func_addr, old_target, 5)
    memory._write_to_address(my_target_addr, b'\x00\x00\x00\x00')

#Проверка моб ли это через хп и анимацию
#TODO проверка на расстояние
def _check_id(id):
    base = id - 0x14
    hp = memory._getValue_In_Address(base + config.BASE['hp'])
    animation = memory._getValue_In_Address(base + config.BASE['anim'])

    #Поиск и конвертирование своих и чужих координат для сравнения
    x_pos = memory._getValue_In_Address(base + config.BASE['x_pos'])
    y_pos = memory._getValue_In_Address(base + config.BASE['y_pos'])
    x_pos = _convert_cord(x_pos)
    y_pos = _convert_cord(y_pos)
    my_x_pos = memory._getValue_In_Address(config.ADDR['my_person_base'] + config.BASE['x_pos'])
    my_y_pos = memory._getValue_In_Address(config.ADDR['my_person_base'] + config.BASE['y_pos'])
    my_x_pos = _convert_cord(my_x_pos)
    my_y_pos = _convert_cord(my_y_pos)

    mob = memory._getValue_In_Address(base, buffer_size = 2)
    if mob != 15228 and mob != None:
        return False
    if hp == None or animation == None or mob == None:
        return False
    hp_flag = hp < 300 and hp > 0 #> 0 and hp < 1000000
    anim_flag = animation > 0 and animation < 6
    mob_flag = mob == 15228 #Первые 2 байта каждого моба
    pos_flag = math.pow(x_pos - my_x_pos, 2) + math.pow(y_pos - my_y_pos, 2) < math.pow(config.farm_radius, 2) #Формула окружности

    if hp_flag and anim_flag and mob_flag and pos_flag:
        return True
    return False

def _make_mob_bytes():
    a = b'\x7C\x3B'
    b = memory._getValue_In_Address(config.ADDR['my_person_base'] + 0x2, buffer_size = 2) #вторые 2 байта моба совпадают с моими
    b = int.to_bytes(b, 2, byteorder='little')
    return a + b

def _print_id(id):
    base = id - 0x14
    hp = memory._getValue_In_Address(base + config.BASE['hp'])
    animation = memory._getValue_In_Address(base + config.BASE['anim'])

    #Поиск и конвертирование своих и чужих координат для сравнения
    x_pos = memory._getValue_In_Address(base + config.BASE['x_pos'])
    y_pos = memory._getValue_In_Address(base + config.BASE['y_pos'])
    x_pos = _convert_cord(x_pos)
    y_pos = _convert_cord(y_pos)
    my_x_pos = memory._getValue_In_Address(config.ADDR['my_person_base'] + config.BASE['x_pos'])
    my_y_pos = memory._getValue_In_Address(config.ADDR['my_person_base'] + config.BASE['y_pos'])
    my_x_pos = _convert_cord(my_x_pos)
    my_y_pos = _convert_cord(my_y_pos)
    print("hp =", hp)
    print('animation = ', animation)
    print('x_pos =', x_pos)
    print('y_pos =', y_pos)
    print('sub x_pos =',math.fabs(my_x_pos - x_pos))
    print('sub y_pos =',math.fabs(my_y_pos - y_pos))

def _farm_mob(start_bot_time=None):
    count_check = 0
    while config.FARM_FLAG and config.FIND_MOB_FLAG:

        mob_addr = None
        while mob_addr == None:
            st = time.time()
            print('check', len(config.public_mob_list))
            for i in config.public_mob_list:
                if _check_id(i + 0x14):
                    mob_addr = i + 0x14
                    break
            print(time.time() - st)

        #ID Для убийства найден!
        _kill_id(mob_addr)
        print('kill')
        count = 0
        while _check_id(mob_addr):
            time.sleep(.2)
            controler._press_key('1', config.game_handle)
            count += 1
            if count > 10:
                controler._press_key('2', config.game_handle)
            if count > 5000:
                _save_id()
                print("Вероятен вылет из игры")
                _print_id(mob_add)
                print('Bot was started in', start_bot_time)
                print('Bot was crashed if', time.localtime())
                config.FARM_FLAG = False
                exit()
        _save_id()
        print("Кол-во ударов:", count)
        print('save')
        controler._press_key(wc.VK_SPACE, config.game_handle)
        controler._press_key(wc.VK_SPACE, config.game_handle)
        controler._press_key(wc.VK_SPACE, config.game_handle)
        #Выход из функции только здесь, после сохранения


#Вылет при атаке другого моба в режиме KILL_ID
#Вылет при открытии карты в режиме KILL_ID, а мб и в save режиме
#Вылет от смерти
#Не найдет функцию таргета в режиме KILL_ID
#Заблокировать бы смену цели в этом режиме
#Блокировка определенных действий в игре во время фарма
#(Не проверено) Ошибка: сесть от бездействия, выбрать цель, не смочь атаковать из-за неактивность навыков, цель уходит и пропадает
#Автоматический предпроцессинг по флагу, нахер его отдельно вызывать, криво как-то выглядит
def main():
    print("started")
    config.pid = memory._get_pid()

    config.game_handle = wg.FindWindow(None ,"Royal Quest")
    ss = _pred_proc()
##    exit()
    config.BASE = memory.get_move_obj()
    mob_bytes = _make_mob_bytes()
    print(mob_bytes)
    my_id = config.ADDR['my_person_base'] + config.BASE['id']
    my_target_addr = config.ADDR['my_person_base'] + config.BASE['target']
    print(hex(my_target_addr))
    start_bot_time = time.localtime()
    config.FARM_FLAG = True
    config.FIND_MOB_FLAG = True
    thread_find = threading.Thread(target=memory._find_mobs, args=(mob_bytes,)).start()
    thread_farm = threading.Thread(target=_farm_mob, args=(start_bot_time,)).start()
    thread_farm.join()
    thread_find.join()

if __name__ == '__main__':
    main()