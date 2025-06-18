# 1.
对运行'roslaunch slam_bot slam.launch'以下报错，将world中sim_time设置为0
```
[ERROR] [1741140018.650264, 1517.347000]: Spawn service failed. Exiting.
[ INFO] [1741140019.167699372, 1517.347000000]: Laser Plugin: Using the 'robotNamespace' param: '/'
[ INFO] [1741140019.167972064, 1517.347000000]: Starting Laser Plugin (ns = /)
[ INFO] [1741140019.170042324, 1517.347000000]: Laser Plugin (ns = /)  <tf_prefix_>, set to ""
[urdf_spawner-6] process has died [pid 19209, exit code 1, cmd /opt/ros/noetic/lib/gazebo_ros/spawn_model -urdf -param robot_description -model slam_bot __name:=urdf_spawner __log:=/home/xuqiang/.ros/log/946235e2-f965-11ef-9c78-37ff010c29c5/urdf_spawner-6.log].
log file: /home/xuqiang/.ros/log/946235e2-f965-11ef-9c78-37ff010c29c5/urdf_spawner-6*.log
```