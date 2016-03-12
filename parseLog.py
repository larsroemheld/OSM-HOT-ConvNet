__author__ = 'lars'

import re
import matplotlib.pyplot as plt
import sys
import numpy as np
import math

phases = ['Train', 'Test']
metrics = [(' net output #0: accuracy = (.*)', ' global acc.'),
           (' net output #1: loss = (.*) \(\*', ' loss'),
           (' net output #2: per_class_accuracy = (.*)', ' nolabel acc.'),
           (' net output #3: per_class_accuracy = (.*)', ' building acc.'),
           (' net output #4: per_class_accuracy = (.*)', ' road acc.'),
          (' net output #5: per_class_accuracy = (.*)', ' farm acc.'),
          (' net output #6: per_class_accuracy = (.*)', ' wetland acc.'),
          (' net output #7: per_class_accuracy = (.*)', ' forest acc.'),
           (' net output #8: per_class_accuracy = (.*)', ' water acc.')]

regexes = {}
data = {}
for ph in phases:
    for m in metrics:
        regexes[ph, m] =re.compile(ph + m[0])
        data[ph, m] = []

filename = sys.argv[1]
print "important params: filename {} ".format(filename)

with open(filename, 'r') as f:
    for line in f:
        for ph in phases:
            for m in metrics:
                match = regexes[ph, m].search(line)
                if match is not None:
                    data[ph, m].append(float(match.group(1)))

# Running average smoothing. Must be 1 or even for the average-padding to work.
printiters = 10
testiters = 120
epochiters = 120

N = {}
N['Test']  = 1 #int(math.ceil(epochiters / 2.0 / testiters))
N['Train'] = int(math.ceil(epochiters / 2.0 / printiters))

print "important params: Moving average over iters:"
print N

for ph in phases:
    for m in metrics:
        if N[ph] > 1:
            data[ph, m] = [np.average(data[ph, m][0:N[ph]/2])] * (N[ph]/2-1) + data[ph, m]
            data[ph, m] = data[ph, m] + [np.average(data[ph, m][-N[ph]/2:])] * (N[ph]/2-1)

        data[ph, m] = np.array(data[ph, m])
        data[ph, m] = np.convolve(data[ph, m], np.ones((N[ph],))/N[ph], mode='valid')

# Test phase does not check at iteration 0?
if 'Test' in phases:
    print "Prepending 0 for test metrics, since no testing is performed on iter=0"
    for m in metrics:
        data['Test', m] = [0] + data['Test', m]

x = {}

print "important params: print every {} iters, test every {} iters.".format(printiters, testiters)
x['Train'] = range(0, len(data['Train', metrics[0]]) * printiters, printiters)
x['Test']  = range(0,  len(data['Test', metrics[0]]) * testiters, testiters)


fig = plt.figure()
fig.patch.set_facecolor('white')
nc = len(phases)
nr = len(metrics)

print "important params: {} iters = 1 epoch.".format(epochiters)

for r, m in enumerate(metrics):
    for c, ph in enumerate(phases):
        plt.subplot(nr, nc, r * nc + c + 1)
        plt.gca().set_axis_bgcolor('white')
        plt.plot(x[ph], data[ph, m])

        for xx in range(epochiters, max(x[ph])+1, epochiters):
            plt.axvline(xx, color='r', linestyle='--')
        plt.title(ph + m[1])

plt.show()

