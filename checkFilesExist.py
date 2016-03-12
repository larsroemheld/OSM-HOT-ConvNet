import os.path
with open('data_pixelLabels_train.txt', 'r') as f:
	with open('data_pixelLabels_train_clean.txt', 'w') as n:
		for l in f:
			file1, file2 = l.split(' ')
			file2 = file2[0:-1]
			if os.path.isfile(file1) and os.path.isfile(file2):
				print l
				n.write(l)