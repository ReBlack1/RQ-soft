# -*- coding: utf-8 -*-

import memory
import math

pid = memory._get_pid()
ADDR = memory._getAddress_dict(pid=pid)
print(hex(ADDR['mob_num']))
target_func = b'\x8B\x80\xD4\x02\x00\x00\x85\xC0\x74\x04\x83\xC0\xEC\xC3\x33\xC0'
print(hex(memory._getAddress_from_bytes(target_func, pid=pid)))
my_target_func = b''
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

