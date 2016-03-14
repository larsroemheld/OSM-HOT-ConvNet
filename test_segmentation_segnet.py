'''
Adapted from test_segmentation_camvid.py (from SegNet): creates HOT-OSM-styled segmentation results.

Modified by Lars Roemheld, roemheld@stanford.edu
'''

import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import os.path
import json
import scipy
import argparse
import math
import pylab
from sklearn.preprocessing import normalize
caffe_root = '/home/ubuntu/segnet/' 			# Change this to the absolute directoy to SegNet Caffe
import sys
sys.path.insert(0, caffe_root + 'python')

import caffe

# Import arguments
parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, required=True)
parser.add_argument('--weights', type=str, required=True)
parser.add_argument('--iter', type=int, required=True)
args = parser.parse_args()

caffe.set_mode_gpu()

net = caffe.Net(args.model,
                args.weights,
                caffe.TEST)


for i in range(0, args.iter):

	net.forward()

	image = net.blobs['data'].data
	label = net.blobs['label'].data
	predicted = net.blobs['conv_classifier'].data
	image = np.squeeze(image[0,:,:,:])
	output = np.squeeze(predicted[0,:,:,:])
	print "if shapes are a problem: phase=test must use batchsize 1!"
	print "net output shape:", output.shape
	ind = np.argmax(output, axis=0)
	print "prediction shape:", ind.shape
	
	r = ind.copy()
	g = ind.copy()
	b = ind.copy()
	r_gt = label.copy()
	g_gt = label.copy()
	b_gt = label.copy()
	print "r_gt shape", r_gt.shape
	print "label.shape:", label.shape

	default = (0, 0, 0)
	building = (220, 214, 214)
	road = (210, 147, 142)
	farm = (221, 220, 189)
	wetland = (226, 232, 225)
	forrest = (178, 194, 157)
	river = (144, 204, 203)

	label_colours = np.array([default, building, road, farm, wetland, forrest, river])
	if np.sum(ind>6) != 0: print "labelling ERROR!"
	
	for l in range(0,6):
		r[ind==l] = label_colours[l,0]
		g[ind==l] = label_colours[l,1]
		b[ind==l] = label_colours[l,2]
		r_gt[label==l] = label_colours[l,0]
		g_gt[label==l] = label_colours[l,1]
		b_gt[label==l] = label_colours[l,2]
	
	print "later r_gt shape:", r_gt.shape
	
	rgb = np.zeros((ind.shape[0], ind.shape[1], 3))
	rgb[:,:,0] = r/255.0
	rgb[:,:,1] = g/255.0
	rgb[:,:,2] = b/255.0
	rgb_gt = np.zeros((ind.shape[0], ind.shape[1], 3))
	rgb_gt[:,:,0] = r_gt/255.0
	rgb_gt[:,:,1] = g_gt/255.0
	rgb_gt[:,:,2] = b_gt/255.0

	image = image/255.0

	image = np.transpose(image, (1,2,0))
	output = np.transpose(output, (1,2,0))
	image = image[:,:,(2,1,0)]


	#scipy.misc.toimage(rgb, cmin=0.0, cmax=255).save(IMAGE_FILE+'_segnet.png')

	plt.figure()
	plt.imshow(image,vmin=0, vmax=1)
	plt.savefig('./{}satellite.png'.format(i))
	plt.figure()
	plt.imshow(rgb_gt,vmin=0, vmax=1)
	plt.savefig('./{}ground_truth.png'.format(i))
	plt.figure()
	plt.imshow(rgb,vmin=0, vmax=1)
	plt.savefig('./{}prediction.png'.format(i))


print 'Success!'

