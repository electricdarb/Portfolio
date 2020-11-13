import matplotlib
import matplotlib.animation
from matplotlib.animation import FuncAnimation as fa
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot as plt
import random


# declarig initial values
frames = 1000
dt = .02  # dt is independent of animation time

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')
ax.set_title("Lorenz Attractor")
lim = 20
ax.set_xlim(-lim,lim)
ax.set_ylim(-lim,lim)
ax.set_zlim(-lim,lim)

rho, beta, sigma = (14., 8 / 3, 10.)
x, y,z = (1, 1, 1)
color = (.3, .3, .3)

def sequencial_color(prev, step = 5):
    # i could re design this function to better fit mpl's [0:1] color range, however i am estatic to use a lambda function
    rand1 = random.randint(round(-step/3), step)
    rand2 = random.randint(round(-step/3), step)
    rand3 = random.randint(round(-step/3), step)

    r, b, g = prev

    cast = lambda a : int(a*255)
    r = cast(r)
    b = cast(b)
    g = cast(g)

    if r < 220 - step and r > step:
        r+= rand1
    elif b < 220 - step and b > step:
        b+= rand2
    elif g < 220- step and g > step:
        g+= rand3
    else:
        r, b, g = (30, 30, 30)

    return r/255, b/255, g/255

def animation(i):
    global rho, beta, sigma, x, y, z, color
    dx = sigma * (y - x) * dt
    dy = (x * (rho - z) - y) * dt
    dz = (x * y - beta * z) * dt

    color = sequencial_color(color)

    ax.plot([x, x + dx], [y, y + dy], [z, z + dz], c = color)

    x += dx
    y += dy
    z += dz

    return None

ani = fa(fig, animation, interval=10, save_count=100)

plt.show()
