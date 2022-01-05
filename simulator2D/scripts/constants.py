# -*- coding: UTF-8 -*-
import pygame
import gol
import control
import toros

PI = 3.14159265

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080  # 设置窗口大小
BASE_SCREEN = pygame.display.set_mode(SCREEN_SIZE)  # 底层窗口

MAP_SCREEN_SIZE = MAP_WIDTH, MAP_HEIGHT = 1480 , SCREEN_HEIGHT
MAP_SCREEN = pygame.Surface(MAP_SCREEN_SIZE, pygame.SRCALPHA)   # 地图窗口
DEBUG_SCREEN = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)   # 调试信息窗口
MAP_MARK = pygame.Surface(MAP_SCREEN_SIZE, pygame.SRCALPHA)   # 地图窗口上方特效/debug2
MAP_FX   = pygame.Surface(MAP_SCREEN_SIZE, pygame.SRCALPHA)   # for change map color
MAP_FX.fill((200,255,200,100))

#static logo
SWITCH_SCREEN = pygame.Surface((SCREEN_WIDTH - MAP_WIDTH, 900), pygame.SRCALPHA)   # 选择控件窗口
logo = pygame.image.load("src/simulator2D/scripts/imgs/logo.png")
BASE_SCREEN.blit(logo,(MAP_WIDTH,900))
############

DETAIL_SCREEN = pygame.Surface((SCREEN_WIDTH - MAP_WIDTH, 100), pygame.SRCALPHA)   # 细节窗口
BG_SCREEN = pygame.Surface((SCREEN_WIDTH ,SCREEN_HEIGHT), pygame.SRCALPHA)   # 背景窗口

#SCRIBE_SCREEN = pygame.Surface((SCREEN_WIDTH - SCREEN_HEIGHT ,450), pygame.SRCALPHA)   # 描述窗口

IN_MAP = 1
IN_SWITCH = 2
IN_DETAIL = 3

#颜色定义 R,G,B,A
C_WHITE = 255, 255, 255,240
C_LIGHTYELLOW = 255,255,200,140
C_DRONE       = 210,110,110,240
C_YELLOW      = 255,255,10,240
C_LIGHTGREEN = 180,255,180,240
C_LIGHTRED = 50,10,10,230
C_LIGHTBLUE = 200, 255, 200,255
C_BLACK = 0,0,0,255
C_RED = 255,100,100,205
C_BLUE = 100,100,255,205
C_GREEN = 55,250,50,255
C_ROUTELINE = 150,150,255,130

#light version
#C_WHITE = 10, 5, 0,240
#C_LIGHTYELLOW = 125,125,10,240
#C_DRONE       = 110,0,0,240
#C_YELLOW      = 55,55,10,240
#C_LIGHTGREEN = 10,55,10,240
#C_LIGHTRED = 255,210,150,255
#C_LIGHTBLUE = 10, 10, 50,255
#C_BLACK = 0,0,0,255
#C_RED = 255,50,50,255
#C_ROUTELINE = 100,100,155,200


btn_tsetshoot = control.Button((150,30),(55,100),(230,255,230,230),"Test shoot",0,"btn_gotobase.png")
#btn_jump2 = control.Button((150,30),(55,110),(230,255,230,230),"Jump to drone",1,"btn_gotodrone.png")
btn_setbase = control.Button((250,30),(55,40),(230,255,230,230),"Set Appropriate perspective",2,"btn_setbase.png")

btn_pasue   = control.Button((35,30),(255,100),(230,255,230,230)," ",1,"btn_next.png")
btn_reset   = control.Button((35,30),(355,100),(230,255,230,230)," ",10,"btn_reset.png")

btn_createwp = control.Button((150,30),(255,685),(230,255,230,230),"create wp",3,"btn_wpcreate.png")
#btn_createwpd = control.Button((150,30),(255,495),(230,255,230,230),"create wp here",4,"btn_wpcreated.png")
btn_removewp = control.Button((150,30),(255,730),(230,255,230,230),"remove wp",5,"btn_wpremove.png")
btn_clearwp = control.Button((150,30),(255,775),(230,255,230,230),"clear wp",6,"btn_wpclear.png")
btn_up = control.Button((50,30),(255,830),(230,255,230,230)," ",7,"btn_up.png")
btn_down = control.Button((50,30),(355,830),(230,255,230,230)," ",8,"btn_down.png")
#btn_createwp = control.Button((150,30),(225,420),(230,255,230,230),"Create wp by point",3,"btn_wpcreate.png")
#btn_createwp = control.Button((150,30),(225,420),(230,255,230,230),"Create wp by point",3,"btn_wpcreate.png")
#btn_createwp = control.Button((150,30),(225,420),(230,255,230,230),"Create wp by point",3,"btn_wpcreate.png")

#traj_pause = control.Button((150,30),(230,20),(230,255,230,230),"暂停",1,"btn_pause.
#traj_pause = control.Button((150,30),(230,20),(230,255,230,230),"暂停",1,"btn_pause.png")
#traj_continue = control.Button((150,30),(230,100),(230,255,230,230),"继续",2,"btn_next.png")
#traj_reset = control.Button((150,30),(45,100),(230,255,230,230),"复位",3,"btn_reset.png")
#traj_fix = control.Button((150,30),(45,180),(230,255,230,230),"游离视角",4,"btn_fix.png")
#traj_ros = control.Button((150,30),(230,180),(230,255,230,230),"未连接ROS",5,"btn_ros.png")

# 此control非彼control，是“控件”
controls = [btn_tsetshoot,btn_pasue,btn_reset,btn_setbase,btn_createwp,btn_removewp,btn_clearwp,btn_up,btn_down]


#图片加载
app_mark = pygame.image.load("src/simulator2D/scripts/imgs/btn_goto.png")
app_mark = pygame.transform.scale(app_mark,(SCREEN_HEIGHT,SCREEN_HEIGHT))

bk_main = pygame.image.load("src/simulator2D/scripts/imgs/btn_goto.png")
bk_main = pygame.transform.scale(bk_main,(SCREEN_WIDTH,SCREEN_HEIGHT))

bk_hell = pygame.image.load("src/simulator2D/scripts/imgs/btn_goto.png")
bk_hell = pygame.transform.scale(bk_hell,(SCREEN_WIDTH,SCREEN_HEIGHT))

bk_end = pygame.image.load("src/simulator2D/scripts/imgs/btn_goto.png")
bk_end = pygame.transform.scale(bk_end,(SCREEN_WIDTH,SCREEN_HEIGHT))

#arrow_ini = pygame.image.load("src/gps/scripts/imgs/btn_goto.png")
#arrow_ini = pygame.transform.scale(arrow_ini,(16,32))

#arrow_now = pygame.image.load("src/gps/scripts/imgs/btn_goto.png")
#arrow_now = pygame.transform.scale(arrow_now,(16,32))



#控制相关
dt = 0.01
Kv = 0.7
Kw = 10

robot_thread = None


