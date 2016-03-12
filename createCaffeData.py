'''
Takes in image and labels json as produced by getTaskData and produces one large .txt file in the Caffe ImageData format:
filename label

Lars Roemheld, roemheld@stanford.edu
'''
__author__ = 'Lars Roemheld'
import os, json

nl = 0
print "starting to read files"
with open('data_full.txt', 'w') as newF:
    for fn in os.listdir('.'):
        if len(fn) > 11 and fn[-11:] == 'labels.json':
            print "now in file: " + fn + " written lines: " + str(nl)
            with open(fn, 'r') as f:
                samples = json.load(f)
                for s in samples:
                    for k in s.keys():
                        label = "building" if s[k] else "nobuilding"
                        newF.write(k + " " + label + "\n")
                        nl += 1
