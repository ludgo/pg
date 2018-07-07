from numpy import unique
from pandas import merge as frame_merge
from phenograph import cluster

from pg_launcher.util import *

def pg_cluster(file_name, k=30, min_cluster_size=10):
	'''
	Run PhenoGraph clustering
	
	:param file_name: file base name
	:param k: kNN's K
	:param min_cluster_size: minimal number of grouped points to form cluster
	''' 
	file_path_single_normalized = build_file_path(file_name, suffix='normalized')
	file_path_single_labeled = build_file_path(file_name, suffix='labeled')
	file_path_single_cluster = build_file_path(file_name, suffix=COL_NAME_CLUSTER)

	markers = read_markers()
	data = load_csv(file_path_single_normalized).filter(items=markers).as_matrix()
	assert data.shape[1]==len(markers)
	print('\tCluster {} points in {}'.format(data.shape[0], file_name), flush=True)
	communities, graph, Q = cluster(data, k=k, nn_method='kdtree', min_cluster_size=min_cluster_size)
	data, graph = None, None
	print('Found {} clusters'.format(len(unique(communities))), flush=True)

	frame = load_csv(file_path_single_normalized)
	frame[COL_NAME_CLUSTER] = communities
	save_csv(frame, file_path_single_labeled)

	# medians & counts
	cluster_frame = frame.groupby(COL_NAME_CLUSTER, as_index=False).median()
	cluster_frame = cluster_frame[cluster_frame[COL_NAME_CLUSTER] != -1] # skip -1 which means under min cluster size
	cluster_frame[COL_NAME_COUNT_CELL] = frame.groupby(COL_NAME_CLUSTER)[COL_NAME_CLUSTER].count()
	save_csv(cluster_frame, file_path_single_cluster)

	print('Clustering successful', flush=True)

def pg_metacluster(file_names, k=30, k_meta=15, min_metacluster_size=2, cluster_each=True):
	'''
	Run PhenoGraph clustering for each file and PhenoGraph metaclustering
	
	:param file_names: file base names
	:param k: kNN's K for clustering
	:param k_meta: kNN's K for metaclustering
	:param min_metacluster_size: minimal number of grouped clusters to form metacluster
	''' 
	file_path_normalized = build_file_path(FILE_BASE_NAME_COMBINED, suffix='normalized')
	file_path_cluster = build_file_path(FILE_BASE_NAME_COMBINED, suffix=COL_NAME_CLUSTER)
	file_path_labeled = build_file_path(FILE_BASE_NAME_COMBINED, suffix='labeled')
	file_path_metalabeled = build_file_path(FILE_BASE_NAME_COMBINED, suffix='metalabeled')
	file_path_metacluster = build_file_path(FILE_BASE_NAME_COMBINED, suffix=COL_NAME_METACLUSTER)

	# Note: it is important that files have been normalized altogether
	if cluster_each:
		split_file(FILE_BASE_NAME_COMBINED, suffix='normalized')
		for file_name in file_names:
			pg_cluster(file_name, k=k)
	cluster_frame = concat_files(file_names, suffix=COL_NAME_CLUSTER, add_col=True)
	save_csv(cluster_frame, file_path_cluster)

	markers = read_markers()
	data = cluster_frame.filter(items=markers).as_matrix()
	assert data.shape[1]==len(markers)
	print('\tMetacluster {} points in {}'.format(data.shape[0], FILE_BASE_NAME_COMBINED), flush=True)
	communities, graph, Q = cluster(data, k=k_meta, nn_method='kdtree', min_cluster_size=min_metacluster_size)
	print('Found {} metaclusters'.format(len(unique(communities))), flush=True)
	cluster_frame[COL_NAME_METACLUSTER] = communities
	save_csv(cluster_frame, file_path_labeled)

	frame = concat_files(file_names, suffix='labeled')
	# -- START
	# For DataFrame merge it is necessary to match also value types. Keep this block to prevent bugs!
	frame[COL_NAME_FILE]= frame[COL_NAME_FILE].astype(str)
	cluster_frame[COL_NAME_FILE]= cluster_frame[COL_NAME_FILE].astype(str)
	frame[COL_NAME_CLUSTER]= frame[COL_NAME_CLUSTER].astype(int)
	cluster_frame[COL_NAME_CLUSTER]= cluster_frame[COL_NAME_CLUSTER].astype(int)
	# -- END
	frame = frame_merge(frame, cluster_frame[[COL_NAME_FILE, COL_NAME_CLUSTER,COL_NAME_METACLUSTER]], how='left', on=[COL_NAME_FILE, COL_NAME_CLUSTER])
	save_csv(frame, file_path_metalabeled)
	split_file(FILE_BASE_NAME_COMBINED, suffix='metalabeled')

	# medians & counts
	frame = frame[frame[COL_NAME_CLUSTER] != -1] # skip -1 which means under min cluster size
	frame = frame[frame[COL_NAME_METACLUSTER] != -1] # skip -1 which means under min metacluster size
	frame.drop(COL_NAME_CLUSTER, axis=1, inplace=True)
	metacluster_frame = frame.groupby(COL_NAME_METACLUSTER, as_index=False).median()
	metacluster_frame[COL_NAME_COUNT_CELL] = cluster_frame.groupby(COL_NAME_METACLUSTER)[COL_NAME_COUNT_CELL].sum()
	metacluster_frame[COL_NAME_COUNT_CLUSTER] = cluster_frame.groupby(COL_NAME_METACLUSTER)[COL_NAME_METACLUSTER].count()
	save_csv(metacluster_frame, file_path_metacluster)

	# medians & counts for each file (patient)
	for file_name in file_names:
		subframe = frame[frame[COL_NAME_FILE] == file_name]
		cluster_subframe = cluster_frame[cluster_frame[COL_NAME_FILE] == file_name]
		metacluster_subframe = subframe.groupby(COL_NAME_METACLUSTER, as_index=False).median()
		metacluster_subframe[COL_NAME_COUNT_CELL] = cluster_subframe.groupby(COL_NAME_METACLUSTER)[COL_NAME_COUNT_CELL].sum()
		metacluster_subframe[COL_NAME_COUNT_CLUSTER] = cluster_subframe.groupby(COL_NAME_METACLUSTER)[COL_NAME_METACLUSTER].count()
		save_csv(metacluster_subframe, build_file_path(file_name, suffix=COL_NAME_METACLUSTER))

	print('Metaclustering successful', flush=True)
