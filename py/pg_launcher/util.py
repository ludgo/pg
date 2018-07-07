from numpy import log10
from pandas import read_csv, DataFrame, concat as frame_concat
from sklearn.preprocessing import Imputer
from sklearn.manifold import TSNE
from matplotlib.backends.backend_pdf import PdfPages
import os.path

from pg_launcher.constants import *

# ./<file_format>/<file_name><optional:_suffix>.<file_format>
def build_file_path(name, suffix=None, file_format='csv'):
	if suffix:
		name = '{}_{}'.format(name, suffix)
	return os.path.join('.', file_format, '{}.{}'.format(name, file_format))

def load_csv(source_path, index_col=None):
	return read_csv(source_path, sep=DEFAULT_SEPARATOR, index_col=index_col)

def save_csv(frame, destination_path):
	frame.to_csv(destination_path, sep=DEFAULT_SEPARATOR, index=False)

def generate_unique_colors(n):
	# at most len(COLOR_PALETTE_UNIQUE) colors can be returned
	return COLOR_PALETTE_UNIQUE[:n]

# read marker names from default file
def read_markers():
	# a marker means a single row here
	return list(read_csv(build_file_path(SOURCE_FILE_BASE_NAME_MARKERS, file_format='txt'), header=None, squeeze=True))

# pyplot figure saving utility
def save_pdf(file_path, figure, file_format='pdf'):
	pdf_page = PdfPages(file_path)
	figure.savefig(pdf_page, format=file_format, bbox_inches='tight')
	pdf_page.close()

def get_A4_dimens(is_landscape, n_pages=1):
	# if not landscape rotate to portrait
	dimens = A4_DIMENS_LANDSCAPE if is_landscape else A4_DIMENS_LANDSCAPE[::-1]
	# multiply height by number of pages
	dimens[1] *= n_pages
	return dimens

# DataFrame missing values substitution
# frame is NOT copied
def impute_missing_values(frame, blank_value=0, replace_with='median'):
	imp = Imputer(missing_values=blank_value, strategy=replace_with, copy=False)
	return DataFrame(imp.fit_transform(frame), columns=frame.columns)

def optimality_function(kl, perp, n):
	'''
	Best t-SNE perplexity should minimize this function
	according to paper: https://arxiv.org/pdf/1708.03229.pdf

	:param kl: Kullback-Leibler divergence
	:param perp: perplexity
	:param n: number of points
	
	:return: function value
	'''
	return 2*kl + perp*log10(n)/n

# run t-SNE (with default number of iterations) to estimate best peplexity choice in range
def find_optimal_perplexity(matrix, min_perp=2, max_perp=15, step=1):
	kl_norm_dict = {}
	for perp in range(min_perp, max_perp+1, step):
		tsne = TSNE(perplexity=perp)
		tsne.fit_transform(matrix)
		kl_norm_dict[perp] = optimality_function(kl=tsne.kl_divergence_, perp=perp, n=matrix.shape[0])
	return min(kl_norm_dict, key=kl_norm_dict.get)

# concatenate files with same columns
# does preserve parameter list file order
# does NOT save newly created frame
# return concatenated DataFrame
def concat_files(file_names, suffix=None, cols=None, add_col=False):
	frames = []
	for file_name in file_names:
		frame = load_csv(build_file_path(file_name, suffix=suffix))
		if cols:
			frame = frame.filter(items=cols)
		if add_col:
			frame[COL_NAME_FILE] = file_name
		frames.append(frame)
	return frame_concat(frames, copy=False)

# split file on default column representing origin file
# does save all newly created files
def split_file(file_name, suffix=None):
	frame = load_csv(build_file_path(file_name, suffix=suffix))
	for u in frame[COL_NAME_FILE].unique():
		save_csv(frame[frame[COL_NAME_FILE] == u], build_file_path(u, suffix=suffix))
