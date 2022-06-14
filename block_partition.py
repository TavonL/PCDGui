import numpy as np
import os
import glob


class Partition:
	
	def __init__(self, path, interval_x, interval_y, overlap=0.5, ratio=0.4, threshold=2000):
		self.interval_x = interval_x
		self.interval_y = interval_y
		self.overlap = overlap
		self.path = path
		self.ratio = ratio
		self.threshold = threshold
	
	def block_generation(self):
		if not os.path.exists(os.path.join('block', self.path)):
			os.makedirs(os.path.join('block', self.path))
		
		str_len = len(self.path)
		for file in glob.glob(os.path.join(self.path, '*.txt')):
			
			file_name = file[str_len + 1:-7]
			data = np.loadtxt(file, delimiter=',')
			point_number = data.shape[0]
			interval = np.max(data, axis=0) - np.min(data, axis=0)
			block_x = int((interval[0] - self.interval_x) / ((1 - self.overlap) * self.interval_x)) + 1
			block_y = int((interval[1] - self.interval_y) / ((1 - self.overlap) * self.interval_y)) + 1
			
			for i in range(block_x):
				start_x = np.min(data, axis=0)[0] + (i * (1 - self.overlap) * self.interval_x)
				for j in range(block_y):
					start_y = np.min(data, axis=0)[1] + (j * (1 - self.overlap) * self.interval_y)
					block_index = [k for k in range(point_number) if (start_x < data[k, 0] < start_x + self.interval_x) and (start_y < data[k, 1] < start_y + self.interval_y)]
					block_data = data[block_index, :]
					building = [t for t in range(len(block_index)) if block_data[t, 6] == 1]
					if (len(building) / (len(block_index)+1) > self.ratio) and (len(block_index) > self.threshold):
						np.savetxt(os.path.join('block', self.path, file_name + str(i) + '_' + str(j) + '.txt'), block_data)




path = 'RealWorldData'
interval_x = 50
interval_y = 50
overlap = 0.5
ratio = 0.001
tt = Partition(path=path, interval_x=interval_x, interval_y=interval_y, overlap=overlap, ratio=ratio)
tt.block_generation()

'''file = 'test\ResidentialArea_GT.txt'
data = np.loadtxt(file, delimiter=',')
point_number = data.shape[0]
interval = np.max(data, axis=0) - np.min(data, axis=0)
block_x = int((interval[0] - 50) / 50) + 1
block_y = int((interval[1] - 50) / 50) + 1

for i in range(block_x):
	start_x = np.min(data, axis=0)[0] + i * 50
	for j in range(block_y):
		start_y = np.min(data, axis=0)[1] + j * 50
		block_index = []
		for k in range(point_number):
			print(k)
			if (data[k, 0] > start_x) & (data[k, 0] < start_x + 50) & (data[k, 1] > start_y) & (data[k, 1] < start_y + 50):
				block_index.append(k)
		block_index = [k for k in range(point_number) if
		               (start_x < data[k, 0] < start_x + 50) and (start_y < data[k, 1] < start_y + 50)]
		block_data = data[block_index, :]
		building = [t for t in range(len(block_index)) if block_data[t, 6] == 1]
		np.savetxt(os.path.join('block', 'test', 'test' + str(i) + str(j) + '.txt'), block_data)'''
