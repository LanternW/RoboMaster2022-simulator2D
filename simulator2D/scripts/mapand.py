# -*- coding: UTF-8 -*-
from constants import *
import pygame
import math
import gol
import control
import random
from asistant import *
import rospy

class HistoryPose():

    def worldXZ2screenXY(self,OFFSET_X,OFFSET_Z,SCALE,x,z):
        screen_x = (SCREEN_HEIGHT / 2) + (x - OFFSET_X) * 100 / (16*SCALE)
        screen_z = (SCREEN_HEIGHT / 2) + (z - OFFSET_Z) * 100 / (16*SCALE)
        return (screen_x,screen_z)

    def __init__(self, pos , color):
        self.pos = pos
        self.color = color
        self.id = 0

    def render(self,SCALE,OFFSET_X,OFFSET_Z,maxid):
        alpha = 255 - 240 * (self.id / float(maxid)) 
        color = (self.color[0], self.color[1] ,self.color[2] ,alpha)
        screen_pos = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,self.pos[0],self.pos[1])
        pygame.draw.circle(MAP_SCREEN,color,screen_pos,3,0)

class HistoryPoseManager():

    def __init__(self,maxid):
        self.history_poses = []
        self.maxid = maxid
    
    def add(self,pose):
        self.history_poses.append(pose)
        for item in self.history_poses:
            item.id += 1
            if item.id > self.maxid:
                self.history_poses.remove(item)
    
    def render(self,OFFSET_X,OFFSET_Z,SCALE):
        for item in self.history_poses:
            item.render(SCALE,OFFSET_X,OFFSET_Z,self.maxid)

############################################################
####### TRAJ ############################################
############################################################

class Trajectoy():

    def worldXZ2screenXY(self,OFFSET_X,OFFSET_Z,SCALE,x,z):
        screen_x = (SCREEN_HEIGHT / 2) + (x - OFFSET_X) * 100 / (16*SCALE)
        screen_z = (SCREEN_HEIGHT / 2) + (z - OFFSET_Z) * 100 / (16*SCALE)
        return (screen_x,screen_z)

    def __init__(self, team , tank_id, optimal_list = []):
        self.optimal_list = optimal_list
        self.team = team
        self.tank_id = tank_id
        self.is_rendering = False
        if team == 0:
            self.color = C_RED
        else:
            self.color = C_BLUE
    
    def replanTraj(self, optimal_list):
        while self.is_rendering == True:
            pass
        self.optimal_list = []
        self.optimal_list = optimal_list

    def render(self,SCALE,OFFSET_X,OFFSET_Z):
        self.is_rendering = True
        n = len(self.optimal_list)
        if n > 3:
            for i in range(0,n-1):
                screen_pos1 = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE, self.optimal_list[i][0] ,self.optimal_list[i][1])
                screen_pos2 = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE, self.optimal_list[i+1][0] ,self.optimal_list[i+1][1])
                pygame.draw.line(MAP_SCREEN,self.color,screen_pos1, screen_pos2,3)

            screen_pos = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE, self.optimal_list[n-1][0] ,self.optimal_list[n-1][1])
            pygame.draw.circle(MAP_SCREEN,self.color, screen_pos,5,0 )
        self.is_rendering = False

############################################################
############################################################
############################################################
############################################################
############################################################
############################################################
class LandMark():

    def __init__(self,posx = 0 , posz = 0 ,color = (255,0,0,255) , id = 0, type_ = 1):
        self.posx = posx
        self.posz = posz
        self.color = color
        self.id = id
        self.type_ = type_
        # type = 1: landmine
        # type = 2: waypoint

    def toPoint(self):
        return (self.posx , self.posz)

    def isIndicated(self,posx,posz):
        if abs(posx - self.posx) < 30 and abs(posz - self.posz) < 10:
            return True
        return False 


