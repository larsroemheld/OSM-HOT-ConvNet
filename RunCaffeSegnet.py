# Modified version of lenet_initial.py

import os
import sys
import caffe
from pylab import *

from caffe import layers as L
from caffe import params as P

# SETTING CAFFE
caffe.set_device(0)
caffe.set_mode_gpu()
solver = caffe.SGDSolver('/home/ubuntu/segnet/models/segnet/segnet_basic_solver.prototxt')
# TESTING FORWARD
solver.net.forward()  # train net
solver.test_nets[0].forward()  # test net (there can be more than one)

niter = 10000
test_interval = 250

# the main solver loop
for it in range(niter):
    solver.step(1)  # SGD by Caffe
    
    # store the train loss
    print solver.net.blobs['loss'].data
    
    # store the output on the first test batch
    # (start the forward pass at conv1 to avoid loading new data)
    solver.test_nets[0].forward(start='conv1')
    
    # run a full test every so often
    # (Caffe can also do this for us and write to a log, but we show here
    #  how to do it directly in Python, where more complicated things are easier.)
    if it % test_interval == 0:
        print 'Iteration', it, 'testing...'
        correct = 0
        for test_it in range(100):
            solver.test_nets[0].forward()
            #print 'Prediction'
            #print solver.test_nets[0].blobs['ip2'].data.argmax(1)
            #print 'label'
            #print solver.test_nets[0].blobs['label'].data
            correct += sum(solver.test_nets[0].blobs['conv_classifier'].data.argmax(1)
                           == solver.test_nets[0].blobs['label'].data)
        print 'Prediction'
        print solver.test_nets[0].blobs['conv_classifier'].data.argmax(1)
        print 'label'
        print solver.test_nets[0].blobs['label'].data
        # print "Loss of current test batch:"+str(solver.test_nets[0].blobs['loss'].data)
        # print correct /float(2400)
        # print test_acc