# -*- coding: utf-8 -*-

from PIL import ImageGrab, Image
import time
from window import _getWindow_box
import cv2
import numpy as np
import math
import win32gui as wg, win32ui as wu, win32con as wc
import ctypes

def get_np_array5(bitmap, num_bytes):
    # 0.079 / 1.145
    buffer = ctypes.cast(bitmap._FT_Bitmap.buffer, ctypes.POINTER(ctypes.c_ubyte * num_bytes))
    return np.frombuffer(buffer.contents, dtype=np.uint8)
"""
Вход - кортеж (x1,y1,x2,y2)
"""
def _get_screen(box, hwnd = None, dataBitMap = None):
    x1,y1,x2,y2 = box
##    img = ImageGrab.grab(bbox=(x1+8, y1+30, x2-8, y2))
##    return np.array(img)
    high = y2-y1
    weight = x2-x1
    if hwnd == None:
        hwnd = wg.FindWindow(None, 'Royal Quest')
    if dataBitMap == None:
        dataBitMap = wu.CreateBitmap()
    wDC = wg.GetWindowDC(hwnd)
    dcObj=wu.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap.CreateCompatibleBitmap(dcObj, weight, high)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(weight, high) , dcObj, (0,0), wc.SRCCOPY)


##    dataBitMap.SaveBitmapFile(cDC, "screen.bmp")
    img = np.fromstring(dataBitMap.GetBitmapBits(True), dtype='uint8')
    img.shape = (high,weight,4)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    wg.ReleaseDC(hwnd, wDC)
    wg.DeleteObject(dataBitMap.GetHandle())
    return img

