# 太极example-volume_rendering
## 背景简介
本文实现了一个简单的医学图像体绘制，实现了最大密度投影和最小密度投影两种算法．可以分别从三个方向上进行投影计算．后续可以加入混合模式，加入传递函数等内容

## 整体结构（Optional）
```
├── data
│   └── FullHead.mhd
│   └── FullHead.raw.gz
├── README.md
├── volume_rendering.py
└── requirements.txt
```

## 运行方式
运行环境：

```
[Taichi] version 1.1.3, win, python 3.8.10
```

确保`data` 和`volume_rendering.py` 在相同的路径下，直接运行:  `python3 volume_rendering.py`


