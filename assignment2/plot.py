# !/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt

# parameters to modify
filename="processed_ping_log2.txt"
label='Ping Task 5, 0.0001s interval'
xlabel = 'RTT (ms)'
ylabel = 'Cumulative Probability'
title='Cumulative Distribution Function'
fig_name='Ping Task 5, 0.0001s interval.png'
bins=100 #adjust the number of bins to your plot

t = np.loadtxt(filename, delimiter=" ", dtype="float")
#index_array = [i + 1 for i in range(len(t))]

#plt.plot(index_array, t, label=label)  # Plot some data on the (implicit) axes.
#Comment the line above and uncomment the line below to plot a CDF
plt.hist(t, bins, density=True, histtype='step', cumulative=True, label=label)
plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.title(title)
plt.legend()
plt.savefig(fig_name)
plt.show()
