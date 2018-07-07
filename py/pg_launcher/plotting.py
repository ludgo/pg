from numpy import nanmin
import matplotlib.pyplot as plt
plt.switch_backend('agg') # prevent show plot bug
from seaborn import heatmap, clustermap

from pg_launcher.util import *

def visualize_tsne(file_name, perp=30, sample_by_col=None, max_points_approx=10000, ncol_legend=20):
	'''
	t-SNE with 2000 iterations,
	pdf (A4 format) is exported for both continuous & discrete columns
	
	:param file_name: file base name
	:param perp: t-SNE perplexity, -1 results in running t-SNE multiple times to find optimal value
	:param sample_by_col: column necessary due to proportional sampling, no sampling if None
	:param max_points_approx: approx. sample size
	:param ncol_legend: number of columns in plot legend
	''' 
	frame = load_csv(build_file_path(file_name))
	frame = frame[frame[COL_NAME_CLUSTER] != -1] # skip -1 which means under min cluster size
	if COL_NAME_METACLUSTER in frame.columns:
		frame = frame[frame[COL_NAME_METACLUSTER] != -1] # skip -1 which means under min metacluster size
	markers = read_markers()

	# sampling
	if not (sample_by_col is None) and len(frame.index) > max_points_approx:
		# sample proportionally to group fraction
		sample_fraction = max_points_approx/len(frame.index)
		frame = frame.groupby(sample_by_col).apply(lambda x: x.sample(frac=sample_fraction))
	data = frame.filter(items=markers).as_matrix()

	n_points = data.shape[0]
	print('\tVisualize {} points'.format(n_points), flush=True)
	if perp == -1:
		# use when not too many rows only! (for example t-SNE on whole clusters)
		perp = find_optimal_perplexity(data)
	print('Chosen t-SNE perplexity {}'.format(perp), flush=True)

	tsne = TSNE(perplexity=perp, n_iter=2000)
	data_embedded = tsne.fit_transform(data)
	print('t-SNE completed with KL divergence {}'.format(tsne.kl_divergence_), flush=True)
	frame['tsne_x'], frame['tsne_y'] = data_embedded[:, 0], data_embedded[:, 1]

	for col in frame:
		plt.figure(figsize=get_A4_dimens(is_landscape=True))
		
		if col in markers:
			# continuous
			plt.scatter(frame['tsne_x'], frame['tsne_y'], c=frame[col], alpha=0.5, cmap='jet', label=col, s=5)
			plt.colorbar()
		elif col in DISCRETE_COLS:
			# discrete
			unique_vals = frame[col].unique()
			colors = generate_unique_colors(len(unique_vals))

			for key, i in zip(unique_vals, range(0, len(unique_vals))):
				sub_frame = frame[frame[col] == key]
				plot_marker = 'o' #circle, default
				if i >= len(colors):
					plot_marker = 's' #square
				if i >= 2*len(colors):
					plot_marker = 'D' #diamond
				# theoretical limit of clusters is 2*len(colors)
				plt.scatter(sub_frame['tsne_x'], sub_frame['tsne_y'], c=colors[i % len(colors)], marker=plot_marker, alpha=0.75, label=key, s=5)
		else:
			continue
		
		ymin, ymax = plt.ylim()
		plt.ylim( ymin, ymin + (ymax-ymin) * 1.25 ) # reserve space for legend
		plt.legend(loc='upper center', ncol=ncol_legend, markerscale=3, columnspacing=0)

		file_path = build_file_path(file_name, suffix=col.replace('/', '_'), file_format='pdf')
		save_pdf(file_path, plt)
		print('Export {}'.format(file_path), flush=True)

		plt.gcf().clear()
		plt.close('all')

def plot_heatmap(frame, save_to_path, y_axis):

	land = frame.shape[1] > frame.shape[0]
	plt.figure(figsize=get_A4_dimens(is_landscape=land))
	square = True if frame.shape[0] < 25 else False # ensure fits A4

	hm = heatmap(frame, cmap='jet', xticklabels=True, yticklabels=True, square=square).get_figure()
	plt.xlabel('marker')
	plt.ylabel(y_axis)
	plt.xticks(rotation=90)
	plt.yticks(rotation=0, fontsize=6)

	save_pdf(save_to_path, hm)
	print('Export {}'.format(save_to_path), flush=True)
	plt.close('all')

def plot_clustermap(frame, save_to_path):

	cm = clustermap(frame, cmap='jet', xticklabels=True, yticklabels=True)

	save_pdf(save_to_path, cm)
	print('Export {}'.format(save_to_path), flush=True)
	plt.close('all')

def visualize_heatmap(file_name, y_axis):
	'''
	Heatmap of cluster medians,
	pdf (A4 format) is exported for both heatmap & clustermap, for both original & per marker transformed

	:param file_name: file base name
	:param y_axis: cluster column
	''' 
	frame = load_csv(build_file_path(file_name), index_col=y_axis).filter(items=read_markers())

	file_path = build_file_path(file_name, suffix='heatmap', file_format='pdf')
	plot_heatmap(frame, file_path, y_axis)
	file_path = build_file_path(file_name, suffix='clustermap', file_format='pdf')
	plot_clustermap(frame, file_path)

	# transformation to normal distribution
	frame = (frame - frame.mean()) / frame.std()
	frame.fillna(nanmin(frame.values), inplace=True)

	file_path = build_file_path(file_name, suffix='heatmap_transformed', file_format='pdf')
	plot_heatmap(frame, file_path, y_axis)
	file_path = build_file_path(file_name, suffix='clustermap_transformed', file_format='pdf')
	plot_clustermap(frame, file_path)
