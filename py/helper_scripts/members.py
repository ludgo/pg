import sys
sys.path.append('..')

from pg_launcher.util import *
from pg_launcher.constants import *

# print percentages of relevant count_col groups within each unique in cluster_col
if __name__ == '__main__':

	file_name = str(sys.argv[1])
	cluster_col = str(sys.argv[2]) # 'cluster'
	count_col = str(sys.argv[3]) # COL_NAME_TESTING

	f = load_csv(build_file_path(file_name))

	clusters = f[cluster_col].unique()
	clusters.sort()

	cluster_type = {}

	for cluster in clusters:
		fC = f[f[cluster_col] == cluster].groupby(count_col)[count_col].count()
		fC.sort_values(ascending=False, inplace=True)
		print(cluster)

		for t in fC.keys():
			type_count = fC.get(t)
			cluster_count = fC.sum()
			proportion = type_count/cluster_count

			if proportion > 0.05 and t != 25:
				try:
					cluster_type[cluster].append(t)
				except KeyError:
					cluster_type[cluster] = [t]
				print('\t', t, '\t', type_count, '\t', round(proportion*100, 2), '%')
		print('\ttotal\t', fC.sum())

	for k,v in cluster_type.items():
		print(k, '\t', v)
