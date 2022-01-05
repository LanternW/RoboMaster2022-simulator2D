# RoboMaster2022-simulator2D

Test in ubuntu 18.04 and ros-melodic 

### Package depend:
python 2.7 、 pygame

```ruby
pip install pygame
```

### Setup workspace

```ruby
mkdir -r catkin_ws/src
cd catkin_ws/src
catkin_init_workspace
```

### Build
```ruby
git clone https://github.com/LanternW/RoboMaster2022-simulator2D.git
cd ..
catkin_make
source devel/setup.bash
```
### Run

Open two terminals , one runs:
```ruby
roscore
```
Another:
```ruby
rosrun simulator2D/main.py
```

### User manual

map unit:               cm
linear velocity unit:   cm/s
angular velocity unit:  rad/s

#### The button ">" is "pause/continue".
#### The button at right of ">" is "reset" , only feasible in pause state.
#### The three buttons at right down only used for mark points.
#### Right click in the map area and drag: measure the distance.
#### all API in "toros.py"
#### Tank's odometry is send as topic "/simulator2D/odometry/($tank_id)" in 100Hz.
#### Buff information is send as topic "/simulator2D/buff_information" in 1Hz.
#### All about ROS interface are in "toros.py"

