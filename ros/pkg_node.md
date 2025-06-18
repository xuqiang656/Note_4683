# 1.Node节点建立
```
catkin_create_pkg ssr_pkg(包名) rospy roscpp std_msgs

add_executable(chao_node src/chao_node.cpp) #添加节点后在cmakelist增加代码，其中chao_node 为节点名， 后面的是路径，之后ctrl+shift+b 编译，或者在catkin_ws目录下使用catkin_make进行编译

#节点运行（c++）
roscore 
rosrun  ssr_pkg chao_node #包名，节点名

#节点运行python，在建立目录结构时执行一次编译就可以了，后面运行节点无需编译
在ssr_pkg下新建scripts文件夹，新建chao_node.py，编写代码文件
roscore 
rosrun ssr_pkg chao_node.py
```
# 2.launch文件启动多节点
在包内新建launch文件夹，在文件夹内新建.lauch文件
```
#实例
<launch>
    <node pkg='ssr_pkg' type='chao_node' name='chao_node'/>
    <node pkg='ssr_pkg' type='chao_node' name='chao_node'/>
    <node pkg='ssr_pkg' type='chao_node' name='chao_node'/>
</launch>

#运行节点
roslaunch ssr_pkg ceshi.launch

#launch文件
launch-prefix='gnome-terminal -e' #将该节点在一个独立的终端进行运行
output = 'screen' #将日志信息显示在终端屏幕上
rqt_graph #查看订阅者与发布者节点网络
```
