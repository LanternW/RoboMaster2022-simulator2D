# -*- coding: UTF-8 -*-
import pygame 
import gol




class Switch(object):    #选择器
    def __init__(self,rect = (20,10) , position = (0,0) , color = (255,255,255,100),str_name = "选择" ,id = 0):

        self.rect = rect            #控件矩形框尺寸
        self.position = position    #位置
        self.selected = False       #被选中情况
        self.color = color          #颜色
        self.str_name = str_name
        self.id = id

        self.frame_color_direct = -1 #选中框颜色变化趋势
        self.frame_color = (255,255,255,0) #选中框颜色
    
    def isPassedBy(self,x,y): #鼠标是否在控件上
        if (x > self.position[0] and x < self.position[0] + self.rect[0]) and (y > self.position[1] and y < self.position[1] + self.rect[1]):
            return True
        return False
    def onPassedBy(self,x,y):
        if self.isPassedBy(x,y) == True:
            self.frame_color_direct = 8
        else:
            self.frame_color_direct = -4

    def animationUpdate(self):
        if self.selected == False:
            fa = self.frame_color[3]
            if self.frame_color_direct != 0:
                fa = fa + self.frame_color_direct
            if fa > 128:
                fa = 128
            if fa < 0:
                fa = 0
            self.frame_color = (255,255,255,fa)

    def onPassedBy(self,x,y):
        if self.isPassedBy(x,y) == True:
            self.frame_color_direct = 8
            gol.set_value("highlight_wp",self.id)

        else:
            self.frame_color_direct = -4

    def onClick(self): #鼠标点击
        self.selected = True
        return self.id
    def render(self,screen):

        if self.selected == True:
            self.color = (self.color[0],self.color[1],self.color[2],200)
            self.frame_color_direct = 0
            self.frame_color = (255,255,255,200)
        else:
            self.color = (self.color[0],self.color[1],self.color[2],100)

        fa = self.frame_color[3]
        if fa > 0:
            pygame.draw.rect(screen,self.frame_color,(self.position,self.rect) , 2,border_radius=3)
        offset = int((self.rect[1]-15)/2)
        pygame.draw.rect(screen,self.color,( (self.position[0] + offset , self.position[1] + offset) ,(15,15)),0,border_radius=3)
        screen.blit(gol.font_Basis.render(self.str_name, True, (200, 200, 200,128)), (self.position[0] + 30 , self.position[1] + offset))


class WpButton(Switch):
    def __init__(self,rect = (20,10) , position = (0,0) , color = (255,255,255,100),str_name = "按钮" ,id = 0):
        super(WpButton,self).__init__(rect,position,color,str_name,id)
        self.selected = False

    def onClick(self): #鼠标点击
        return self.id

    def setPosition(self,pos):
        self.position = pos

    def render(self,screen,color = None):

        bposx = self.position[0] + 0.5*(self.rect[1] - 10)
        bposy = self.position[1] + 0.5*(self.rect[1] - 10)
        bpos = (bposx,bposy)
        pygame.draw.rect(screen,self.color,(bpos,(10,10)),0)
        pygame.draw.rect(screen,self.frame_color,(self.position,self.rect) , 2,border_radius=3)
        screen.blit(gol.font_Basis.render(str(self.str_name), True, (200, 255, 200,255)), (self.position[0] + 45 , self.position[1] +5))


class Button(Switch):
    def __init__(self,rect = (20,10) , position = (0,0) , color = (255,255,255,100),str_name = "按钮" ,id = 0 , img_name = "btn_last.png"):
        super(Button,self).__init__(rect,position,color,str_name,id)
        
        btn_img_file_name = str("src/simulator2D/scripts/imgs/" + img_name)
        #print(btn_img_file_name)
        self.btn_img = pygame.image.load(btn_img_file_name)
        self.btn_img = pygame.transform.scale(self.btn_img,(32,32))
        self.img_alpha = 128
        self.img_alpha_velocity = 0
        self.btn_img.set_alpha(self.img_alpha)
    
    def setIcon(self,btn_img_file_name):
        self.btn_img = pygame.image.load(btn_img_file_name)
        self.btn_img = pygame.transform.scale(self.btn_img,(32,32))
        self.img_alpha = 128
        self.img_alpha_velocity = 0
        self.btn_img.set_alpha(self.img_alpha)


    def onPassedBy(self,x,y):
        if self.isPassedBy(x,y) == True:
            self.img_alpha_velocity = 8
        else:
            self.img_alpha_velocity = -8

    def animationUpdate(self):
        fa = self.img_alpha
        if self.img_alpha_velocity != 0:
            fa = fa + self.img_alpha_velocity
        if fa > 255:
            fa = 255
        if fa < 128:
            fa = 128
        self.img_alpha = fa

    def onClick(self): #鼠标点击
        return self.id

    def render(self,screen,color = None):

        self.btn_img.set_alpha(self.img_alpha)
        screen.blit(self.btn_img, (self.position[0], self.position[1]))
        screen.blit(gol.font_Basis.render(str(self.str_name), True, (230, 255, 230,255)), (self.position[0] + 45 , self.position[1] +5))

