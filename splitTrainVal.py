'''
Given a caffe-formatted ImageData file, randomly split the file into train, val, test parts

Lars Roemheld, roemheld@stanford.edu
'''
__author__ = 'Lars Roemheld'

import random

SHARE_VAL = 0.1
SHARE_TEST = 0.05
SHARE_TRAIN = 1 - SHARE_TEST - SHARE_VAL

with open('data_full_pixelLabels.txt', 'r') as f_source:
    with open('data_full_pixelLabels_train.txt', 'w') as f_train:
        with open('data_full_pixelLabels_val.txt', 'w') as f_val:
            with open('data_full_pixelLabels_test.txt', 'w') as f_test:
                for line in f_source:
                    rn = random.random()
                    if rn < SHARE_TRAIN:
                        f = f_train
                    elif rn < SHARE_TRAIN + SHARE_VAL:
                        f = f_val
                    else:
                        f = f_test
                    f.write(line)