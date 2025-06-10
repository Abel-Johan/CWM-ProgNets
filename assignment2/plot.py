# !/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt

# parameters to modify
filename="processed_iperf3.log"
label='iPerf3 Task 1'
xlabel = 'Time/Interval (s)'
ylabel = 'Bandwidth'
title='Bandwidth at Each Interval'
fig_name='iPerf3 Task 1'
bins=10 #adjust the number of bins to your plot

t = np.loadtxt(filename, delimiter=" ", dtype="float")
#index_array = [i + 1 for i in range(len(t))]
#plt.plot(np.log10([100, 1000, 100000]), [0, 0, 0], '-rx')
#plt.plot(index_array, t, label=label)  # Plot some data on the (implicit) axes.
plt.stairs(t[:, 1], range(len(t[:, 1]) + 1), baseline = 880) # Plot bandwidth at each interval

#Comment the line above and uncomment the line below to plot a CDF
#plt.hist(t[:,1], bins, density=True, histtype='step', cumulative=True, label=label)
plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.title(title)
plt.legend()
plt.savefig(fig_name)
plt.show()

# Original code for reference
## !/usr/bin/python3
#import numpy as np
#import matplotlib.pyplot as plt

## parameters to modify
#filename="test.data"
#label='label'
#xlabel = 'xlabel'
#ylabel = 'ylabel'
#title='Simple plot'
#fig_name='test.png'
#bins=100 #adjust the number of bins to your plot


#t = np.loadtxt(filename, delimiter=" ", dtype="float")

#plt.plot(t[:,0], t[:,1], label=label)  # Plot some data on the (implicit) axes.
##Comment the line above and uncomment the line below to plot a CDF
##plt.hist(t[:,1], bins, density=True, histtype='step', cumulative=True, label=label)
#plt.xlabel(xlabel)
#plt.ylabel(ylabel)
#plt.title(title)
#plt.legend()
#plt.savefig(fig_name)
#plt.show()