class LDMKManager():

    def worldXZ2screenXY(self,OFFSET_X,OFFSET_Z,SCALE,x,z):
        screen_x = (SCREEN_HEIGHT / 2) + (x - OFFSET_X) * 100 / (16*SCALE)
        screen_z = (SCREEN_HEIGHT / 2) + (z - OFFSET_Z) * 100 / (16*SCALE)
        return (screen_x,screen_z)

    def __init__(self):
        self.landmarks = []
        self.waypoints = []
        self.waypoint_buttons_total = []
        self.waypoint_buttons = []
        self.waypbtn_posx = 55
        self.waypbtn_posy = 450
        self.wayp_num = 0
        self.total_pages = 1
        self.current_page = 1
    
    def clearWp(self):
        self.wayp_num = 0
        self.waypoint_buttons_total = []
        self.waypoint_buttons = []
        self.waypoints = []
        self.current_page = 1
        self.WpPageUpdate(1)

    def WpPageUpdate(self,current_page):
        self.total_pages = int(math.ceil(self.wayp_num / 5.0))
        if self.total_pages == 0:
            self.total_pages = 1
        
        if current_page > self.total_pages:
            current_page = self.total_pages
            self.current_page = current_page

        if current_page < 1:
            current_page = 1
            self.current_page = current_page

        self.waypbtn_posy = 450 + 45 * (self.wayp_num % 5)
        self.waypoint_buttons = []
        for i in range( current_page * 5 - 5 , current_page * 5):
            if i >= self.wayp_num:
                return
            temposy = 650 + 45 * (i % 5)
            self.waypoint_buttons_total[i].setPosition((self.waypbtn_posx,temposy))
            self.waypoint_buttons.append(self.waypoint_buttons_total[i])
    
    def addWayPoint(self,pos,id):
        self.waypoints.append(LandMark(pos[0],pos[1],(150,150,255,255),id,2) )
        btn = control.WpButton((150,30),(self.waypbtn_posx,self.waypbtn_posy),(150,150,255,255),"w"+str(id),id)
        self.waypoint_buttons_total.append(btn)

        self.wayp_num += 1
        self.WpPageUpdate(self.current_page)
    
    def removeWayPoint(self,id):
        self.waypoints.remove( self.getWpById(id) )
        for item in self.waypoint_buttons_total:
            if item.id == id:
                self.waypoint_buttons_total.remove(item)

        self.wayp_num -= 1
        self.WpPageUpdate(self.current_page)

    def getValidWpId(self):
        for i in range(101,300):
            if self.getWpById(i) == None:
                return i
        print("waypoints full")
        return None
    
    def getValidLDMKId(self):
        for i in range(0,100):
            if self.getLandmarkById(i) == None:
                return i
        print("landmine full")
        return None

    def render(self,OFFSET_X,OFFSET_Z,SCALE):

        for item in self.landmarks:
            screen_pos = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,item.posx,item.posz)
            if isInMap(screen_pos[0],screen_pos[1],10):
                pygame.draw.rect(MAP_SCREEN,item.color,((screen_pos[0] - 5 , screen_pos[1] - 5),(10,10)),0)
                MAP_SCREEN.blit(gol.font_Basis.render(str(item.id), True, C_LIGHTBLUE), (screen_pos[0] + 10 , screen_pos[1] - 8))
        
        for item in self.waypoints:
            screen_pos = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,item.posx,item.posz)
            if isInMap(screen_pos[0],screen_pos[1],10):
                pygame.draw.rect(MAP_SCREEN,item.color,((screen_pos[0] - 5 , screen_pos[1] - 5),(10,10)),0)
                MAP_SCREEN.blit(gol.font_Basis.render(str("w"+str(item.id)), True, C_LIGHTBLUE), (screen_pos[0] + 10 , screen_pos[1] - 8))
                if item.id == gol.get_value("highlight_wp"):
                    pygame.draw.rect(MAP_SCREEN,(255,255,255,255),((screen_pos[0] - 8 , screen_pos[1] - 8),(16,16)),3)
                    MAP_SCREEN.blit(gol.font_Basis.render(str("w"+str(item.id)), True, C_WHITE ), (screen_pos[0] + 10 , screen_pos[1] - 8))

    def getLandmarkById(self,id):

        for item in self.landmarks:
            if item.id == id:
                return item
        return None
    
    def getWpById(self,id):

        for item in self.waypoints:
            if item.id == id:
                return item
        return None

######################################################
###### obstacle 
#######################################################
class Obstacle():

    def __init__(self,pos = (0,0) , size = (1,1) ,color = (200,150,50,255) , id = 0):
        self.pos  = pos
        self.size = size
        self.pos2 = (pos[0] + size[0] , pos[1] + size[1])
        self.color = color
        self.id = id
    
    def isInObstacle(self, pos):
        if (pos[0] >= self.pos[0] and pos[0] <= self.pos[0] + self.size[0] and pos[1] >= self.pos[1] and pos[1] <= self.pos[1] + self.size[1]):
            return True
        else:
            return False


class ObstacleManager():

    def worldXZ2screenXY(self,OFFSET_X,OFFSET_Z,SCALE,x,z):
        screen_x = (SCREEN_HEIGHT / 2) + (x - OFFSET_X) * 100 / (16*SCALE)
        screen_z = (SCREEN_HEIGHT / 2) + (z - OFFSET_Z) * 100 / (16*SCALE)
        return (screen_x,screen_z)

    def __init__(self):
        self.obstacles = []
    
    def addObstacle(self,pos,size,id,color = (200,150,50,255)):
        self.obstacles.append(Obstacle(pos,size,color,id))
    
    def render(self,OFFSET_X,OFFSET_Z,SCALE):

        for item in self.obstacles:
            screen_pos  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,item.pos[0],item.pos[1])
            screen_pos2 = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,item.pos2[0],item.pos2[1])
            screen_size = (screen_pos2[0] - screen_pos[0] , screen_pos2[1] - screen_pos[1])
            #if isInMap(screen_pos[0],screen_pos[1],20) or isInMap(screen_pos2[0],screen_pos2[1],20):
            pygame.draw.rect(MAP_SCREEN,item.color, (screen_pos, screen_size), 0)

############################################################
##########  Mark Rect
############################################################
class MarkRect():
    def __init__(self,pos = (0,0) , size = (1,1) ,color = (200,20,20,255) , text="area" , id = 0):
        self.pos  = pos
        self.size = size
        self.pos2 = (pos[0] + size[0] , pos[1] + size[1])
        self.color = color
        self.text = text
        self.id = id

class MarkRectManager():

    def worldXZ2screenXY(self,OFFSET_X,OFFSET_Z,SCALE,x,z):
        screen_x = (SCREEN_HEIGHT / 2) + (x - OFFSET_X) * 100 / (16*SCALE)
        screen_z = (SCREEN_HEIGHT / 2) + (z - OFFSET_Z) * 100 / (16*SCALE)
        return (screen_x,screen_z)

    def __init__(self):
        self.markrect = []
    
    def addMarkRect(self,pos,size,id,text ,color):
        self.markrect.append(MarkRect(pos,size,color,text,id))
    
    def render(self,OFFSET_X,OFFSET_Z,SCALE):

        for item in self.markrect:
            screen_pos  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,item.pos[0],item.pos[1])
            screen_pos2 = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,item.pos2[0],item.pos2[1])
            screen_size = (screen_pos2[0] - screen_pos[0] , screen_pos2[1] - screen_pos[1])
            if isInMap(screen_pos[0],screen_pos[1],10) or isInMap(screen_pos2[0],screen_pos2[1],10):
                pygame.draw.rect(MAP_SCREEN,item.color, (screen_pos, screen_size), 8)
                if SCALE < 8:
                    MAP_SCREEN.blit(gol.font_Basis.render(item.text, True, item.color), ( screen_pos[0] + 10, screen_pos[1] + 10))

