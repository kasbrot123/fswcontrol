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



"""
Source:
https://datascience.stackexchange.com/questions/102986/how-can-i-plot-a-3d-antenna-radiation-pattern-in-python

Interpolates the measurement data (doubles it)

"""

def interp_array(N1):  # add interpolated rows and columns to array
    N2 = np.empty([int(N1.shape[0]), int(2*N1.shape[1] - 1)])  # insert interpolated columns
    N2[:, 0] = N1[:, 0]  # original column
    for k in range(N1.shape[1] - 1):  # loop through columns
        N2[:, 2*k+1] = np.mean(N1[:, [k, k + 1]], axis=1)  # interpolated column
        N2[:, 2*k+2] = N1[:, k+1]  # original column
    N3 = np.empty([int(2*N2.shape[0]-1), int(N2.shape[1])])  # insert interpolated columns
    N3[0] = N2[0]  # original row
    for k in range(N2.shape[0] - 1):  # loop through rows
        N3[2*k+1] = np.mean(N2[[k, k + 1]], axis=0)  # interpolated row
        N3[2*k+2] = N2[k+1]  # original row
    return N3


def plot3d(path, interp_factor=0,sphere=True):

    files = glob.glob(path+os.sep+'*.txt')
    POINTS = []


    for file in files:
        split = file.replace('.txt','').split('_')
        az = float(split[-2])
        el = float(split[-1])

        trace = np.loadtxt(file, comments='#')

        r = trace.max()
        # for testing
        # r = np.cos(az/180*np.pi)*np.sin(el/180*np.pi) # dipole 
        # r = np.cos(az/180*np.pi)*np.sin(el/180*np.pi) # whale

        # POINTS.append((az, el, r))
        # -az -> angle of robot is in the other direction
        POINTS.append((el, -az, r))



    # AZ, EL, R = zip(*sorted(POINTS))
    EL, AZ, R = zip(*sorted(POINTS))
    # AZ = [i[0] for i in POINTS]
    # EL = [i[1] for i in POINTS]
    # R = [i[2] for i in POINTS]

    a = AZ.count(AZ[0])
    b = len(AZ)//a
    AZ = np.array(AZ).reshape(a, b)
    EL = np.array(EL).reshape(a, b)
    R = np.array(R).reshape(a, b)
    Rmax = R.max()
    R = R - R.min()#*10
    # R = 10**(R/20)
    # R = R/R.max()


    if sphere:
        Radius = 1
    else:
        Radius = R
    XX = Radius*np.cos(EL*np.pi/180)*np.cos(AZ*np.pi/180)
    YY = Radius*np.cos(EL*np.pi/180)*np.sin(AZ*np.pi/180)
    ZZ = Radius*np.sin(EL*np.pi/180)

    # interp_factor = 2
    for counter in range(interp_factor):
        AZ = interp_array(AZ)
        EL = interp_array(EL)

        XX = interp_array(XX)
        YY = interp_array(YY)
        ZZ = interp_array(ZZ)
        R = interp_array(R)


    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    # color for surface plot
    norm = colors.Normalize(R.min(), R.max())
    m = cm.ScalarMappable(norm=norm, cmap='jet')
    m.set_array([])
    fcolors = m.to_rgba(R)

    surf = ax.plot_surface(XX, YY, ZZ, facecolors=fcolors, rstride=1, cstride=1, antialiased=1,shade=0)
    # surf = ax.scatter(XX, YY, ZZ, c=fcolors[:,:,2])
    # surf = ax.scatter(XX, YY, ZZ, c=(R-R.min()*0.9)/(R.max()-R.min()), s=100)


    ax.view_init(azim=350, elev=30)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    # ax.set_aspect('equal')
    fig.colorbar(m, shrink=0.5, aspect=5)
    ax.set_title('Max Amp.: {:0.1f} dB'.format(Rmax))

    # if path == '../2024_02_05_Linsen_Michi/run03':
    #     AZ = AZ - 2
    #     EL = EL - 2
    #
    # fig, ax = plt.subplots()
    # ax.pcolor(AZ, EL, R, cmap='jet')
    # ax.set_xlabel('Azimuth angle in °')
    # ax.set_ylabel('Elevation angle in °')
    # ax.set_title('Max Amp.: {:0.1f} dBm'.format(Rmax))
    # ax.set_aspect('equal')
    # 
    #
    # if path == '../2024_02_05_Linsen_Michi/run03':
    #     plt.xlim([-6, 6])
    #     plt.ylim([-6, 6])


    # return AZ, EL, R
    return fig






def plot2d(path, interp_factor=0,sphere=True):

    files = glob.glob(path+os.sep+'*.txt')
    POINTS = []


    for file in files:
        split = file.replace('.txt','').split('_')
        az = float(split[-2])
        el = float(split[-1])

        trace = np.loadtxt(file, comments='#')

        r = trace.max()
        # for testing
        # r = np.cos(az/180*np.pi)*np.sin(el/180*np.pi) # dipole 
        # r = np.cos(az/180*np.pi)*np.sin(el/180*np.pi) # whale

        # POINTS.append((az, el, r))
        # -az -> angle of robot is in the other direction
        POINTS.append((el, -az, r))



    # AZ, EL, R = zip(*sorted(POINTS))
    EL, AZ, R = zip(*sorted(POINTS))

    # a = AZ.count(AZ[0])
    # b = len(AZ)//a
    # AZ = np.array(AZ).reshape(a, b)
    # EL = np.array(EL).reshape(a, b)
    # R = np.array(R).reshape(a, b)
    # Rmax = R.max()
    # R = R - R.min()#*10

    # R = 10**(R/20)
    # R = R/R.max()


    # fig = plt.figure()
    # plt.plot(AZ, R, 'o--')
    # plt.xlabel('Azimuth in °')
    # plt.ylabel('Amplitude in dB')

    return list(AZ), list(R)


FACTOR = 0

if __name__ == '__main__':

    path_measurement = './folder'
    plot3d(path_measurement, interp_factor=2, sphere=True)
    plt.show()


