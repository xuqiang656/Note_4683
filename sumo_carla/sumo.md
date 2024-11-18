# sumo尝试

## 1.使用trip文件生成车流

参数 | 意义                            | 参数  | 意义 
:--------: | :--------------:        | :-------: | :-------:
id |  trip编号                    |depart  |  出发时间 
from    |  出发边                    |to|  到达边
文件名 |  *.trip.xml              

中间道路自动补全，每个trip编号分配一辆车
```xml 
<routes>
    <trip id="trip0" depart="0" from="1fi" to="2o"/>
    <trip id="trip1" depart="10" from="1fi" to="3o"/>
    <trip id="trip2" depart="20" from="1fi" to="4o"/>
</routes> 
```
最后使用`duarouter --route-files=hello.trip.xml --net-file=../hello.net.xml --output-file=hello.rou.xml`转换为rou.xml文件

## 2.使用flow文件生成车流

参数 | 意义                            | 参数  | 意义 
:--------: | :--------------:        | :-------: | :-------:
begin  |  出发时间                     |probability  |  每秒发送一辆车的概率 
end    |  消失时间                     |number |  给定的总车辆数
vehsPerHour |  每小时车辆数              
period  |  该时间段内插入等间隔车辆

```xml
<routes>
    <!-- 定义两个车辆类型 -->
    <vType id="type1" accel="0.8" decel="4.5" sigma="0.5" length="5" maxSpeed="70"/>
    <vType id="type2" accel="1.2" decel="4.5" sigma="0.5" length="7" maxSpeed="120"/>
    <!-- 定义 flow, 每小时 1000 辆车 -->
    <flow id="flow1" color="1,1,0"  begin="0" end= "7200" vehsPerHour="1000" type='type1'>
        <route edges="3fi 3si 4o"/>
    </flow>
    <!-- 定义 flow, 每个 5 秒有车 -->
    <flow id="flow2" color="0,1,1"  begin="0" end="7200" period="5" type="type2" from="1si" to="2o"/>
    <routes>
</routes>
```
**利用number和时间段定义**
```xml
<routes>
    <!-- 第一个时间段 -->
    <interval begin="0" end="100">
        <flow id="00" from="1si" to="2o" number="50"/>
    </interval>
    <!-- 第二个时间段 -->
    <interval begin="100" end="200">
        <flow id="10" from="1si" to="3o" number="50"/>
        <flow id="11" from="1si" to="4o" number="50"/>
    </interval>
</routes>
```
**flow文件还可以写为**`<flow id="f2" begin="0" end="100" number="23" from="beg" to="end" via="e1 e23 e7"/>`

**文件转换为rou.xml**`duarouter --route-files=hello.trip.xml --net-file=../hello.net.xml --output-file=hello.rou.xml --human-readable-time --randomize-flows true --departlane random --seed 30`
参数 | 意义                            | 参数  | 意义 
:--------: | :--------------:        | :-------: | :-------:
--human-readable-time  |  时间转换为day:hour:minute:second         |--departlane |  起始的车道随机
--randomize-flows    |  车辆 depart time 随机                     |--seed |  随机种子


## 3.randomTrips.py生成随机车流
`python randomTrips.py -n input_net.net.xml`
参数 | 意义                            | 参数  | 意义 
:--------: | :--------------:        | :-------: | :-------:
-n  |  给定路网                    |-e  |  结束时间 
-b    |  开始时间                     |-p |  每秒生成车辆数
--fringe-factor<float> |  车辆从边缘处产生或消失的倍率    |  -L| 按照车道数分配比重          
-l  |  按照边的长度分配生成比重      

## 4.设置车辆在边的某处停下来
```xml
<routes>
    路线0设置车辆在行驶到middle_0的车道为50m处停止，持续20s
    <route id="route0" edges="beg middle end rend">
        <stop lane="middle_0" endPos="50" duration="20"/>
    </route>
    
    车辆v0内置属性，使得车辆在end_0车道的10m处停止，直到仿真秒到达50
    <vehicle id="v0" route="route0" depart="0">
        <stop lane="end_0" endPos="10" until="50"/>
    </vehicle>
   
   以13.89米/秒的速度通过end_1的10m处
    <vehicle id="v1" route="route0" depart="90">
        <stop lane="end_1" endPos="10" speed="13.89"/>
    </vehicle>
</routes>
```

## 5.vehicle Types

```xml
<routes>
    <vType id="type1" length="5" maxSpeed="70" carFollowModel="Krauss" accel="2.6" decel="4.5" sigma="0.5"/>
</routes>
```
可设置的参数，挑选常见和特殊的参数介绍
参数 | 意义                            | 参数  | 意义 
:--------: | :--------------:        | :-------: | :-------:
sigma[0,1]  |  驾驶不完美程度                    |minGap  |  跟车距离 
speedFactor=normc(mean,deviation,lowerCutOff,upperCutOff)   |  速度分布                    |speedFactor='1' |  车辆速度均值（车道限速百分比）
speedDev  |  速度的偏差                    |vClass  |  车辆类型
emissionClass|  排放类别                    |vClass  |  车辆类型
laneChangeModel|  车道变换模型                   |carFollowModel |  车辆跟随模型
boardingDuration|  行人登车时间                   |carFollowModel |  车辆跟随模型





