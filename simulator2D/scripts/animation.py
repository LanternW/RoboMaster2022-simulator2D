# -*- coding: UTF-8 -*-
from constants import *
import gol
import math
from asistant import *

current_map = gol.get_value("current_map")
max_errdis = 0
es = 1 #地图跳转动画时用

def bkAnimationUpdate(): #背景切换动画
    bk_alpha = gol.get_value("bk_alpha")
    bk_tend = gol.get_value("bk_end")
    bk = gol.get_value("bk")
    if bk_alpha < 100:
        if bk_tend == 1:
            bk_main.set_alpha(bk_alpha)
            bk.blit(bk_main,(0,0))
        if bk_tend == 2:
            bk_hell.set_alpha(bk_alpha)
            bk.blit(bk_hell,(0,0))
        if bk_tend == 3:
            bk_end.set_alpha(bk_alpha)
            bk.blit(bk_end,(0,0))

        bk_alpha = bk_alpha + 1
        if bk_alpha > 70 and bk_alpha < 99:
            bk_alpha = 99
        gol.set_value("bk_alpha",bk_alpha)
        gol.set_value("bk",bk)

def controlsAnimationUpdate(): #控件动画

    detail_controls = gol.get_value("detail_controls")
    for item in detail_controls:
        item.animationUpdate()

    for item in controls:
        item.animationUpdate()

    for item in current_map.landmarks_manager.waypoint_buttons:
        item.animationUpdate()

def detailAnimationUpdate(): #细节窗口动画
    detail_end = gol.get_value("detail_end")
    detail_endx = gol.get_value("detail_endx")
    detail_endy = gol.get_value("detail_endy")
    detail_scale = gol.get_value("detail_scale")
    detail_posx = gol.get_value("detail_posx")
    detail_posy = gol.get_value("detail_posy")
    err = detail_end - detail_scale
    errx = detail_endx - detail_posx
    erry = detail_endy - detail_posy
    detail_velocity = err * 0.14 #比例控制器
    detail_velocityx = errx * 0.14 #比例控制器
    detail_velocityy = erry * 0.2 #比例控制器
    if (math.fabs(err) + math.fabs(errx) + math.fabs(erry)) < 0.05:
        detail_scale = detail_end
        #detail_posx = detail_endx
        #detail_posy = detail_endy
    else:
        detail_scale = detail_scale + detail_velocity
        detail_posx = detail_posx + detail_velocityx
        detail_posy = detail_posy + detail_velocityy
    
    gol.set_value("detail_scale",detail_scale)
    gol.set_value("detail_posx",detail_posx)
    gol.set_value("detail_posy",detail_posy)

def mapOffsetAnimationUpdate(): #地图跳转动画
    global max_errdis,es,current_map
    map_jump_sw = gol.get_value("map_jump_sw")
    if map_jump_sw == 1:
        end_offsetx = gol.get_value("end_offsetx")
        end_offsetz = gol.get_value("end_offsetz")
        end_scale = gol.get_value("end_scale")
        errx = end_offsetx - current_map.OFFSET_X
        errz = end_offsetz - current_map.OFFSET_Z
        errs = end_scale   - current_map.SCALE 

        
                             
        cx = errx * (-3000) #比例控制器
        cz = errz * (-3000)
        cs = errs * (2)

        #if errdis > max_errdis:
        #    max_errdis = errdis
        #    s = current_map.SCALE  #位移S型曲线插值
        #    if s < 10:
        #        es = 10
        #    else:
        #        es = 5
        #x = max_errdis - errdis
        #errs = es - current_map.SCALE
        #if math.fabs(errs) < 0.3:
        #    if es == 10:
        #        es = 5
        #zke = gol.get_value("zoom_kinetic_energy")
        #if es == 10:
        #    zke = zke + errs * 0.1
        #else:
        #    zke = zke + (-20-errs) * 0.05
        #print(errs,zke)
        #gol.set_value("zoom_kinetic_energy",zke)
        gol.set_value("drag_kinetic_energy_x",cx)
        gol.set_value("drag_kinetic_energy_z",cz)
        gol.set_value("zoom_kinetic_energy",cs)
        if math.fabs(errx) + math.fabs(errz) + math.fabs(errs)< 0.6:
            gol.set_value("map_jump_sw",0)
            gol.set_value("drag_kinetic_energy_x",0)
            gol.set_value("drag_kinetic_energy_z",0)
            current_map.OFFSET_X = end_offsetx
            current_map.OFFSET_Z = end_offsetz
            current_map.SCALE    = end_scale


