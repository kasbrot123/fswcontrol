# -*- coding: utf-8 -*-
"""
Script: "3d_visualization.py"

Author(s): Michael Toefferl
Created: 2023-10-19 12:30


Script to visualize the radiation characteristics measured with the Rohde & 
Schwarz FSW measurement device. 


"""


import os
import glob
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import colors


# path of measurement files
path = './testing2'



files = glob.glob(path+os.sep+'*.txt')
POINTS = []


for file in files:
    split = file.replace('.txt','').split('_')
    az = float(split[-2])
    el = float(split[-1])

    trace = np.loadtxt(file, comments='#')

    r = trace.max()

    POINTS.append((az, el, r))



AZ, EL, R = zip(*sorted(POINTS))
a = AZ.count(AZ[0])
b = len(AZ)//a
AZ = np.array(AZ).reshape(a, b)
EL = np.array(EL).reshape(a, b)
R = np.array(R).reshape(a, b)


XX = R*np.cos(EL*np.pi/180)*np.cos(AZ*np.pi/180)
YY = R*np.cos(EL*np.pi/180)*np.sin(AZ*np.pi/180)
ZZ = R*np.sin(EL*np.pi/180)



fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

# color for surface plot
norm = colors.Normalize(R.min(), R.max())
m = cm.ScalarMappable(norm=norm, cmap='jet')
m.set_array([])
fcolors = m.to_rgba(R)

surf = ax.plot_surface(XX, YY, ZZ, facecolors=fcolors, rstride=1, cstride=1, shade=0)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_aspect('equal')
fig.colorbar(m, shrink=0.5, aspect=5)

plt.show()


