import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

"""
Create a image of the 3d lorenz attractor equation 
"""
# math stuff

N = 10000
x = np.zeros(N)
y = np.zeros(N)
z = np.zeros(N)

rho, beta, sigma = (28, 8 / 3, 14)
x[0], y[0], z[0] = (.2, 2, 0)

dt = .01  # time step between every index (frame)

# setting up figure
plt.style.use('dark_background')

fig = plt.figure(figsize = (8, 8))
ax = fig.add_subplot(111, projection = '3d')

color_period_freq = 1000 # color goes from dark to light to dark in blank inexes
cmhold = abs(np.sin(np.linspace(0, N / color_period_freq, N)))# color map
colormap = cm.RdBu(cmhold)

for i in range(N - 1):
    x[i+1] = x[i] + sigma * (y[i] - x[i]) * dt
    y[i+1] = y[i] + (x[i] * (rho - z[i]) - y[i]) * dt
    z[i+1] = z[i] + (x[i] * y[i] - beta * z[i]) * dt

ax.scatter(x, y, z, c = colormap, s = .2)
ax.grid(False)
ax.axis('off')

plt.show()