############################################################
##########  Function area
############################################################  
class FunctionArea():
    def __init__(self,pos = (0,0) , size = (1,1) ,color = (200,20,20,255) , type = 0 , id = 0):
        self.pos  = pos
        self.size = size
        self.pos2 = (pos[0] + size[0] , pos[1] + size[1])
        self.posc = (pos[0] + 0.5*size[0] , pos[1] + 0.5*size[1])
        self.color = color

        self.type = type
        #0-红方回血区   1-禁止射击  2-红方子弹补给 3-蓝回血 4-禁止移动 5-蓝子弹补给

        self.id = id

    def isPointIn(self, pos):
        if pos[0] > self.pos[0] and pos[0] < self.pos2[0] and pos[1] > self.pos[1] and pos[1] < self.pos2[1]:
            return True
        return False

class FunctionAreaManager():

    def worldXZ2screenXY(self,OFFSET_X,OFFSET_Z,SCALE,x,z):
        screen_x = (SCREEN_HEIGHT / 2) + (x - OFFSET_X) * 100 / (16*SCALE)
        screen_z = (SCREEN_HEIGHT / 2) + (z - OFFSET_Z) * 100 / (16*SCALE)
        return (screen_x,screen_z)

    def __init__(self):
        self.function_areas = []
    
    def addFunctionArea(self,pos,size ,color, type, id):
        self.function_areas.append(FunctionArea(pos,size,color,type,id))
    
    def getAreaById(self,id):
        for item in self.function_areas:
            if item.id == id:
                return item
        return None

    def getAreaTypeById(self,id):
        area = self.getAreaById(id)
        if area != None:
            return area.type
    
    def getCorId(self,id):
        if id <= 3:
            return id + 3
        else:
            return id - 3

    def refreshFunctionArea(self):
        refreshed = []
        id = random.randint(1,6)
        while id in refreshed:
            id = random.randint(1,6)
        refreshed.append(id)
        refreshed.append(self.getCorId(id))
        self.getAreaById(id).type = 0
        self.getAreaById(self.getCorId(id)).type = 3

        id = random.randint(1,6)
        while id in refreshed:
            id = random.randint(1,6)
        refreshed.append(id)
        refreshed.append(self.getCorId(id))
        self.getAreaById(id).type = 1
        self.getAreaById(self.getCorId(id)).type = 4

        id = random.randint(1,6)
        while id in refreshed:
            id = random.randint(1,6)
        refreshed.append(id)
        refreshed.append(self.getCorId(id))
        self.getAreaById(id).type = 2
        self.getAreaById(self.getCorId(id)).type = 5
        
    
    def render(self,OFFSET_X,OFFSET_Z,SCALE):

        for item in self.function_areas:
            screen_pos  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,item.pos[0],item.pos[1])
            screen_pos2 = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,item.pos2[0],item.pos2[1])
            screen_posc = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,item.posc[0],item.posc[1])
            screen_size = (screen_pos2[0] - screen_pos[0] , screen_pos2[1] - screen_pos[1])

            cross_p1 = (screen_pos[0] + 0.3*screen_size[0] , screen_pos[1] + 0.5*screen_size[1])
            cross_p2 = (screen_pos[0] + 0.7*screen_size[0] , screen_pos[1] + 0.5*screen_size[1])
            cross_p3 = (screen_pos[0] + 0.5*screen_size[0] , screen_pos[1] + 0.3*screen_size[1])
            cross_p4 = (screen_pos[0] + 0.5*screen_size[0] , screen_pos[1] + 0.7*screen_size[1])
            rect_p1  = (screen_pos[0] + 0.3*screen_size[0] , screen_pos[1] + 0.3*screen_size[1])
            rect_p2  = (screen_pos[0] + 0.7*screen_size[0] , screen_pos[1] + 0.7*screen_size[1])
            rect_size= (rect_p2[0] - rect_p1[0] , rect_p2[1] - rect_p1[1])

            if isInMap(screen_pos[0],screen_pos[1],50) or isInMap(screen_pos2[0],screen_pos2[1],50):
                pygame.draw.rect(MAP_SCREEN,item.color, (screen_pos, screen_size), 6)
                if item.type == 0:
                    pygame.draw.line(MAP_SCREEN, C_RED, cross_p1, cross_p2 , 6)
                    pygame.draw.line(MAP_SCREEN, C_RED, cross_p3, cross_p4 , 6)
                elif item.type == 3:
                    pygame.draw.line(MAP_SCREEN, C_BLUE, cross_p1, cross_p2 , 6)
                    pygame.draw.line(MAP_SCREEN, C_BLUE, cross_p3, cross_p4 , 6)
                elif item.type == 1:
                    pygame.draw.circle(MAP_SCREEN, item.color, screen_posc, 80/SCALE , 5)
                    pygame.draw.line(MAP_SCREEN,   item.color, rect_p1, rect_p2 , 5)
                elif item.type == 4:
                    pygame.draw.rect(MAP_SCREEN, item.color, (rect_p1, rect_size) , 5)
                    pygame.draw.line(MAP_SCREEN,   item.color, rect_p1, rect_p2 , 5)
                elif item.type == 2:
                    pygame.draw.circle(MAP_SCREEN, C_RED, screen_posc, 80/SCALE , 5)
                elif item.type == 5:
                    pygame.draw.circle(MAP_SCREEN, C_BLUE, screen_posc, 80/SCALE , 5)

                

                    



