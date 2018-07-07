from pg_launcher import select, normalize, pg_cluster, visualize_tsne, visualize_heatmap, COL_NAME_CLUSTER
import sys

# python py/cluster.py fileBase K
if __name__ == '__main__':

	file_name = str(sys.argv[1])
	parameter_k = int(sys.argv[2])

	# preprocess
	file_name = select([file_name])
	normalize(file_name)

	# cluster
	pg_cluster(file_name, k=parameter_k)

	# visualize
	# heatmap of cluster medians
	visualize_heatmap('{}_cluster'.format(file_name), y_axis=COL_NAME_CLUSTER)
	# t-SNE on sample of points
	visualize_tsne('{}_labeled'.format(file_name), sample_by_col=COL_NAME_CLUSTER)
