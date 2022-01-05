#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import rospy
import numpy as np
import math
import time
from geometry_msgs.msg import Twist
from geometry_msgs.msg import QuaternionStamped
from gps.msg import BoundingBox
from sensor_msgs.msg import Range
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64

locator = None
pub     = None
err_pub = None
yaw_pub = None

class Locator:

    def __init__(self):
        
        self.l       = 0.46   # 机臂长度
        self.t       = math.atan(self.l / 1.5)

        self.h       = 1.04 # 飞机高度
        self.yaw     = 0    # 偏航角
        self.pitch   = 0     # 俯仰角
        self.roll    = 0     # 横滚角

        self.bmp_width = 640
        self.bmp_height = 480


        # 内参矩阵
        #self.K       = np.array([[371.34 ,0 ,313.89],[0,369.52, 246.59],[0,0,1]])
        self.K       = np.array([[370.5 ,0 ,320],[0,370.5, 240],[0,0,1]])
        ct           = math.cos(self.t)
        st           = math.sin(self.t)
        sqrt3        = math.sqrt(3)
        rotz_mpi1_6   = np.mat([[sqrt3/2 , 0.5 , 0] ,[-0.5, sqrt3/2,0] ,[0,0,1]])
        rotx_pi_t    = np.mat([[1,0,0] ,[0,-ct,-st] ,[0,st,-ct]])
    
        self.Rdc     = np.dot(rotz_mpi1_6 , rotx_pi_t)

        print("rotz_pi1_6:")
        print(rotz_mpi1_6)
        print("rotx_pi_t:")
        print(rotx_pi_t)
        print("Rdc:")
        print(self.Rdc)

        self.Pdcorg  = np.array([[0.2733] , [0.37337] ,[0]])
        self.Rwd     = np.mat(np.eye(3,3)) # Z-X-Y euler angle
        self.ct = ct

    
    def V2WP(self,V):

        #dpixel_x = V[0] - 0.5*self.bmp_width
        dpixel_y = V[1] - 0.5*self.bmp_height
        #dpixel_dis = math.sqrt(dpixel_x*dpixel_x + dpixel_y*dpixel_y)
        dpixel_dis = dpixel_y
        alpha = math.atan(dpixel_dis/371)

        z = self.h * math.cos(alpha) / math.cos(self.t + alpha)
        #z = self.h / self.ct
        # 中间过程
        K_inv = np.linalg.inv(self.K)
        Pc = np.dot(K_inv , (z*V) )

        Pd = np.dot(self.Rdc , Pc) + self.Pdcorg
        Pw = np.dot(self.Rwd , Pd)

        return Pw  
        # Pw再加飞机的Base坐标得到地雷相对Base坐标

def Q2R(x,y,z,w):

    R = np.array([
        [1 - 2*y*y - 2*z*z  ,   2*x*y - 2*z*w    ,  2*x*z + 2*y*w],
        [   2*x*y + 2*z*w   , 1 - 2*x*x - 2*z*z  ,  2*y*z - 2*x*w],
        [   2*x*z - 2*y*w   , 2*y*z + 2*x*w      ,  1 - 2*x*x - 2*y*y ],
    ])
    return R


def findLandmine(msg):
    location = Twist()

    if msg.width < 2 and msg.height < 2:
        return

    vx = msg.x + 0.5 * msg.width
    vy = msg.y + 0.5 * msg.height

    #vx = vx * 1920 / 640 
    #vy = vy * 1080 / 480

    #V = np.array([[msg.linear.x, msg.linear.y , 1]]).T  # V = [x,y,1]'
    V = np.array([[vx, vy , 1]]).T
    Pw = locator.V2WP(V)
    
    location.linear.x = Pw[0]
    location.linear.y = Pw[1]
    location.angular.z = locator.yaw
    location.linear.z = locator.h
    pub.publish(location)

    #errPub(-Pw[1] , Pw[0])

    print("locate a landmine")

def imuLisener(msg):
    global locator,yaw_pub
    x = msg.quaternion.x
    y = msg.quaternion.y
    z = msg.quaternion.z
    w = msg.quaternion.w
    locator.Rwd = Q2R(x,y,z,w)

    siny_cosp = 2.0*(w*z + x*y)
    cosy_cosp = 1.0 - 2.0*(y*y + z*z)
    yaw = math.atan2(siny_cosp , cosy_cosp)
    locator.yaw = yaw
    y = Float64(yaw)
    yaw_pub.publish(y)

    print("yaw update to: ",y)

    


def changeHeight(msg):
    global locator
    locator.h = msg.range + 0.05

def fortest():
    global locator,pub


    locator.Rwd = Q2R(0,0,-0.707,0.707)
    location = Twist()
    for x in range(0,640,20):
        for y in range(0,480,20):
            V = np.array([[x,y,1]]).T
            Pw = locator.V2WP(V)
            location.linear.x = Pw[0]
            location.linear.y = Pw[1]
            pub.publish(location)

            
            errPub(-Pw[1] , Pw[0])
            print("test a landmine")
            time.sleep(0.01)

def errPub(dx,dy):
    global err_pub

    err = Odometry()
    err.pose.pose.position.x = dx
    err.pose.pose.position.y = dy

    err_pub.publish(err)
    pass          


def lct_init():
    global locator,pub, err_pub, yaw_pub
    locator = Locator()
    rospy.init_node("locator",anonymous=True)
    pub = rospy.Publisher("/landmine_position", Twist ,queue_size=10)
    err_pub = rospy.Publisher("/error", Odometry , queue_size=10 )
    yaw_pub = rospy.Publisher("/yaw" , Float64 ,queue_size=10)
    rospy.Subscriber("/tld_tracked_object", BoundingBox ,findLandmine)
    rospy.Subscriber("/dji_sdk/attitude", QuaternionStamped , imuLisener)
    rospy.Subscriber("/tfmini_ros_node/TFmini", Range , changeHeight)

    print("landmine locator start")
    #fortest()


if __name__ == "__main__":
    lct_init()
    rospy.spin()