############################################################
##########  TANK
############################################################     
class Tank():
    def __init__(self,init_pos , id , health,team , basis_yaw , battery_yaw ):
        self.pos         = init_pos
        self.id          = id
        self.health      = health
        self.team        = team
        # 0 : red team | 1: blue team

        self.bullet_count = 50
        self.heat         = 0

        self.behitque      = [] #For judging critical hit
        self.hit_time      = []

        self.dead        = False
        self.noshooting  = False
        self.noshooting_time = 0
        self.noshooting_trigger_time = 0
        self.nomoving    = False
        self.nomoving_time   = 0
        self.nomoving_trigger_time = 0

        self.basis_yaw   = basis_yaw
        self.battery_yaw = battery_yaw

        self.vel        = (0,0)
        self.yawdot     = 0
        self.bat_yawdot = 0

        if team == 0:
            self.color = (255, 100, 100, 200)
        elif team == 1:
            self.color = (100, 100, 255, 200)
        else:
            self.color = (255, 255, 100, 200)
        
        self.trajectory = Trajectoy(team, id, [])
    
    def setTrajectory(self, traj):
        self.trajectory.replanTraj(traj)
    
    def setNoShooting(self):
        self.noshooting_trigger_time = rospy.Time.now().to_sec()
        self.noshooting  = True
        self.noshooting_time =10
    
    def setNoMoving(self):
        self.nomoving_trigger_time = rospy.Time.now().to_sec()
        self.nomoving  = True
        self.nomoving_time =10
        self.vel = (0,0)
        self.yawdot = 0

    
    def isPointIn(self, pos):
        cyaw = math.cos( self.basis_yaw )
        syaw = math.sin( self.basis_yaw )
        pbx = cyaw * (pos[0]- self.pos[0]) + syaw * (pos[1] - self.pos[1])
        pby = syaw * (self.pos[0] - pos[0]) + cyaw * (-pos[1] + self.pos[1])
        if abs(pbx) < 28 and abs(pby) < 22:
            return True
        return False
    
    def criticalHitJudger(self, part):
        n = len(self.behitque)
        score = 0
        self.behitque.append(part)
        self.hit_time.append(rospy.Time.now().to_sec())
        if n < 9:
            return False
        else:
            if self.behitque[0] == self.behitque[1] == self.behitque[2] == self.behitque[6] == self.behitque[7] == self.behitque[8]:
                if self.behitque[3] != self.behitque[2] and self.behitque[3] == self.behitque[4] == self.behitque[5] and (self.hit_time[8] - self.hit_time[0]) < 8:
                    self.loseHealth(150)
                    score = 150
            self.behitque.remove(self.behitque[0])
            self.hit_time.remove(self.hit_time[0])
        return score
            
    
    def getCornerPos(self, point_id):
        cyaw = math.cos( self.basis_yaw )
        syaw = math.sin( self.basis_yaw )
        Pcb = (0,0)
        if point_id == 1:
            Pcb = (28,-22)
        elif point_id == 2:
            Pcb = (28,22)
        elif point_id == 3:
            Pcb = (-28,22)
        elif point_id == 4:
            Pcb = (-28,-22)
        
        elif point_id == 5:
            Pcb = (28,-6)
        elif point_id == 6:
            Pcb = (28,6)
        elif point_id == 7:
            Pcb = (6,22)
        elif point_id == 8:
            Pcb = (-6,22)
        elif point_id == 9:
            Pcb = (-28,6)
        elif point_id == 10:
            Pcb = (-28,-6)
        elif point_id == 11:
            Pcb = (-6,-22)
        elif point_id == 12:
            Pcb = (6,-22)
        #2D rotation matrix
        Pcw = (cyaw * Pcb[0] - syaw * Pcb[1] + self.pos[0], syaw * Pcb[0] + cyaw * Pcb[1] +self.pos[1])
        return Pcw
    
    def getBatteryPos(self):
        cyaw = math.cos( self.basis_yaw )
        syaw = math.sin( self.basis_yaw )
        Pcb = (20 * math.cos(self.battery_yaw), 20 *math.sin(self.battery_yaw))
        Pcw1 = (cyaw * Pcb[0] - syaw * Pcb[1] + self.pos[0], syaw * Pcb[0] + cyaw * Pcb[1] +self.pos[1])
        
        Pcb = (10 * math.cos(self.battery_yaw), 10 *math.sin(self.battery_yaw))
        Pcw2 = (cyaw * Pcb[0] - syaw * Pcb[1] + self.pos[0], syaw * Pcb[0] + cyaw * Pcb[1] +self.pos[1])
        return Pcw1,Pcw2
    
    def getBulletShootInfo(self, bullet_velnorm):
        pcw1,pcw2 = self.getBatteryPos()
        bullet_pos = pcw2
        bullet_vel = (pcw1[0] - pcw2[0] , pcw1[1] - pcw2[1])
        bullet_vel = (bullet_velnorm * bullet_vel[0] / 10 , bullet_velnorm * bullet_vel[1] / 10)  #bullet_velnorm m/s
        return bullet_pos, bullet_vel
    
    def loseHealth(self, num):
        self.health = self.health - num
        if self.health < 0:
            self.health = 0
            self.dead   = True

    def loseHeat(self):
        
        if self.heat > 240 and self.heat < 360:
            self.loseHealth( ( self.heat - 240 )* 4)
        elif self.heat >= 360:
            self.loseHealth( (self.heat - 360)* 40)
            self.heat = 360

        if self.health <= 400:
            self.heat = self.heat - 24
        else:
            self.heat = self.heat - 12
        if self.heat < 0:
            self.heat = 0

    
    def shootBullet(self, bv):
        self.bullet_count = self.bullet_count - 1
        if self.bullet_count < 0:
            self.bullet_count = 0
        self.heat = self.heat + 0.01 * bv
        if bv >= 2500 and bv < 3000:
            self.loseHealth(200)
        elif bv >= 3000 and bv < 3500:
            self.loseHealth(1000)
        elif bv >= 3500:
            self.loseHealth(2000)

    
    def updatePose(self,dt):
        self.pos = (self.pos[0] + self.vel[0] * dt , self.pos[1] + self.vel[1] * dt)
        self.basis_yaw   = self.basis_yaw + self.yawdot * dt
        self.battery_yaw = self.battery_yaw + self.bat_yawdot * dt
    
    def updateState(self):
        time = rospy.Time.now().to_sec()
        if self.noshooting and time - self.noshooting_trigger_time > 10:
            self.noshooting = False
        if self.nomoving and time - self.nomoving_trigger_time > 10:
            self.nomoving = False
        
        self.nomoving_time = 10 - (time - self.nomoving_trigger_time)
        self.noshooting_time = 10 - (time - self.noshooting_trigger_time)
    
    def isBeHit(self,pos, team):
        #击中则返回真，特别地击中装甲要扣血,理论上用凸包矩阵Ax < 0判断更好，但计算量太大
        p1,p2,p3,p4 = self.getCornerPos(1), self.getCornerPos(2), self.getCornerPos(3), self.getCornerPos(4)
        p5,p6,p7,p8 = self.getCornerPos(5), self.getCornerPos(6), self.getCornerPos(7), self.getCornerPos(8)
        p9,p10,p11,p12 = self.getCornerPos(9), self.getCornerPos(10), self.getCornerPos(11), self.getCornerPos(12)
       
        #if abs(pos[0] - p3[0]) < 10: 
        #    print( isOnLineSeg(p4,p3,pos))
        score = 0
        if(isOnLineSeg(p1,p2,pos) == True):
             # The forward deck is hit
            if(team != self.team and isOnLineSeg(p5,p6,pos) == True):
                self.loseHealth(20)
                score = score + 20
                score = score + self.criticalHitJudger(1)
            return score

        # The side ...
        elif (isOnLineSeg(p2,p3,pos) == True):
            if( team != self.team and (isOnLineSeg(p7,p8,pos) == True or isOnLineSeg(p11,p12,pos) == True) ):
                self.loseHealth(40)
                score = score + 40
                score = score + self.criticalHitJudger(2)
            return score
        
        elif (isOnLineSeg(p1,p4,pos) == True):
            if( team != self.team and (isOnLineSeg(p7,p8,pos) == True or isOnLineSeg(p11,p12,pos) == True) ):
                self.loseHealth(40)
                score = score + 40
                score = score + self.criticalHitJudger(3)
            return score

        # back
        elif (isOnLineSeg(p4,p3,pos) == True ):
            if( team != self.team and isOnLineSeg(p9,p10,pos) == True):
                self.loseHealth(60)
                score = score + 60
                score = score + self.criticalHitJudger(4)
            return score
        
        return 0


