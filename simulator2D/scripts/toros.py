# -*- coding: UTF-8 -*-

import rospy
from constants import *
import gol
import math

#from gps.msg import Gpsinfo
from simulator2D.msg import Buff
from nav_msgs.msg import Odometry
from visualization_msgs.msg import Marker

current_map = None

tank_odom_publisher = [None,None,None,None]
buff_publisher = None



def eular2Quaternion(z):
    qx = 0
    qy = 0
    qz = math.sin(z / 2)
    qw = math.cos(z / 2)
    return (qx,qy,qz,qw)

def updateHeat(e):
    current_map.updateHeat()

# return  pos, vel, basis_yaw, bat_yaw, basis_yawdot, bat_yawdot
def getTankState(tank_id):
    return current_map.tank_manager.getTankState(tank_id)

# return pos, vel,  basis_yaw,  basis_yawdot
def getTankOdometry(tank_id):
    return current_map.tank_manager.getTankOdometry(tank_id)

# 线速度单位：cm/s  角速度单位 rad/s
def setTankVelocity(tank_id , linear_vel, basis_yaw_dot, bat_yaw_dot):
    current_map.tank_manager.setTankVelocity(tank_id, linear_vel, basis_yaw_dot, bat_yaw_dot)

# pos单位：cm  角度单位 rad
def setTankPose(self, id ,pos ,basis_yaw, bat_yaw):
    current_map.tank_manager.setTankPose(self, id ,pos ,basis_yaw, bat_yaw)

# trajectory is a optimal list , just for visualization
def setTankTraj(tank_id, trajectory):
    current_map.tank_manager.setTankTraj(tank_id, trajectory)

def rvizAxis2simulatorAxis( cor ):
    sim_cor = (-cor[1]*100 , -cor[0]*100)
    return sim_cor

def simulatorAxis2rvizAxis( cor ):
    rviz_cor = (-cor[1]*0.01 , -cor[0]*0.01 )
    return rviz_cor

def simulatorR2rvizR( rz ):
    return rz - 1.570796327

def trajCallback(traj_marker):
    traj = []
    for point in traj_marker.points:
        traj.append( rvizAxis2simulatorAxis( (point.x , point.y) ))
    
    setTankTraj(1, traj)

def publishOdometry(e):
    global tank_odom_publisher
    odom = Odometry()
    odom.header.frame_id = "world"
    odom.header.stamp = rospy.Time.now()
    for i in range(1,5):
        pos, vel, basis_yaw, basis_yawd = getTankOdometry(i)

        pos = simulatorAxis2rvizAxis( pos )
        vel = simulatorAxis2rvizAxis( vel )
        basis_yaw = simulatorR2rvizR(basis_yaw)
        q   = eular2Quaternion(basis_yaw)
        odom.pose.pose.position.x     = pos[0]
        odom.pose.pose.position.y     = pos[1]
        odom.twist.twist.linear.x     = vel[0]
        odom.twist.twist.linear.y     = vel[1]
        odom.twist.twist.angular.z    = basis_yawd

        odom.pose.pose.orientation.x  = q[0]
        odom.pose.pose.orientation.y  = q[1]
        odom.pose.pose.orientation.z  = q[2]
        odom.pose.pose.orientation.w  = q[3]

        tank_odom_publisher[i-1].publish(odom)

def publishBuff(e):

    global buff_publisher
    buff_info = Buff()
    buff_info.buff1 = current_map.functionarea_manager.getAreaTypeById(1)
    buff_info.buff2 = current_map.functionarea_manager.getAreaTypeById(2)
    buff_info.buff3 = current_map.functionarea_manager.getAreaTypeById(3)
    buff_info.buff4 = current_map.functionarea_manager.getAreaTypeById(4)
    buff_info.buff5 = current_map.functionarea_manager.getAreaTypeById(5)
    buff_info.buff6 = current_map.functionarea_manager.getAreaTypeById(6)
    buff_publisher.publish(buff_info)


def initRosPart():

    global current_map, tank_odom_publisher, buff_publisher
    current_map = gol.get_value("current_map")
    rospy.init_node("simulator2D_ros",anonymous=True)

    setTankVelocity(1,(0,0),0,1)
    setTankVelocity(2,(0,0),0,1)
    setTankVelocity(3,(0,0),0,1)
    setTankVelocity(4,(0,0),0,1)

    for i in range(0,4):
        tank_odom_publisher[i] = rospy.Publisher(str("simulator2D/odometry/%d" % (i+1)), Odometry, queue_size=1)
    
    buff_publisher = rospy.Publisher("simulator2D/buff_information", Buff, queue_size=1)

    HeatTimer       = rospy.Timer(rospy.Duration(0.1), updateHeat)
    OdometryTimer   = rospy.Timer(rospy.Duration(0.01), publishOdometry)  # 100 Hz
    buffTimer       = rospy.Timer(rospy.Duration(1), publishBuff)         # 1 Hz
    rospy.Subscriber("/car_planner_node/optimal_list", Marker , trajCallback)

    print("simulator2D start")
    #rospy.spin()






