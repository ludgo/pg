import numpy, pandas

import sys
sys.path.append('..')

from pg_launcher.util import *
from pg_launcher.constants import *

# take file_name csv and split into 4 approx. same size files
if __name__ == "__main__":

	file_name = str(sys.argv[1])
	file_path = build_file_path(file_name)

	frame = load_csv(file_path)
	frame['FileNum'] = frame['FileNum'].round(decimals=0).astype(int)

	randomFrame = numpy.random.rand(len(frame))

	save_csv(frame[randomFrame <= 0.25], build_file_path('p1'))
	save_csv(frame[numpy.logical_and(randomFrame > 0.25, randomFrame <= 0.5)], build_file_path('p2'))
	save_csv(frame[numpy.logical_and(randomFrame > 0.5, randomFrame <= 0.75)], build_file_path('p3'))
	save_csv(frame[randomFrame > 0.75], build_file_path('p4'))
