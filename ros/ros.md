# 1.ros环境搭建

### 1.ROS noteic版本的对应的utunbu官网
<https://wiki.ros.org/cn/noetic/Installation/Ubuntu>

### 2.在ros镜像源选择一个镜像下载ros应用商店
<https://wiki.ros.org/ROS/Installation/UbuntuMirrors>
![alt text](image.png)

### 3.设置秘钥
```python
sudo apt install curl # if you haven't already installed curl
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
```

### 4.安装
#### 4.1 更新
```python
sudo apt update
```
#### 4.2 安装
```python
sudo apt install ros-noetic-desktop-full
```
### 5.环境设置
```python
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc
```
### 5.依赖安装
```
sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool build-essential
```
上述指令失败后可转为执行以下命令
```
sudo apt-get install python3-pip
sudo pip3 install 6-rosdep
sudo 6-rosdep
sudo rosdep init
rosdep update
```

### 6.目录结构建立
```
sudo apt install git #安装git工具
mkdir catkin_ws
cd catkin_ws
mkdir src
```
### 6.vscode
1.官网下载.deb格式的安装包
2.进入对应位置的终端 ```sudo dpkg -i code_(Tab补全)```

### 6.terminator
sudo apt install terminator
ctrl+alt+t 启动
![alt text](image-1.png)
