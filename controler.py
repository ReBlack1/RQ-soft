# -*- coding: utf-8 -*-

from window import _getWindow_box

import win32gui as wg
import win32ui as wu
import win32con as wc
import win32api as wa

import time
"""
"""
def _press_key(char, game_handle = None):
    try: #возможность запихать как букву, так и тупо номер кнопки
        char = ord(char)
    except:
        pass
    if game_handle == None:
        game_handle = wg.FindWindow(None ,"Royal Quest")
    lparam_down = wa.MapVirtualKey(char, 0) * 65536 + 0x1
    lparam_up = lparam_down + 0xC0000000
    wa.PostMessage(game_handle, wc.WM_KEYDOWN, char, lparam_down)
    wa.PostMessage(game_handle, wc.WM_KEYUP, char, lparam_up)

def _rclick(x, y, game_handle = None):
    if game_handle == None:
        game_handle = wg.FindWindow(None ,"Royal Quest")
    wParam = wc.MK_RBUTTON
    lParam = lParam = y <<16 | x
    wa.PostMessage(game_handle, wc.WM_RBUTTONDOWN, wParam, lParam)
    time.sleep(0.003)
    wa.PostMessage(game_handle, wc.WM_RBUTTONUP, 0, lParam)

def _lclick(x, y, game_handle = None):
    if game_handle == None:
        game_handle = wg.FindWindow(None ,"Royal Quest")
    wParam = wc.MK_LBUTTON
    lParam = lParam = y <<16 | x

    wa.PostMessage(game_handle, wc.WM_LBUTTONDOWN, wParam, lParam)
    wa.PostMessage(game_handle, wc.WM_LBUTTONUP, 0, lParam)