"""
Разбивает картинку на окна x/y
на 490к точек ~ 0.075c
(И нигде не используется походу)
"""
def _img_to_pixel(img, x, y):
    x_full = len(img[0])
    y_full = len(img)
    x_less = math.ceil(x_full//x)
    y_less = math.ceil(y_full//y)
    ret_array = np.empty((y_less,x_less))
    for j in range(0,y_full,y):
        for i in range(0,x_full,x):
            sub = img[j:j+y,i:i+x].sum()//(x*y)
            ret_array[j//y,i//x] = sub
    return ret_array

"""
Возможно сделать более точно(но медленней) с автоподстройкой параметров step во время уточнения
Вход - изображение, кол-во окон, высота окна, длина окна, шаг уточнения в высоту, шаг уточнения в длину, порог вхождения, кол-во уточнений
"""

def _getBrightest_list(img, n, high, weight, y_step, x_step, threshold, n_update=1):
    br_list = np.zeros((n))
    xy_list = np.zeros((n,2))
    argmin = np.argmin(br_list)
    min_br = br_list[argmin]
    x_full = len(img[0])
    y_full = len(img)

# поиск оснвных непересекающихся светлых участков
    j = 0
    while j < y_full-high:
        i = 0
        while i < x_full-weight: #плавающее окно с шагом равным размеру окна
            br_now = img[j:j+high, i:i+weight].sum()//(high*weight) #Яркость получившегося окна
            if br_now > min_br and br_now > threshold:
                br_list[argmin] = br_now
                xy_list[argmin][0], xy_list[argmin][1] = i,j
                argmin = np.argmin(br_list)
                min_br = br_list[argmin]
                i += weight
            i += weight
##            cv2.imshow("ret",img[j:j+high, i:i+weight])
##            cv2.waitKey(0)
        j += high
##    return xy_list

#Уточнение расположение объекта шагами x_step и y_step
    for q in range(len(xy_list)):
        x_left = xy_list[q][0]
        y_left= xy_list[q][1]
        for k in range(n_update): #кол-во уточнений (Вызывается N*N_UPDATE раз)
            #Если картинка чуть ниже - светлее, возьмем её
            br_down = img[y_left+y_step:y_left+high+y_step, x_left:x_left+weight].sum()//(high*weight)
            if br_down > br_list[q]:
                xy_list[q][1] = y_left+y_step
##                br_list[q] = br_down
            #Если картинка чуть правее - светлее, возьмем её
            br_right = img[y_left:y_left+high, x_left+x_step:x_left+weight+x_step].sum()//(high*weight)
            if br_right > br_list[q]:
                xy_list[q][0] = x_left+x_step
##                br_list[q] = br_right
            #Если чуть выше - светлее, возьмем там
            br_up = img[y_left-y_step:y_left+high-y_step, x_left:x_left+weight].sum()//(high*weight)
            if br_up > br_list[q]:
                xy_list[q][1] = y_left-y_step
##                br_list[q] = br_up
            #Если левее - светлее, возьмем там
            br_left = img[y_left:y_left+high, x_left-x_step:x_left+weight-x_step].sum()//(high*weight)
            if br_left > br_list[q]:
                xy_list[q][0] = x_left-x_step
##                br_list[q] = br_left
##    print(br_list)
    return xy_list.astype(int)

def _paint_rectangles(img, list_start_point, x_size, y_size, color):
    list_start_point = list_start_point.astype(int)
    for i in list_start_point:
        cv2.rectangle(img, (i[0],i[1]), (i[0]+x_size, i[1]+y_size), color)
    return img

def _check_contour(contour):
    area = cv2.contourArea(contour)
    if area > 600 or area < 300:
        return False
    cont_len = cv2.arcLength(contour, 1)
    compact = area/math.pow(cont_len,2)
    if compact < 0.025:
        return False
    return True

def _pre_proc_img(img):
##    st = time.time()
    img = cv2.GaussianBlur(img, (7, 7), 2)
    bin_b = cv2.inRange(img[:,:,0],0,45)
##    cv2.imshow('r', bin_b)
##    exit()
    low_color = ( 0, 0)
    high_color =(95, 110)
    bin_full = cv2.inRange(img[:,:,1:], low_color, high_color)
##    cv2.imshow("bin_full", bin_full)
##    exit()
##    b,g,r = cv2.split(img)
##    hist_b = np.bincount(b.ravel(), minlength = 256)
##    hist_g = np.bincount(g.ravel(), minlength = 256)
##    hist_r = np.bincount(r.ravel(), minlength = 256)
##    max_arg_b = int( hist_b.argmin())
##    max_arg_g = int( hist_g.argmin())
##    max_arg_r = int( hist_r.argmin())
##    img[img[:,:,0]-max_arg_b < 32] = 255
##    img[img[:,:,1]-max_arg_g < 32] = 255
##    img[img[:,:,2]-max_arg_r < 32] = 255

##    cv2.imshow('', img)
##    cv2.waitKey(0)
##    print(time.time() - st)

##    low_color = (240,240,240)
##    high_color = (255,255,255)
##
##    bin_img = cv2.inRange(img, low_color, high_color)
##    bin_img = cv2.medianBlur(bin_img, 3)

##    cv2.imshow('',img)
##    cv2.waitKey(0)
##    print(img.shape)
#    bin_img = cv2.inRange(img, 50, 100)
    bin_img = cv2.dilate(bin_full, (3,3), 3)
##    bin_img = cv2.medianBlur(bin_full, 5)

    return bin_img

    cv2.imshow('', bin_img)
    exit()


"""
Вернет список координат центров контуров объектов
"""
def _get_contours_mid(img):
    ret_list = []

    im2, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    good_cont = []
    for i in range(len(contours)):
        if _check_contour(contours[i]):
            mid = contours[i].sum(axis=0)//len(contours[i])
            ret_list.append(mid[0])
##            good_cont.append(contours[i])
##    cv2.drawContours(img, good_cont , -1, (0,255,0), 2)
##    cv2.imshow('',img)
##    print(len(ret_list))
    return ret_list
##box =  _getWindow_box("Royal Quest")
##hwnd = wg.FindWindow(None, 'Royal Quest')
##st = time.time()
##img1 = _get_screen(box, hwnd=hwnd)
##img1 = _pre_proc_img(img1)
##xy_list = _get_contours_mid(img1)
##print(time.time() - st)
##img = _get_screen(box, hwnd=hwnd)
##for i in xy_list:
##    x_center = int(i[0])
##    y_center = int(i[1])
##    cv2.circle(img, (x_center, y_center), 25, (255,255,255))
##    cv2.imshow("",img)
##bin_img = cv2.inRange(img1, 70, 170)
##
##im2, contours, hierarchy = cv2.findContours(bin_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
####for i in contours:
####    peri = cv2.arcLength(i, True)
####    approx = cv2.approxPolyDP(i, .02 * peri, True)
##contours = [i for i in contours if math.fabs( cv2.contourArea(i))>300 and math.fabs( cv2.contourArea(i))< 1500]
##mid = contours[0].sum(axis=0)//len(contours[0])
##print(mid[0])
##
##cv2.drawContours(img1, contours, -1, (255,255,255), 2)

##cv2.imshow("", img1)
##time.sleep(.3)
##img2 = cv2.cvtColor(_get_screen(box), cv2.COLOR_BGR2GRAY)
##
##sub = cv2.subtract(img1, img2)
##xy_list = _getBrightest_list(sub, 5, 70, 50, 25, 15, 0)
##print(xy_list)
##sub = _paint_rectangles(sub,xy_list,50,70,(255,255,255))
##cv2.imshow("",sub)
