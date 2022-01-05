# -*- coding: UTF-8 -*-
from constants import *
import math
import gol

# math functions

def sign(num):
    if num >= 0:
        return 1
    else:
        return -1

def abs(num):
    if num < 0:
        return -num
    return num



def colorMerge(color1 , color2,k): #颜色线性插值器
    (r1,g1,b1,a1) = color1
    (r2,g2,b2,a2) = color2
    r = r1 + k * (r2 - r1)
    g = g1 + k * (g2 - g1)
    b = b1 + k * (b2 - b1)
    a = 0.5 * (a1 + a2)
    return (r,g,b,a)
    
def norm2(num1,num2):
    return math.sqrt(num1 * num1 + num2 * num2)

def distance(point1,point2):
    dx = point1[0] - point2[0]
    dy = point1[1] - point2[1]
    return math.sqrt(dx*dx + dy*dy)


#判断POSC是否在POS1和POS2组成的线段上
def isOnLineSeg(pos1, pos2, posc):
    crossTime = (posc[0] - pos1[0])*(pos2[1] - posc[1]) - (posc[1] - pos1[1])*(pos2[0] - posc[0])
    normC1 = distance(posc, pos1)
    normC2 = distance(posc, pos2)
    dotC12 = (pos1[0] - posc[0]) * (pos2[0] - posc[0]) + (pos1[1]-posc[1])*(pos2[1]-posc[1])
    cos_t  = dotC12 / (normC1 * normC2)

    if (abs(crossTime) < 5 and cos_t < 0):
        #return True, abs(crossTime), cos_t
        return True
    else:
        #return False, abs(crossTime), cos_t 
        return False

def inWhichArea(posx,posy):

    in_detail = gol.get_value("detail_menu")
    if in_detail != 0:
        if (posx > 50 and posx < SCREEN_WIDTH - 50) and (posy > 50 and posy < SCREEN_HEIGHT - 50):
            return IN_DETAIL

    if (posx > 0 and posx < MAP_WIDTH) and (posy > 0 and posy < SCREEN_HEIGHT):
        return IN_MAP
    elif (posx > MAP_WIDTH and posx < SCREEN_WIDTH) and (posy > 0 and posy < SCREEN_HEIGHT):
        return IN_SWITCH
    
    
    return 0

def isInMap(posx,posy ,inflate = 0):
    if (posx > -inflate and posx < (MAP_WIDTH + inflate) ) and (posy > -inflate and posy < (SCREEN_HEIGHT+inflate) ):
        return True
    return False

def lalo2worldXZ(latitude, longitude):
    #纬度优先线性化
    z_la = gol.get_value("base_latitude")
    z_lo = gol.get_value("base_longitude")

    dx = (longitude - z_lo) * 111321.3889 * math.cos( z_la * 6.283185307 / 360)
    dz = -(latitude - z_la) * 111321.3889
    
    return(dx, dz)

def worldXZ2lalo(x,z):
    z_la = gol.get_value("base_latitude")
    z_lo = gol.get_value("base_longitude")


    dlo = x * 0.000008982999673 / math.cos( z_la * 6.283185307 / 360 )
    dla = -z * 0.000008982999673

    return (z_la + dla , z_lo + dlo) 