class TankManager():
    def worldXZ2screenXY(self,OFFSET_X,OFFSET_Z,SCALE,x,z):
        screen_x = (SCREEN_HEIGHT / 2) + (x - OFFSET_X) * 100 / (16*SCALE)
        screen_z = (SCREEN_HEIGHT / 2) + (z - OFFSET_Z) * 100 / (16*SCALE)
        return (screen_x,screen_z)

    def __init__(self):
        self.tanks = []

    def addTank(self, init_pos, id, health , team, basis_yaw, battery_yaw):
        self.tanks.append(Tank(init_pos,id, health , team, basis_yaw, battery_yaw))
    
    def setTankVelocity(self, id, vel, yawdot, bat_yawdot):
        tank = self.getTankById(id)
        if tank.nomoving == False and not tank.dead:
            tank.vel        = vel
            tank.yawdot     = yawdot
        else:
            tank.vel        = (0,0)
            tank.yawdot     = 0
        tank.bat_yawdot = bat_yawdot
    
    def setTankTraj(self, id, traj):
        tank = self.getTankById(id)
        tank.setTrajectory(traj)
    
    def setTankPose(self, id ,pos ,basis_yaw, bat_yaw):
        tank = self.getTankById(id)
        tank.pos        = pos
        tank.basis_yaw     = basis_yaw
        tank.batery_yaw = bat_yaw

    def getTankState(self, id):
        tank = self.getTankById(id)
        pos = tank.pos
        vel = tank.vel
        basis_yaw = tank.basis_yaw
        bat_yaw   = tank.battery_yaw
        basis_yawdot = tank.yawdot
        bat_yawdot   = tank.bat_yawdot
        return pos, vel, basis_yaw, bat_yaw, basis_yawdot, bat_yawdot
    
    def getTankOdometry(self, id):
        tank = self.getTankById(id)
        pos = tank.pos
        vel = tank.vel
        basis_yaw = tank.basis_yaw
        basis_yawdot = tank.yawdot
        return pos, vel, basis_yaw, basis_yawdot
    
    def getTankById(self,id):
        for item in self.tanks:
            if item.id == id:
                return item
        return None
    
    def getTanksByTeam(self,team):
        tanks = []
        for item in self.tanks:
            if item.team == team:
                tanks.append(item)
        return tanks


    def render(self,OFFSET_X,OFFSET_Z,SCALE):

        for item in self.tanks:
            p1,p2,p3,p4 = item.getCornerPos(1), item.getCornerPos(2), item.getCornerPos(3), item.getCornerPos(4)
            p5,p6,p7,p8 = item.getCornerPos(5), item.getCornerPos(6), item.getCornerPos(7), item.getCornerPos(8)
            p9,p10,p11,p12 = item.getCornerPos(9), item.getCornerPos(10), item.getCornerPos(11), item.getCornerPos(12)
            pb1,pb2 = item.getBatteryPos()

            sp1  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,p1[0],p1[1])
            sp2  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,p2[0],p2[1])
            sp3  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,p3[0],p3[1])
            sp4  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,p4[0],p4[1])

            sp5  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,p5[0],p5[1])
            sp6  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,p6[0],p6[1])
            sp7  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,p7[0],p7[1])
            sp8  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,p8[0],p8[1])

            sp9  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,p9[0],p9[1])
            sp10  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,p10[0],p10[1])
            sp11  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,p11[0],p11[1])
            sp12  = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE,p12[0],p12[1])

            spc   = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE, item.pos[0],item.pos[1])
            spb1   = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE, pb1[0], pb1[1])
            spb2   = self.worldXZ2screenXY(OFFSET_X,OFFSET_Z,SCALE, pb2[0], pb2[1])
            
            item.trajectory.render(SCALE,OFFSET_X,OFFSET_Z)
            if isInMap(sp1[0],sp1[1],20) or isInMap(sp2[0],sp2[1],20) or isInMap(sp3[0],sp3[1],20) or isInMap(sp4[0],sp4[1],20):
                pygame.draw.line(MAP_SCREEN, C_WHITE, sp1,sp2 ,2)
                pygame.draw.line(MAP_SCREEN, C_WHITE, sp2,sp3 ,2)
                pygame.draw.line(MAP_SCREEN, item.color, sp3,sp4 ,2)
                pygame.draw.line(MAP_SCREEN, C_WHITE, sp4,sp1 ,2)
                
                pygame.draw.line(MAP_SCREEN, item.color, sp5,sp6 ,5)
                pygame.draw.line(MAP_SCREEN, item.color, sp7,sp8 ,5)
                pygame.draw.line(MAP_SCREEN, item.color, sp9,sp10 ,5)
                pygame.draw.line(MAP_SCREEN, item.color, sp11,sp12 ,5)

                pygame.draw.circle(MAP_SCREEN, C_WHITE, spc, 90/SCALE, 2)
                pygame.draw.line(MAP_SCREEN, C_WHITE, spb2,spb1 ,2)

                MAP_SCREEN.blit(gol.font_Basis.render(str(item.id), True, item.color), ( spc[0]-5, spc[1] -10))

