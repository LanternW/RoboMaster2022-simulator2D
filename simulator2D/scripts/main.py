#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pygame
import sys
pygame.init()
pygame.display.set_caption('RM simulator2D')

import gol
gol.init()

from constants import *
from asistant import *
from animation import *
from pygame.locals import * # pygame 
import rospy
from toros import *
import control


is_game_paused = True
time_left = 180000 #micro-second

tick = 0
velocity_x = 0
velocity_z = 0
mouse_posx = -100000
mouse_posy = -100000
mosue_posx_old = -100000
mouse_posy_old = -100000

left_button_down = 0
right_button_down = 0
measure_fixed_x = 0
measure_fixed_z = 0

id = 1
detail_id = 0

id_detail = 0
bk = bk_main
map_choice_id = 1


detail_controls = []

current_map = gol.get_value("current_map")

initRosPart()

#初始化
gol.set_value("map_mark",255)



def buttonsHandler(id): #按钮响应
    #global route_pos_start,route_pos_end,route_switch
    global time_left

    if id == 0: #shoot
       current_map.shoot(1, 2000)
       current_map.shoot(2, 2000)
       current_map.shoot(3, 2000)
       current_map.shoot(4, 2000)
       
    
    elif id == 1: # pause and continue
        is_game_paused = gol.get_value("is_game_paused")
        if is_game_paused == True:
            controls[1].setIcon(str("src/simulator2D/scripts/imgs/" + "btn_pause.png"))
        else:
            controls[1].setIcon(str("src/simulator2D/scripts/imgs/" + "btn_next.png"))
        gol.set_value("is_game_paused", not is_game_paused)
    
    elif id == 10: # reset
        if gol.get_value("is_game_paused") == True:
            current_map.reset()
            #controls[1].setIcon(str("src/simulator2D/scripts/imgs/" + "btn_next.png"))
            gol.set_value("is_game_paused", 1)
            gol.set_value("is_game_over",0)
            time_left = 180000

    elif id == 2: #set Appropriate perspective
        gol.set_value("end_offsetx",-120)
        gol.set_value("end_offsetz",0)
        gol.set_value("end_scale",4)
        gol.set_value("map_jump_sw",1) #地图跳转开关

    elif id == 3: #create wp
        iscw = not gol.get_value("is_creating_wp")
        gol.set_value("is_creating_wp",iscw)
    
    elif id == 4: #create wpd
        drone_pos = (current_map.now_pos_x, current_map.now_pos_z)
        current_map.addWayPoint(drone_pos,current_map.landmarks_manager.getValidWpId())

    elif id == 5: #remove wp
        isrw = not gol.get_value("is_removing_wp")
        gol.set_value("is_removing_wp",isrw)

    elif id == 6: #clear wp
       current_map.landmarks_manager.clearWp()


    
    elif id == 7: #up
        current_map.landmarks_manager.current_page -= 1
        if current_map.landmarks_manager.current_page < 1:
            current_map.landmarks_manager.current_page = 1
        current_map.landmarks_manager.WpPageUpdate(current_map.landmarks_manager.current_page)

    elif id == 8: #down
        current_map.landmarks_manager.current_page += 1
        if current_map.landmarks_manager.current_page > current_map.landmarks_manager.total_pages:
            current_map.landmarks_manager.current_page -= 1
        current_map.landmarks_manager.WpPageUpdate(current_map.landmarks_manager.current_page)