def zoomAnimationUpdate():  #阻尼缩放动画
    global current_map
    zoom_kinetic_energy = gol.get_value("zoom_kinetic_energy")
    zoom_velocity = math.sqrt(2 * math.fabs(zoom_kinetic_energy)) #单位质量
    zoom_force = gol.get_value("zoom_f") * zoom_velocity
    if zoom_kinetic_energy < 0:
        zoom_velocity = -zoom_velocity
    if (math.fabs(zoom_velocity) < 0.2):
        zoom_velocity = 0
        zoom_kinetic_energy = 0
    else:
        current_map.SCALE = current_map.SCALE + (zoom_velocity  * 0.01) * (current_map.SCALE + 1)
        zoom_kinetic_energy = zoom_kinetic_energy - zoom_force * (zoom_velocity)  * 0.01
        if current_map.SCALE > 40:
            current_map.SCALE = 40
        if current_map.SCALE < 0.01:
            current_map.SCALE = 0.01
    
    gol.set_value("zoom_kinetic_energy",zoom_kinetic_energy)

def dragAnimationUpdate():  #阻尼拖拽动画
    global current_map
    drag_kinetic_energy_x = gol.get_value("drag_kinetic_energy_x")
    drag_kinetic_energy_z = gol.get_value("drag_kinetic_energy_z")
    drag_velocity_x = math.sqrt(2 * math.fabs(drag_kinetic_energy_x)) #单位质量
    drag_velocity_z = math.sqrt(2 * math.fabs(drag_kinetic_energy_z))

    drag_force_x = gol.get_value("drag_f") * drag_velocity_x #阻尼定义
    drag_force_z = gol.get_value("drag_f") * drag_velocity_z

    if drag_kinetic_energy_x < 0:
        drag_velocity_x = -drag_velocity_x
    if drag_kinetic_energy_z < 0:
        drag_velocity_z = -drag_velocity_z

    if (math.fabs(drag_velocity_x) + math.fabs(drag_velocity_z) < 1):
        drag_velocity_x = 0
        drag_velocity_z = 0
        drag_kinetic_energy_x = 0
        drag_kinetic_energy_z = 0
    
    else:
        current_map.OFFSET_X = current_map.OFFSET_X - (drag_velocity_x  * 0.01) 
        current_map.OFFSET_Z = current_map.OFFSET_Z - (drag_velocity_z  * 0.01) 
        drag_kinetic_energy_x = drag_kinetic_energy_x - drag_force_x * (drag_velocity_x)  * 0.01
        drag_kinetic_energy_z = drag_kinetic_energy_z - drag_force_z * (drag_velocity_z)  * 0.01

    gol.set_value("drag_kinetic_energy_x",drag_kinetic_energy_x)
    gol.set_value("drag_kinetic_energy_z",drag_kinetic_energy_z)

def lightAnimationUpdate(): #遮罩层动画
    ali = gol.get_value("map_mark")
    if(ali > 0):
        ali = ali - int(math.log(ali + 1))
    else:
        ali = 0
    gol.set_value("map_mark",ali)

def animationUpdate():
    global current_map
    current_map = gol.get_value("current_map")
    zoomAnimationUpdate()
    dragAnimationUpdate()
    lightAnimationUpdate()
    controlsAnimationUpdate()
    detailAnimationUpdate()
    bkAnimationUpdate()
    mapOffsetAnimationUpdate()

    
