from numpy import arcsinh

from pg_launcher.util import *

def select(file_names, impute=False, transform=True):
	'''
	Select and concatenate columns from specified files,
	only columns for markers loaded from default source file are selected,
	newly created file is saved
	
	:param file_names: file base names
	:param impute: choose whether to impute missing values
	:param transform: choose whether to apply arcsinh transformation

	:return: newly created file base name
	''' 
	markers = read_markers()
	f = concat_files(file_names, cols=markers, add_col=True)
	print('Markers to clustering:', markers, flush=True)

	diff_cols = f.columns.difference([COL_NAME_FILE])
	if transform:
		f[diff_cols] = f[diff_cols].applymap(lambda x: arcsinh(x/5))
		print('Transformed by arcsinh with cofactor 5', flush=True)
	if impute:
		f[diff_cols] = impute_missing_values(f[diff_cols])
		print('Missing values replaced by median', flush=True)

	file_name = file_names[0] if len(file_names)==1 else FILE_BASE_NAME_COMBINED
	save_csv(f, build_file_path(file_name, suffix='selected'))
	return file_name

def normalize(file_name, max_quantile=0.995, altogether=True):
	'''
	Normalize 0 to 1,
	newly created file is saved
	
	:param file_name: file base name
	:param max_quantile: quantile to end up being 1 after transformation applied
	:param altogether: False normalize per COL_NAME_FILE, True all files together
	''' 
	markers = read_markers()
	f = load_csv(build_file_path(file_name, suffix='selected'))
	if altogether:
		for marker in markers:
			min_q = f[marker].min()
			max_q = f[marker].quantile(max_quantile)
			range_q = max_q - min_q
			f[marker] = f[marker].apply(lambda x: (x - min_q) / range_q)
		print('Normalized 0 to 1 with MAX={}th percentile ALTOGETHER'.format(max_quantile*100), flush=True)
	else:
		for file in f[COL_NAME_FILE].unique():
			subf = f[f[COL_NAME_FILE]==file]
			for marker in markers:
				min_q = subf[marker].min()
				max_q = subf[marker].quantile(max_quantile)
				range_q = max_q - min_q
				f.loc[subf.index,marker] = f.loc[subf.index,marker].apply(lambda x: (x - min_q) / range_q)
		print('Normalized 0 to 1 with MAX={}th percentile PER FILE'.format(max_quantile*100), flush=True)
	save_csv(f, build_file_path(file_name, suffix='normalized'))