def waypButtonsHandler(id,type_):
    #waypoints button handler
    if gol.get_value("is_removing_wp") == 0:
        wp = current_map.landmarks_manager.getWpById(id)
        if type_ == 1: #left button
            gol.set_value("end_offsetx",wp.posx)
            gol.set_value("end_offsetz",wp.posz)
            gol.set_value("end_scale", current_map.SCALE)
            gol.set_value("map_jump_sw",1)

        elif type_ == 2: #right_button
            gol.set_value("chosed_wp",wp.id)

    else:
        if type_ == 1: #left button
            wp = current_map.landmarks_manager.getWpById(id)
            gol.set_value("end_offsetx",wp.posx)
            gol.set_value("end_offsetz",wp.posz)
            gol.set_value("end_scale", current_map.SCALE)
            gol.set_value("map_jump_sw",1)
        elif type_ == 2: #right_button
            current_map.landmarks_manager.removeWayPoint(id)
            gol.set_value("is_removing_wp",0)
            if gol.get_value("chosed_wp") == id:
                gol.set_value("chosed_wp",0)

        


def renderControls(): #控件绘制
    
    SWITCH_SCREEN.fill((50,50,50,200))

    for item in controls:
        item.render(SWITCH_SCREEN)

    for item in current_map.landmarks_manager.waypoint_buttons:
        item.render(SWITCH_SCREEN)

    #for item in expanders:
    #   item.render(SWITCH_SCREEN)

    BASE_SCREEN.blit(SWITCH_SCREEN,(MAP_WIDTH,0))
def detailLayerRender(): #细节窗口绘制

    global detail_controls
    scale = gol.get_value("detail_scale")
    position_x = gol.get_value("detail_posx")
    position_y = gol.get_value("detail_posy")
    position = (position_x,position_y)

    detail_controls = gol.get_value("detail_controls")

    new_size = (int((SCREEN_WIDTH - 100) * scale)  ,int((SCREEN_HEIGHT - 100) * scale))
    if (new_size[0] + new_size[1] > 20):
        DETAIL_SCREEN.fill((128,128,128,200))
        if id_detail == 7:
            for item in detail_controls:
                item.render(DETAIL_SCREEN,(0,0,0,255))

        A = pygame.transform.scale(DETAIL_SCREEN,new_size)
        BASE_SCREEN.blit(A,position)

