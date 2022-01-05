# -*- coding: UTF-8 -*-

from constants import *
import mapand
import pygame
global_dict = {}

#地图对象定义
######## this param is rgba background color
#BCOLOR = (230,230,255,230)
BCOLOR = (0,0,15,210)
map1= mapand.Map( BCOLOR )

# append a landmine to map
# params: color, position , id
# id must be unique 
#map1.addLDMK(C_RED,(12,-114),0)
#map1.addLDMK(C_RED,(-45,-33),1)
#map1.addLDMK(C_RED,(-27,-18),2)
#map1.addLDMK(C_RED,(-68,-46),3)
#map1.addLDMK(C_RED,(-30,-120),4)

# append a waypoint to map
# params: position, id
# id start from 101 and must be unique
#map1.addWayPoint((29,-54),101)
#map1.addWayPoint((45,-24),102)

# append an area to map
# params: north-west corner positon , east-south corner position, name


#字体定义
font_Basis = pygame.font.Font("src/simulator2D/scripts/font/admin.TTF",16)
font_Basis_h = pygame.font.Font("src/simulator2D/scripts/font/admin.TTF",48)
font_Basis_m = pygame.font.Font("src/simulator2D/scripts/font/admin.TTF",32)
font_Basis_s = pygame.font.SysFont("SimHei",10)
font_Scribe = pygame.font.Font("src/simulator2D/scripts/font/scribe.TTF",18)
#
def set_value(key, value):
    #定义一个全局变量
    global_dict[key] = value

def get_value(key):
    return global_dict[key]





def init(): # 初始化
    global global_dict


    
    bk = pygame.image.load("src/simulator2D/scripts/imgs/main.png")
    bk = pygame.transform.scale(bk,(1040,600))
    set_value("current_map",map1)

    #state
    set_value("is_game_paused",1)
    set_value("is_game_over",0)

    #图层开关
    set_value("layer_ldmk_sw",0)
    set_value("layer_ldmc_sw",0)
    set_value("layer_wlwl_sw",0)

    #细节菜单相关
    set_value("detail_menu",0) #1,2,3分别为开启第一、二、三个细节界面
    set_value("detail_controls",[]) #细节菜单控件
    set_value("detail_selet_id" , 0) #细节菜单中选中的item的id

    #动画相关
    set_value("zoom_kinetic_energy",0)  #缩放动能
    set_value("zoom_f",10)   #缩放阻尼系数
    set_value("drag_kinetic_energy_x",0)  #水平方向拖拽动能
    set_value("drag_kinetic_energy_z",0)  #垂直方向拖拽动能
    set_value("drag_f",5)   #拖拽阻尼系数

    set_value("map_mark",0) #遮罩层不透明度

    set_value("detail_end",0) #细节窗口目标缩放
    set_value("detail_endx",0) #细节窗口目标位置
    set_value("detail_endy",0) 
    set_value("detail_scale",0) #细节窗口缩放
    set_value("detail_posx",0)  #细节窗口位置
    set_value("detail_posy",0)

    set_value("bk_alpha",100) #背景图片不透明度
    set_value("bk_end",1) #目标背景图片
    set_value("bk",bk) #背景

    set_value("end_offsetx",0) #地图目标offsetx
    set_value("end_offsetz",0) #地图目标offsetz
    set_value("end_scale",4) #地图目标scale
    set_value("map_jump_sw",0) #地图跳转开关

    #状态
    set_value("fixed_perspective",0)
    set_value("is_creating_wp",0)
    set_value("is_removing_wp",0)
    set_value("current_page",1)
    set_value("highlight_wp",0)
    set_value("chosed_wp",0)

    #基站经纬度
    #正数表示北纬 / 东经 ， 复数表示 南纬 / 西经
    #JIFUDASHA 
    set_value("base_latitude",39.535999)
    set_value("base_longitude",115.705293)


    # obstacles init
    map1.addObstacle( (-424, -244) , (848, 20) ,1)
    map1.addObstacle( (-424, -224) , (20, 448) ,2)
    map1.addObstacle( (404, -224) , (20, 448) ,3)
    map1.addObstacle( (-424, 224) , (848, 20) ,4)

    
    map1.addObstacle( (-254, -10) , (100, 20) ,9)
    map1.addObstacle( (154, -10) , (100, 20) ,10)

    
    map1.addObstacle( (-50, -130.5) , (100, 20) ,11)
    map1.addObstacle( (-50, 110.5) , (100, 20) ,12)

    
    map1.addObstacle( (-15, -15) , (30, 30) ,13)

    # transparent obstacles

    map1.addObstacle( (-404, -124) , (100, 20) ,5 , color = (200,150,50,100))
    map1.addObstacle( (304, 104) , (100, 20) ,6 , color = (200,150,50,100))
    map1.addObstacle( (-254, 124) , (20, 100) ,7 , color = (200,150,50,100))
    map1.addObstacle( (254, -224) , (20, 100) ,8 , color = (200,150,50,100))

    # areas
    map1.addMarkRect((-404, -224),(100,100), 1 ,"start area", color = C_RED)
    map1.addMarkRect((-404, 124),(100,100), 1 ,"start area", color = C_RED)
    map1.addMarkRect((304, -224),(100,100), 1 ,"start area", color = C_BLUE)
    map1.addMarkRect((304, 124),(100,100), 1 ,"start area", color = C_BLUE)

    # function areas
    map1.addFunctionArea( (-381,-83), (46,40), (200,150,50,180),0, 1)
    map1.addFunctionArea( (187,-83), (46,40), (200,150,50,180),1, 2)

    map1.addFunctionArea( (-27,-203.5), (46,40), (200,150,50,180),2, 6)
    map1.addFunctionArea( (-27,155.5), (46,40), (200,150,50,180),3, 3)

    map1.addFunctionArea( (-241, 31), (46,40), (200,150,50,180),4, 5)
    map1.addFunctionArea( (327, 31), (46,40), (200,150,50,180),5, 4)

    # tanks
    # init_pos,  id , health, team (0-red , 1-blue), basis_yaw ,battery_yaw
    map1.addTank((-364,-174),1, 2000, 0, 0, 0)
    map1.addTank((-364,174), 2, 2000, 0, 0, 0)

    
    map1.addTank((364,174), 3, 2000, 1,  3.14, 0)
    map1.addTank((364,-174), 4, 2000, 1, 3.14, 0)