########################################
##### bullet
########################################  

class Bullet():
    def __init__(self,pos ,vel,team ,tank_id):
        self.pos         = pos
        self.last_pos    = pos
        self.vel         = vel
        self.team        = team
        self.tank_id     = tank_id
        self.hispose_manager = HistoryPoseManager(50)
        # 0 : red team | 1: blue team
        if team == 0:
            self.color = (255,100,100,255)
        elif team == 1:
            self.color = (100,100,255,255)
    def update(self, dt):
        self.last_pos = self.pos
        self.pos = (self.pos[0] + self.vel[0] * dt , self.pos[1] + self.vel[1] * dt)
        for s in range(0,10,1):
            t = s/10.0
            #cpos = (self.last_pos[0] * t + self.pos[0] * (1-t) , self.last_pos[1] * t + self.pos[1] * (1-t))
            cpos = (self.last_pos[0] * (1-t) + self.pos[0] * t , self.last_pos[1] * (1-t) + self.pos[1] * t)
            self.hispose_manager.add(HistoryPose(cpos, self.color))

class BulletManager():
    def worldXZ2screenXY(self,OFFSET_X,OFFSET_Z,SCALE,x,z):
        screen_x = (SCREEN_HEIGHT / 2) + (x - OFFSET_X) * 100 / (16*SCALE)
        screen_z = (SCREEN_HEIGHT / 2) + (z - OFFSET_Z) * 100 / (16*SCALE)
        return (screen_x,screen_z)

    def __init__(self):
        self.bullets = []
    def createBullet(self, pos, vel, team, tk_id):
        self.bullets.append(Bullet( pos, vel, team, tk_id))
    
    def updatePos(self,dt):
        for item in self.bullets:
            item.update(dt)
            if distance((0,0), item.pos) > 1000:
                self.bullets.remove(item)


    def render(self,OFFSET_X,OFFSET_Z,SCALE):
         for item in self.bullets:
             item.hispose_manager.render(OFFSET_X, OFFSET_Z, SCALE)


def colorMerge(color1 , color2): #颜色线性插值器
    k = 0.5
    (r1,g1,b1,a1) = color1
    (r2,g2,b2,a2) = color2
    r = r1 + k * (r2 - r1)
    g = g1 + k * (g2 - g1)
    b = b1 + k * (b2 - b1)
    a = 0.5 * (a1 + a2)
    return (r,g,b,a)


#########################################################
#########################################################
#########################################################

