from pg_launcher import select, normalize, pg_metacluster, visualize_tsne, visualize_heatmap, COL_NAME_METACLUSTER
import sys

# python py/metacluster.py fileBase1,fileBase2,... K K_meta
if __name__ == '__main__':

	file_names = str(sys.argv[1]).split(',')
	parameter_k = int(sys.argv[2])
	parameter_k_meta = int(sys.argv[3])

	# preprocess
	file_name = select(file_names)
	normalize(file_name)

	# cluster each & metacluster
	pg_metacluster(file_names, k=parameter_k, k_meta=parameter_k_meta)
	
	# visualize
	# heatmap of cluster medians
	visualize_heatmap('{}_metacluster'.format(file_name), y_axis=COL_NAME_METACLUSTER)
	# t-SNE on sample of points
	visualize_tsne('{}_metalabeled'.format(file_name), sample_by_col=COL_NAME_METACLUSTER)
	# t-SNE on cluster medians
	visualize_tsne('{}_labeled'.format(file_name), perp=20)
	# do the same visualization per file (meaning per patient for example)
	for file_name in file_names:
		# heatmap of cluster medians
		visualize_heatmap('{}_metacluster'.format(file_name), y_axis=COL_NAME_METACLUSTER)
		# t-SNE on sample of points
		visualize_tsne('{}_metalabeled'.format(file_name), sample_by_col=COL_NAME_METACLUSTER)
