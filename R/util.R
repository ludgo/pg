library('flowCore')

DEFAULT_SEPARATOR <- '\t'
SOURCE_FILE_BASE_NAME_FCS_PATHS <- 'files'
MAX_FILE_NAME_LENGTH <- 30

# ./<fileFormat>/<fileName>.<fileFormat>
buildPathFromName <- function(fileName, fileFormat){

	return(file.path('.', fileFormat, paste0(fileName, '.', fileFormat)))
}

# extract base name - last path segment without extension
extractNameFromPath <- function(filePath){

	return(strsplit(basename(filePath), '[.]')[[1]][1])

}

# read fcs file paths from default file
readFcsPaths <- function(){
	
	return(scan(buildPathFromName(fileName=SOURCE_FILE_BASE_NAME_FCS_PATHS, fileFormat='txt'), what='', sep='\n'))
}

# read fcs file
# replace column names with column description
# save new file
makeDescColName <- function(filePathFcs){

	fileName <- extractNameFromPath(filePathFcs)
	fileNameNew <- paste0(fileName, '_descAsName')
	filePathFcsNew <- buildPathFromName(fileName=fileNameNew, fileFormat='fcs')

	frame <- read.FCS(filePathFcs, transformation=FALSE)
	colnames(frame) <- make.names(pData(parameters(frame))$desc)
	write.FCS(frame, filename=filePathFcsNew)

	return(filePathFcsNew)
}


# convert fcs file to csv equivalent
# ! spaces in file name will be replaced with underscore
# ! file name will be reduced, make sure is unique in first MAX_FILE_NAME_LENGTH characters
# !!! use descAsColName=TRUE if column names are stored in description instead of the right column
convertFcsToCsv <- function(filePathFcs, descAsColName=TRUE){

	stopifnot(isFCSfile(filePathFcs))
	fileName <- extractNameFromPath(filePathFcs)
	fileName <- substr(fileName, 0, MAX_FILE_NAME_LENGTH)
	fileName <- gsub(" ", "_", fileName)

	frame <- read.FCS(filePathFcs, transformation=FALSE)
	# DEBUG to see where column names are stored:
	# print(pData(parameters(frame)))
	if (descAsColName){
		colnames(frame) <- c(pData(parameters(frame))$desc)
		# or use:
		# colnames(frame) <- make.names(pData(parameters(frame))$desc)
		# but it replaces all special characters with .
	}
	frame <- as.data.frame((exprs(frame)))

	filePathCsv <- buildPathFromName(fileName=fileName, fileFormat='csv')
	write.table(frame, filePathCsv, sep=DEFAULT_SEPARATOR, row.names=FALSE)
	cat(paste(filePathFcs, '--->', filePathCsv), '\n')

	return(fileName)
}