class Map():
    def __init__(self,bc = (128,0,0,0)):
        self.last_path = None
        self.back_color = bc
        self.SCALE = 4.0
        self.OFFSET_X = -120
        self.OFFSET_Z = 0
        
        self.ROTATE_DEGREE = 0

        self.blue_score = 0
        self.red_score  = 0


        self.landmarks_manager = LDMKManager()
        self.obstacle_manager  = ObstacleManager()
        self.markrect_manager  = MarkRectManager()
        self.tank_manager      = TankManager()
        self.bullet_manager    = BulletManager()
        self.functionarea_manager = FunctionAreaManager()


    def addLDMK(self,color,pos,id):
        self.landmarks_manager.landmarks.append(LandMark(pos[0],pos[1],color,id))

    def addWayPoint(self,pos,id):
        self.landmarks_manager.addWayPoint(pos,id)

    def addObstacle(self, pos,size,id,color = (200,150,50,205)):
        self.obstacle_manager.addObstacle(pos,size,id,color)

    def addMarkRect(self, pos,size,id,text,color = (200,20,20,205)):
        self.markrect_manager.addMarkRect(pos,size,id,text,color)
    
    def addFunctionArea(self,pos,size ,color, type, id):
        self.functionarea_manager.addFunctionArea(pos,size ,color, type, id)

    def addTank(self, init_pos, id, health , team, basis_yaw, battery_yaw):
        self.tank_manager.addTank(init_pos, id, health , team, basis_yaw, battery_yaw)
    
    def createBullet(self, pos,vel ,team, tk_id):
        self.bullet_manager.createBullet(pos,vel,team, tk_id)
    
    def shoot(self, tank_id, bullet_vel):
        if gol.get_value("is_game_paused") == False:
            tank = self.tank_manager.getTankById(tank_id)
            if tank != None and tank.bullet_count > 0 and tank.noshooting == False and not tank.dead:
                bp,bv = tank.getBulletShootInfo(bullet_vel)
                self.bullet_manager.createBullet(bp,bv,tank.team, tank_id)
                tank.shootBullet(bullet_vel)



    def scanWpOnMap(self,mouse_posx,mouse_posy):
        (wx,wz) = self.screenXY2worldXZ(mouse_posx,mouse_posy)
        for item in self.landmarks_manager.waypoints:
            (sx,sy) = self.worldXZ2screenXY(item.posx , item.posz)
            if isInMap(sx,sy):
                if mouse_posx - sx < 50 and mouse_posx - sx > -4 and abs(mouse_posy - sy) < 10:
                    return item.id
        
        return 0

    def searchLDMK(self,pos,range):
        for item in self.landmarks_manager.waypoints:
            if distance(item.toPoint() , pos) < range:
                return item

        return None


    def worldXZ2screenXY(self,x,z):
        screen_x = (SCREEN_HEIGHT / 2) + (x - self.OFFSET_X) * 100 / (16*self.SCALE)
        screen_z = (SCREEN_HEIGHT / 2) + (z - self.OFFSET_Z) * 100 / (16*self.SCALE)
        return (screen_x,screen_z)

    def screenXY2worldXZ(self,x,y):
        world_x = (x - (SCREEN_HEIGHT / 2)) * (16*self.SCALE) / 100 + self.OFFSET_X
        world_z = (y - (SCREEN_HEIGHT / 2)) * (16*self.SCALE) / 100 + self.OFFSET_Z
        return (world_x,world_z)

################################################
####### MAP-RENDER
    def renderGrid(self):

        delta_scan = 16
        if self.SCALE > 10:
            delta_scan = 64
        center_x = math.floor(self.OFFSET_X / delta_scan)
        center_z = math.floor(self.OFFSET_Z / delta_scan)
        temp_x = center_x * delta_scan
        temp_z = center_z * delta_scan
        (ts_x , ts_y) = self.worldXZ2screenXY(temp_x,temp_z)

        
        while True:
            if ts_x < 0 and ts_y < 0:
                break
            if (False) :
                line_width = 2
                line_color = colorMerge(self.back_color,(0,0,0,255))
            else:
                line_width = 1
                line_color = colorMerge(self.back_color,(100,100,100,255))
            pygame.draw.lines(MAP_SCREEN, line_color, False, [(ts_x,0) , (ts_x,MAP_WIDTH)],line_width)
            pygame.draw.lines(MAP_SCREEN, line_color, False, [(0,ts_y) , (MAP_WIDTH,ts_y)],line_width) 
            temp_x = temp_x - delta_scan
            temp_z = temp_z - delta_scan
            (ts_x , ts_y) = self.worldXZ2screenXY(temp_x,temp_z) 
        
        temp_x = center_x * delta_scan + delta_scan
        temp_z = center_z * delta_scan + delta_scan
        (ts_x , ts_y) = self.worldXZ2screenXY(temp_x,temp_z)

        while True:
            if ts_x > MAP_WIDTH and ts_y > SCREEN_HEIGHT:
                break
            if ts_x < 0 and ts_y < 0:
                break
            if (False) :
                line_width = 2
                line_color = colorMerge(self.back_color,(0,0,0,255))
            else:
                line_width = 1
                line_color = colorMerge(self.back_color,(100,100,100,255))
            pygame.draw.lines(MAP_SCREEN, line_color, False, [(ts_x,0) , (ts_x,MAP_WIDTH)],line_width)
            pygame.draw.lines(MAP_SCREEN, line_color, False, [(0,ts_y) , (MAP_WIDTH,ts_y)],line_width) 
            temp_x = temp_x + delta_scan
            temp_z = temp_z + delta_scan
            (ts_x , ts_y) = self.worldXZ2screenXY(temp_x,temp_z) 

    def renderLDMKS(self):
        self.landmarks_manager.render(self.OFFSET_X,self.OFFSET_Z,self.SCALE)

    def renderObstacles(self):
        self.obstacle_manager.render(self.OFFSET_X,self.OFFSET_Z,self.SCALE)
        
    def renderMarkRects(self):
        self.markrect_manager.render(self.OFFSET_X,self.OFFSET_Z,self.SCALE)

    def renderTanks(self):
        self.tank_manager.render(self.OFFSET_X,self.OFFSET_Z,self.SCALE)

    def renderBullets(self):
        self.bullet_manager.render(self.OFFSET_X,self.OFFSET_Z,self.SCALE)
    
    def renderFunctionArea(self):
        self.functionarea_manager.render(self.OFFSET_X,self.OFFSET_Z,self.SCALE)

    def renderCross(self):
        MAP_SCREEN.blit(gol.font_Basis.render(str("+"), True, (100, 0, 0,128)), (int(SCREEN_HEIGHT/2) ,int(SCREEN_HEIGHT/2) - 4 ))

    def renderAxis(self):
        (screen_posx,screen_posy) = self.worldXZ2screenXY(0,0)
        if isInMap(screen_posx,screen_posy , 20):
            pygame.draw.line(MAP_SCREEN, C_RED, (screen_posx+2,screen_posy),(screen_posx+20,screen_posy),2 )
            pygame.draw.line(MAP_SCREEN, C_GREEN, (screen_posx,screen_posy+2),(screen_posx,screen_posy+20),2 )
        

    def renderBase(self):

        MAP_SCREEN.fill(self.back_color)
        if gol.get_value("fixed_perspective") == 1:
            self.OFFSET_X = self.now_pos_x
            self.OFFSET_Z = self.now_pos_z

