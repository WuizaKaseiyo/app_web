import numpy as np
import matplotlib.pyplot as plt

# 设置画布背景为暗色风格
plt.style.use('dark_background')

# 创建螺旋线数据
theta = np.linspace(0, 8 * np.pi, 1000)  # 角度
r = np.linspace(0, 1, 1000)              # 半径
x = r * np.cos(theta)
y = r * np.sin(theta)

# 创建颜色渐变
colors = theta

# 绘图
fig, ax = plt.subplots(figsize=(8, 8))
scatter = ax.scatter(x, y, c=colors, cmap='plasma', s=5)

# 添加标题
ax.set_title("Pythonic Spiral", fontsize=18, weight='bold')

# 去掉坐标轴
ax.axis('off')

# 显示图形
plt.show()
