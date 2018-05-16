# -*- coding: utf-8 -*-

public_mob_set = set()
public_mob_list = []
farm_radius = 18 #Радиус в котором мы будем вырезать мобов, >0 и <X после которой игра крашнется
buffer_size = 200000 #Для перебора по всей памяти

FARM_FLAG = False
FIND_MOB_FLAG = False
HEAL_FLAG = False

HEAL_SETTING_OPENED = False

proc_name = 'rqmain.exe'
pid = None
game_handle = None
ADDR = {}
BASE = {}

HP_HEAL_1 = 0.25 # >0, <1
HP_HEAL_2 = 0.5  # >0, <1
HP_HEAL_1_KEY = '2'
HP_HEAL_2_KEY = '1'