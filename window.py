# -*- coding: utf-8 -*-

"""
TODO стиль упёртого барана, проверки и повторные открытия в случае не тех ответов, но с ограничениями на кол-во
"""

import win32api as wa, win32gui as wg, win32con as wc
import time
import os, psutil
import cv2

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

def _click(x,y):
    wa.mouse_event(wc.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    time.sleep(.01)
    wa.mouse_event(wc.MOUSEEVENTF_LEFTUP,x,y,0,0)

"""
Open game client of RQ and return windows handle
"""
def _start_RQ():
    launcher_handle = wg.FindWindow(None ,"RQLauncher")
    game_handle = wg.FindWindow(None ,"Royal Quest")
    if launcher_handle == 0 and game_handle == 0:
        launcher_handle = _start_launcher() #Реализовать 3 попытки
    if launcher_handle != 0:
        game_handle = _launcher_to_game(launcher_handle=launcher_handle)
    if game_handle != 0:
        return game_handle
"""

"""
def _waiting_load(name_window, wait_time = 3):
    n = 0
    wait_handle = wg.FindWindow(None, name_window)
    while n < wait_time*10 and wait_handle == 0:
            time.sleep(.1)
            n += 1
            wait_handle = wg.FindWindow(None, name_window)
    return wait_handle

def _is_run_proc(proc_name):
    for proc in psutil.process_iter():
        if proc.name() == proc_name:
            return True
    return False

"""
TODO - Замена пути и времени ожидания на config
TODO - Логи через log_config
Выход - Handle открытого лаунчера
Вход:
    Wait - кол-во секунд, которое мы ждем лаунчер
"""
def _start_launcher():
    os.system('taskkill /f /im rqlauncher.exe') #На случай если оно открыто фоновым процессом
    while _is_run_proc('rqlauncher.exe'):
        time.sleep(.025)
    os.startfile(r'D:\1C\rqlauncher')
    launcher_handle = _waiting_load("RQLauncher", wait_time = 15) # Ждем пока окно откроется
    return launcher_handle


"""
TODO - поиск координат кнопки игры через потомков к лаунчеру
TODO - проверки на вытащенность из трея и фокус на него
"""
def _launcher_to_game(launcher_handle = None):
    if launcher_handle == None:
        launcher_handle = wg.FindWindow(None, "RQLauncher")

    wg.ShowWindow(launcher_handle, wc.SW_SHOWNORMAL) #Вытащить его из трея
    time.sleep(.05)
    wg.SetWindowPos(launcher_handle, wc.HWND_TOPMOST, 0,0,1024,600, wc.SWP_NOSIZE) #Сделать верхним без права перекрывания
    time.sleep(.05)

    cord = wa.GetCursorPos() #Возьмем координаты курсора, чтоб потом вернуть его на место
    wa.SetCursorPos((800,600))
    time.sleep(.02)
    _click(800,600)
    time.sleep(.02)
    wa.SetCursorPos(cord)

    game_handle = _waiting_load("Royal Quest", wait_time = 20)
    return game_handle

def _getWindow_box(name_window):
    win_handle = wg.FindWindow(None, name_window)
    return wg.GetWindowRect(win_handle)

#Здесь можно сразу найти нужную кнопку, но потом
def all_ok(hwnd, param):
    print(hwnd)
    print(convert_base(hwnd, to_base = 16))
    print(wg.GetWindowRect(hwnd))
    return True
##time.sleep(25)
##
##game_button = wg.EnumChildWindows(handle, all_ok, None)
##print(game_button)
