# 代码中导入xodr地图

```python
xodr_path = str(r'your xodr path')
with open(xodr_path, encoding='utf-8') as od_file:
    data = od_file.read()
    world = client.generate_opendrive_world(data)
world = client.get_world()
```