##############################33
##update and reset
###############################

    def triggerFunctionArea(self, tank, function_area):
        if function_area.type == 0:
            tanks = self.tank_manager.getTanksByTeam(0)
            for tank in tanks:
                tank.health = tank.health + 200
        elif function_area.type == 3:
            tanks = self.tank_manager.getTanksByTeam(1)
            for tank in tanks:
                tank.health = tank.health + 200
         
        elif function_area.type == 2:
            tanks = self.tank_manager.getTanksByTeam(0)
            for tank in tanks:
                tank.bullet_count = tank.bullet_count + 100
         
        elif function_area.type == 5:
            tanks = self.tank_manager.getTanksByTeam(1)
            for tank in tanks:
                tank.bullet_count = tank.bullet_count + 100
 
        elif function_area.type == 1:
            tank.setNoShooting()
         
        elif function_area.type == 4:
            tank.setNoMoving()

        function_area.type = 100

    def updateHeat(self):
        for tank in self.tank_manager.tanks:
            tank.loseHeat()
            tank.updateState()

    def update(self,dt):
        self.bullet_manager.updatePos(dt)

        # bullet crash obstacle
        for obstacle in self.obstacle_manager.obstacles:
            for bullet in self.bullet_manager.bullets:
                lpos = bullet.last_pos
                npos = bullet.pos
                for s in range(0,5,1):
                    t = s/5.0
                    cpos = (lpos[0] * t + npos[0] * (1-t) , lpos[1] * t + npos[1] * (1-t))
                    if obstacle.isInObstacle(cpos):
                        self.bullet_manager.bullets.remove(bullet)
                        break
        
        # tank trigger buff
        for funciton_area in self.functionarea_manager.function_areas:
            if funciton_area.type != -1:
                for tank in self.tank_manager.tanks:
                    if distance( tank.pos , funciton_area.posc) < 66:
                        pa3 = (funciton_area.pos[0] + funciton_area.size[0] , funciton_area.pos[1])
                        pa4 = (funciton_area.pos[0]  , funciton_area.pos[1] + funciton_area.size[1])
                        if tank.isPointIn(funciton_area.pos) or tank.isPointIn(funciton_area.pos2) or tank.isPointIn(pa3) or tank.isPointIn(pa4):
                            self.triggerFunctionArea(tank, funciton_area)
                            #print(1)
                            continue
                        p1,p2,p3,p4 = tank.getCornerPos(1), tank.getCornerPos(2) , tank.getCornerPos(3), tank.getCornerPos(4)
                        if funciton_area.isPointIn(p1) or funciton_area.isPointIn(p2) or funciton_area.isPointIn(p3) or funciton_area.isPointIn(p4):
                            self.triggerFunctionArea(tank, funciton_area)
                            continue

        # bullet hit tank
        for tank in self.tank_manager.tanks:
            tank.updatePose(dt)
            for bullet in self.bullet_manager.bullets:
                if tank.id != bullet.tank_id:
                    if distance(tank.pos, bullet.pos) < 40:
                        lpos = bullet.last_pos
                        npos = bullet.pos
                        for s in range(0,300,1):
                            t = s/300.0
                            cpos = (lpos[0] * t + npos[0] * (1-t) , lpos[1] * t + npos[1] * (1-t))
                            score = tank.isBeHit(cpos, bullet.team)
                            if score > 0:
                                self.bullet_manager.bullets.remove(bullet)
                                if tank.team == 0:
                                    self.blue_score = self.blue_score + score
                                else:
                                    self.red_score = self.red_score + score
                                break

    def reset(self):
        self.tank_manager.tanks = []
        self.addTank((-364,-174),1, 2000, 0, 0, 0)
        self.addTank((-364,174), 2, 2000, 0, 0, 0)

        
        self.addTank((364,174), 3, 2000, 1,  3.14, 0)
        self.addTank((364,-174), 4, 2000, 1, 3.14, 0)
        self.blue_score = self.red_score = 0
        pass


