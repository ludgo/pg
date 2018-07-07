DEFAULT_SEPARATOR = '\t'

COL_NAME_CLUSTER = 'cluster'
COL_NAME_METACLUSTER = 'metacluster'
COL_NAME_FILE = 'file'
COL_NAME_TESTING = 'FileNum'
COL_NAME_LABEL = 'cell_type'
DISCRETE_COLS = [COL_NAME_CLUSTER, COL_NAME_METACLUSTER, COL_NAME_FILE, COL_NAME_TESTING, COL_NAME_LABEL]
COL_NAME_COUNT_CELL = 'cell_count'
COL_NAME_COUNT_CLUSTER = 'cluster_count'

FILE_BASE_NAME_COMBINED = 'comb'

SOURCE_FILE_BASE_NAME_MARKERS = 'markers'

A4_DIMENS_LANDSCAPE = [11.69, 8.27] # unit inch

# enumerate visually unique colors
# source: http://phrogz.net/tmp/24colors.html
COLOR_PALETTE_UNIQUE = [
	'#FF0000', '#FFFF00', '#00EAFF', '#AA00FF', '#FF7F00', '#BFFF00',
	'#0095FF', '#FF00AA', '#FFD400', '#6AFF00', '#0040FF', '#EDB9B9',
	'#B9D7ED', '#E7E9B9', '#DCB9ED', '#B9EDE0', '#8F2323', '#23628F',
	'#8F6A23', '#6B238F', '#4F8F23', '#000000', '#737373', '#CCCCCC'
]