refresh_flag = False
def debugRender(): #debug信息绘制
    global right_button_down,measure_fixed_z,measure_fixed_x,mouse_posx,mouse_posy, time_left,refresh_flag
    mouse_world_pos = current_map.screenXY2worldXZ(mouse_posx,mouse_posy)

    string = str("x:  %.2fcm \t" % (mouse_world_pos[0]))
    MAP_SCREEN.blit(gol.font_Basis.render(string, True, C_LIGHTBLUE), (20 , 10))

    string = str("z:  %.2fcm \t" % (mouse_world_pos[1]))
    MAP_SCREEN.blit(gol.font_Basis.render(string, True, C_LIGHTBLUE), (20 , 30))
    

    pygame.draw.rect(MAP_SCREEN,(100,100,100,140),((350,30),(1000,5)),1,border_radius=5)
    pygame.draw.rect(MAP_SCREEN,(100,100,100,140),((350,30),(500,5)),0,border_radius=5)

    unit50 = current_map.SCALE * 80 
    MAP_SCREEN.blit(gol.font_Scribe.render(str("0"), True, C_LIGHTBLUE), (350 , 10))
    string = str("%.2f"%unit50)
    MAP_SCREEN.blit(gol.font_Scribe.render(string, True, C_LIGHTBLUE), (850 , 10))
    string = str("%.2f cm" % (unit50 * 2))
    MAP_SCREEN.blit(gol.font_Scribe.render(string, True, C_LIGHTBLUE), (1350 , 10))
    pygame.draw.rect(DEBUG_SCREEN,(0,0,0,0),((0,0) ,SCREEN_SIZE),0)

    if right_button_down == 1:
        measure_point_w = (measure_fixed_x,measure_fixed_z)
        mouse_point_w   =  current_map.screenXY2worldXZ(mouse_posx,mouse_posy)
        (x1,y1) = current_map.worldXZ2screenXY(measure_fixed_x,measure_fixed_z)
        (x2,y2) = (mouse_posx,mouse_posy)
        point1 = (x1,y1)
        point2 = (x2,y2)
        point3 = (0.5*(x1+x2) + 25 , 0.5*(y1+y2) )
        dis12 = distance(measure_point_w,mouse_point_w)
        str_dis = str(" %.2fcm " % (dis12))
        pygame.draw.line(MAP_SCREEN,C_LIGHTYELLOW,point1,point2,5)
        MAP_SCREEN.blit(gol.font_Basis.render(str_dis, True, C_YELLOW), point3)



    #timer

    time_left_second = int(time_left / 1000)
    if time_left < 0:
        time_left = -1
        time_left_second = 0
        gol.set_value("is_game_over",1)
        gol.set_value("is_game_paused",1)
    minute = int(time_left_second / 60)
    second = time_left_second - minute*60
    if second != 0:
        refresh_flag = True
    elif second == 0 and refresh_flag == True:
        refresh_flag = False
        current_map.functionarea_manager.refreshFunctionArea()

    color  = (200,150,50,100)
    if gol.get_value("is_game_paused") == False:
        color = C_LIGHTGREEN
    DEBUG_SCREEN.blit(gol.font_Basis_h.render(str(minute), True, color), (MAP_WIDTH+135 , 145))
    DEBUG_SCREEN.blit(gol.font_Basis_h.render(str(":"), True, color), (MAP_WIDTH+165 , 140))
    DEBUG_SCREEN.blit(gol.font_Basis_h.render(str(second).zfill(2), True, color), (MAP_WIDTH+185 , 145))

    #DEBUG_SCREEN.blit(gol.font_Basis.render(str("way points:"), True, (150,255,150,235)), (MAP_WIDTH+55 , 600))
    now_page = current_map.landmarks_manager.current_page
    total_page = current_map.landmarks_manager.total_pages
    str_page = str(now_page) + " / " + str(total_page)
    DEBUG_SCREEN.blit(gol.font_Basis.render(str_page, True, (150,255,150,235)), (MAP_WIDTH+305 , 840))
    if gol.get_value("is_creating_wp") == 1:

        now_mpos = (mouse_posx,mouse_posy)
        btn_pos  = (255 + MAP_WIDTH + 15 , 685 + 15)
        pygame.draw.line(DEBUG_SCREEN,(155,155,255,100),btn_pos,now_mpos,5)
        pygame.draw.rect(DEBUG_SCREEN,(150,150,255,255),((mouse_posx,mouse_posy),(10,10)),0)
        wpnm = "w" + str(current_map.landmarks_manager.getValidWpId())
        DEBUG_SCREEN.blit(gol.font_Basis.render(wpnm, True, C_LIGHTGREEN), (mouse_posx+15,mouse_posy-5))

    if gol.get_value("is_removing_wp") == 1:

        now_mpos = (mouse_posx,mouse_posy)
        btn_pos  = (255 + MAP_WIDTH + 15,730 + 15)
        pygame.draw.line(DEBUG_SCREEN,(255,70,70,140),btn_pos,now_mpos,5)
    

    # health and bullet_count and debuff
    # DEBUG_SCREEN.blit(gol.font_Basis.render(str("states:"), True, (150,255,150,235)), (MAP_WIDTH+55 , 200))

    postemp_y = 240
    for tank in current_map.tank_manager.tanks:
        color = tank.color
        DEBUG_SCREEN.blit(gol.font_Basis.render(str(tank.id), True, tank.color), (MAP_WIDTH+55 , postemp_y))
        health_bar_length = 0.1 * tank.health
        pygame.draw.rect( DEBUG_SCREEN, color, ( (MAP_WIDTH + 85 , postemp_y), (health_bar_length, 20) ),0)
        DEBUG_SCREEN.blit(gol.font_Basis.render(str(tank.health), True, (20,150,20,200)), (MAP_WIDTH+305 , postemp_y))
        DEBUG_SCREEN.blit(gol.font_Basis.render(str(tank.bullet_count), True, (200,150,50,100)), (MAP_WIDTH+385 , postemp_y))
        DEBUG_SCREEN.blit(gol.font_Basis.render(str(tank.heat), True, C_RED), (MAP_WIDTH+305 , postemp_y+20))

        if tank.noshooting == True:
            pygame.draw.circle(DEBUG_SCREEN , (200,150,50,100), (MAP_WIDTH+105 , postemp_y+40) , 14 ,3)
            DEBUG_SCREEN.blit(gol.font_Basis.render(str(round(tank.noshooting_time,2)), True, (200,150,50,100)), (MAP_WIDTH+135 , postemp_y+30))
        if tank.nomoving == True:
            pygame.draw.rect(DEBUG_SCREEN , (200,150,50,100),((MAP_WIDTH+205 , postemp_y+30) ,(20,20)),4)
            DEBUG_SCREEN.blit(gol.font_Basis.render(str(round(tank.nomoving_time,2)), True, (200,150,50,100)), (MAP_WIDTH+235 , postemp_y+30))

        postemp_y = postemp_y + 70

    #score
    DEBUG_SCREEN.blit(gol.font_Basis_m.render(str(current_map.red_score), True, C_RED), (MAP_WIDTH+85 , 600))
    DEBUG_SCREEN.blit(gol.font_Basis_m.render(str(" VS "), True, (200,150,50,100)), (MAP_WIDTH+165 , 600))
    DEBUG_SCREEN.blit(gol.font_Basis_m.render(str(current_map.blue_score), True, C_BLUE), (MAP_WIDTH+255 , 600))


