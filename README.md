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
