import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":

    fname = sys.argv[1]

    with open(fname, "r") as f:
        lines = f.readlines()

    lines = [l.strip("#") for l in lines if l.startswith("##")]
    lines = [l.split(",") for l in lines]
    lines = [[float(l[0]),float(l[1]),float(l[2])] for l in lines]
    pos_infos= np.array(lines)
    times       = pos_infos[:,0]
    positions_x = pos_infos[:,1]/32
    positions_y = pos_infos[:,2]/32

    plt.figure()
    plt.plot(times,positions_x, times,positions_y)

    d_times = times[1:] - times[:-1]
    d_positions_x = positions_x[1:] - positions_x[:-1]
    d_positions_x = d_positions_x/d_times
    d_positions_y = positions_y[1:] - positions_y[:-1]
    d_positions_y = d_positions_y/d_times

    plt.figure()
    plt.plot(times[1:],d_positions_x, times[1:],d_positions_y)

    plt.show()