last_time = rospy.Time.now().to_sec()
def render(): #绘 制

    global last_time, time_left
    time = rospy.Time.now().to_sec()
    dt   = time - last_time
    last_time = time

    if gol.get_value("is_game_paused") == False:
        current_map.update(dt)
        time_left = time_left - 1000*dt
    current_map.renderBase()
    current_map.renderGrid()
    current_map.renderLDMKS()
    current_map.renderMarkRects()
    current_map.renderFunctionArea()
    current_map.renderObstacles()
    current_map.renderTanks()
    current_map.renderBullets()
    current_map.renderAxis()

    renderControls()
    debugRender()

    #MAP_SCREEN = pygame.transform.rotate(MAP_SCREEN,20)
    BASE_SCREEN.blit(MAP_SCREEN, (0,0))
    #BASE_SCREEN.blit(MAP_MARK,(0,0))
    #BASE_SCREEN.blit(DETAIL_SCREEN,(SCREEN_WIDTH - MAP_WIDTH,300))

    BASE_SCREEN.blit(DEBUG_SCREEN,(0,0))
    #BASE_SCREEN.blit(MAP_FX,(0,0),special_flags=BLEND_RGBA_MULT)

    #BASE_SCREEN.blit(gol.font_Scribe.render(str("LanGNSS v0.2.2"), True, (255, 255, 255,128)), (SCREEN_WIDTH - 200 , SCREEN_HEIGHT - 25))
    pass

def mouseMoveHandler(x,y,mouse_area): #鼠标移动事件处理
    global mouse_posx,mouse_posy,mosue_posx_old,mouse_posy_old,velocity_x,velocity_z,left_button_down
    mouse_posx_old = mouse_posx
    mouse_posy_old = mouse_posy
    mouse_posx = x
    mouse_posy = y
    if left_button_down == 1:
        dx = mouse_posx - mouse_posx_old
        dz = mouse_posy - mouse_posy_old
        current_map.OFFSET_X = current_map.OFFSET_X - (dx * 16 * current_map.SCALE / 100 )
        current_map.OFFSET_Z = current_map.OFFSET_Z - (dz * 16 * current_map.SCALE / 100 )
        velocity_x = dx * 5 * current_map.SCALE
        velocity_z = dz * 5 * current_map.SCALE
    
    if mouse_area == IN_MAP:

        #mouse_world_pos = current_map.screenXY2worldXZ(mouse_posx,mouse_posy)
        #print(current_map.tank_manager.tanks[0].isPointIn(mouse_world_pos))
    
        if gol.get_value("is_removing_wp") == 1:
            highlight_wp = current_map.scanWpOnMap(mouse_posx,mouse_posy)
            gol.set_value("highlight_wp",highlight_wp)

    if mouse_area == IN_SWITCH:

        for item in controls:
            item.onPassedBy(x - MAP_WIDTH,y)
        
        gol.set_value("highlight_wp",0)
        for item in current_map.landmarks_manager.waypoint_buttons:
            item.onPassedBy(x - MAP_WIDTH,y)
    
    if mouse_area == IN_DETAIL:

        detail_controls = gol.get_value("detail_controls")
        for item in detail_controls:
            item.onPassedBy(x - 50,y - 50)

