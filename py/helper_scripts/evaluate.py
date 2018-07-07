from pandas import Series

import sys
sys.path.append('..')

from pg_launcher import visualize_tsne, visualize_heatmap
from pg_launcher.util import *
from pg_launcher.constants import *

def assign_cell_type(pg_cluster):
	return {
		'0': 'CD11bmidMonocyte, CD11b-Monocyte',
		'1': 'Erythroblast',
		'2': 'Megakaryocyte',
		'4': 'MEP',
		'5': 'MatureCD4+T',
		'6': 'NaiveCD8+T',
		'7': 'NK',
		'8': 'NaiveCD4+T, GMP',
		'9': 'MPP, Platelet',
		'10': 'CD11bhiMonocyte',
		'12': 'Pre-BII, Plasma, MatureCD8+T, Pre-BI',
		'16': 'CMP, MatureCD38loB, MatureCD38midB',
		'18': 'PlasmacytoidDC'
	}.get(pg_cluster, '?')

def expert_to_pg(expert_cluster):
	return {
		'1': 10,
		'2': 0,
		'3': 0,
		'4': 16,
		'5': 1,
		'6': 8,
		'9': 16,
		'10': 16,
		'11': 5,
		'12': 12,
		'13': 2,
		'14': 4,
		'15': 9,
		'17': 8,
		'18': 6,
		'19': 7,
		'20': 12,
		'21': 18,
		'22': 9,
		'23': 12,
		'24': 12
	}.get(expert_cluster, -1)

if __name__ == '__main__':

	file_name = str(sys.argv[1])

	file_path = build_file_path(file_name)
	file_path_labeled = build_file_path(file_name, suffix='labeled')
	file_path_test = build_file_path(file_name, suffix='test')

	f = load_csv(file_path_labeled)
	f[COL_NAME_TESTING] = load_csv(file_path)[COL_NAME_TESTING].apply(lambda x: int(round(x)))

	if True:
		f = f[f[COL_NAME_TESTING] != 25]

	#visualize_tsne('{}_test'.format(file_name), sample_by_col=COL_NAME_CLUSTER, max_points_approx=10000)
	#visualize_heatmap('{}_cluster'.format(file_name), y_axis=COL_NAME_CLUSTER)

	f[COL_NAME_LABEL] = f[COL_NAME_CLUSTER].apply(lambda x: assign_cell_type(str(x))).apply(Series)

	f['true_cluster'] = f[COL_NAME_TESTING].apply(lambda x: expert_to_pg(str(x))).apply(Series)
	
	precision_total = 0
	recall_total = 0
	f1score_total = 0
	real_count_total = 0
	clusters = f[COL_NAME_CLUSTER].unique()
	clusters.sort()
	for pg_cluster in clusters:
		label = assign_cell_type(str(pg_cluster))
		if label != '?':
			tp = len(f[(f[COL_NAME_CLUSTER] == pg_cluster) & (f['true_cluster'] == pg_cluster)])
			fp = len(f[(f[COL_NAME_CLUSTER] == pg_cluster) & (f['true_cluster'] != pg_cluster)])
			fn = len(f[(f[COL_NAME_CLUSTER] != pg_cluster) & (f['true_cluster'] == pg_cluster)])
			precision = tp / (tp + fp)
			recall = tp / (tp + fn)
			f1score = 2 / (1/precision + 1/recall)
			print(label)
			print('\t', 'tp', '\t', tp)
			print('\t', 'fp', '\t', fp)
			print('\t', 'fn', '\t', fn)
			print('\t', 'precision', '\t', round(precision*100, 2), '%')
			print('\t', 'recall', '\t', round(recall*100, 2), '%')
			print('\t', 'f1score', '\t', round(f1score*100, 2), '%')
			real_count = len(f[f['true_cluster'] == pg_cluster])
			precision_total += (real_count * precision)
			recall_total += (real_count * recall)
			f1score_total += (real_count * f1score)
			real_count_total += real_count
	precision_total /= real_count_total
	recall_total /= real_count_total
	f1score_total /= real_count_total
	print('total')
	print('\t', 'precision', '\t', round(precision_total*100, 2), '%')
	print('\t', 'recall', '\t', round(recall_total*100, 2), '%')
	print('\t', 'f1score', '\t', round(f1score_total*100, 2), '%')

	if True:
		f = f[f[COL_NAME_LABEL] != '?']

	save_csv(f, file_path_test)

	#visualize_tsne('{}_test'.format(file_name), sample_by_col=COL_NAME_LABEL, max_points_approx=10000, ncol_legend=4)