def expandHandler(id,selected): #展开事件处理
    global id_detail
    if selected == True:
        if id == 7:
            gol.set_value("detail_end",1)
            gol.set_value("detail_endx",50)
            gol.set_value("detail_endy",50)
            id_detail = 7
            gol.set_value("detail_menu",1)

            detail_controls = gol.get_value("detail_controls")
            oringinal_x = 20
            oringinal_y = 15
            for item in current_map.landmarks_manager.landmarks:

                string = str("%s (x: %d , z: %d)" % (item.name,item.posx ,item.posz))
                ldmk_button = control.DetailSwitch((400,30),(oringinal_x,oringinal_y),item.color,string,item.id)
                detail_controls.append(ldmk_button)

                oringinal_y = oringinal_y + 30
                if oringinal_y > SCREEN_HEIGHT - 125:
                    oringinal_x = oringinal_x + 410
                    oringinal_y = 15

            control_btn_next = control.Button((32,32),(890,30),(0,0,0,0),"操作按钮之下一页",21,"btn_next.png")
            control_btn_last = control.Button((32,32),(890,70),(0,0,0,0),"操作按钮之上一页",22,"btn_last.png")
            control_btn_goto = control.Button((32,32),(890,140),(0,0,0,0),"操作按钮之跳转",23,"btn_goto.png")
            detail_controls.append(control_btn_next)
            detail_controls.append(control_btn_last)
            detail_controls.append(control_btn_goto)
            gol.set_value("detail_controls",detail_controls)

        if id == 8:
            gol.set_value("detail_end",1)
            gol.set_value("detail_endx",50)
            gol.set_value("detail_endy",50)
            id_detail = 8
            gol.set_value("detail_menu",2)
        
        if id == 9:
            gol.set_value("detail_end",1)
            gol.set_value("detail_endx",50)
            gol.set_value("detail_endy",50)
            id_detail = 9
            gol.set_value("detail_menu",3)

    if selected == False:
        closeDetail(id)
    
def mouseClickHandler(x,y,button,mouse_area): #鼠标单击事件处理
    global old_id,id,mouse_posx,mouse_posy,right_button_down,left_button_down,current_map,measure_fixed_x,measure_fixed_z
    if button == 5: #上滚轮
        if mouse_area == IN_MAP:
            zoom_kinetic_energy = gol.get_value("zoom_kinetic_energy") + 1  #假设物体“缩放”的质量为1 ，每次滚动给予1焦耳动能
            gol.set_value("zoom_kinetic_energy",zoom_kinetic_energy)
    if event.button == 4: #下滚轮
        if mouse_area == IN_MAP:
            zoom_kinetic_energy = gol.get_value("zoom_kinetic_energy") - 1
            gol.set_value("zoom_kinetic_energy",zoom_kinetic_energy)
                    

    if event.button == 1: #左键
        if mouse_area == IN_MAP:   # 地图界面单击信息处理
            left_button_down = 1
            velocity_x = 0
            velocity_z = 0
            gol.set_value("drag_kinetic_energy_x",0) #按下键拖拽时立即消除滑动动能
            gol.set_value("drag_kinetic_energy_z",0)
        if mouse_area == IN_SWITCH: # 主界面单击信息处理
            old_id = id
            for item in controls:
                if item.isPassedBy(x-MAP_WIDTH,y) == True:
                    id = item.onClick()
                    buttonsHandler(id)

            for item in current_map.landmarks_manager.waypoint_buttons:
                if item.isPassedBy(x-MAP_WIDTH,y) == True:
                    id = item.onClick()
                    waypButtonsHandler(id,1)
                    break
    
    if event.button == 3: #right button
        if mouse_area == IN_MAP:
            if gol.get_value("is_creating_wp") == 1:
                (wpx,wpz) = current_map.screenXY2worldXZ(mouse_posx,mouse_posy)
                current_map.addWayPoint((wpx,wpz),current_map.landmarks_manager.getValidWpId())
                gol.set_value("is_creating_wp",0)
            
            elif gol.get_value("is_removing_wp") == 1:
                hwp = gol.get_value("highlight_wp") 
                if hwp != 0:
                    current_map.landmarks_manager.removeWayPoint(hwp)
                    gol.set_value("is_removing_wp",0)
                    gol.set_value("highlight_wp",0)
                else:
                    right_button_down = 1
                    (measure_fixed_x,measure_fixed_z) = current_map.screenXY2worldXZ(mouse_posx, mouse_posy)

            else:
                right_button_down = 1
                (measure_fixed_x,measure_fixed_z) = current_map.screenXY2worldXZ(mouse_posx, mouse_posy)
        
        if mouse_area == IN_SWITCH: # 主界面单击信息处理

            for item in current_map.landmarks_manager.waypoint_buttons:
                if item.isPassedBy(x - MAP_WIDTH,y) == True:
                    id = item.onClick()
                    waypButtonsHandler(id,2)
                    break
            

while True:  # 死循环确保窗口一直显示

    tick = tick + 1
    for event in pygame.event.get():  # 遍历所有事件
        mouse_area = inWhichArea(mouse_posx,mouse_posy)
        if event.type == pygame.QUIT:  # 如果单击关闭窗口，则退出
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
                mouseClickHandler(mouse_posx,mouse_posy,event.button,mouse_area)

        if event.type == pygame.MOUSEMOTION:
                mouseMoveHandler(event.pos[0],event.pos[1],mouse_area)
            

        if event.type == pygame.MOUSEBUTTONUP:
            if left_button_down == 1:
                gol.set_value("drag_kinetic_energy_x", 0.5 * velocity_x * velocity_x * sign(velocity_x) )
                gol.set_value("drag_kinetic_energy_z", 0.5 * velocity_z * velocity_z * sign(velocity_z) )
            
            left_button_down = 0
            tick = 0
            if event.button == 3:
                right_button_down = 0

        if event.type == pygame.KEYDOWN:  #目前没什么用，占个位
            if event.key == K_w:
                current_map.tank_manager.setTankVelocity(1, (0,-100), 0.4, 1)    
                pass       
            elif event.key == K_s:
                current_map.tank_manager.setTankVelocity(1, (0,100), 0.4, 1) 
                pass       
            elif event.key == K_a:
                current_map.tank_manager.setTankVelocity(1, (-100,0), 0.4, 1)
                pass        
            elif event.key == K_d:         
                current_map.tank_manager.setTankVelocity(1, (100,0), 0.4, 1)       
                pass 
        if event.type == pygame.KEYUP:
            a_flag = 0
            cx_flag = 0
            pause_flag = 0
    
    pygame.display.update()
    pygame.time.wait(2)
    pygame.draw.rect(BASE_SCREEN,C_BLACK,((0,0) ,MAP_SCREEN_SIZE),0)
    pygame.draw.rect(BASE_SCREEN,C_BLACK,((MAP_WIDTH,0) ,(SCREEN_WIDTH - MAP_WIDTH, 900)),0)
    animationUpdate()
    render()

pygame.quit()  # 退出pygame
