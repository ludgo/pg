source(file.path('.', 'R', 'util.R'))

args <- commandArgs(trailingOnly=TRUE)
parameterK <- strtoi(args[1])
parameterKmeta <- strtoi(args[2])
nFiles <- strtoi(args[3])

command <- 'python'
pythonScriptPath <- buildPathFromName(fileName='metacluster', fileFormat='py')

fileNames <- c()
if (nFiles == 0){
	# 0 prompts to load file paths from source file
	for (filePathFcs in readFcsPaths()){

		fileNames <- c(fileNames, convertFcsToCsv(filePathFcs))		
	}
} else {
	# args[4:3+n] are fcs file paths
	for (i in 4:(3+nFiles)){

		filePathFcs <- args[i]
		fileNames <- c(fileNames, convertFcsToCsv(filePathFcs))
	}
}

allArgs <- c(pythonScriptPath, paste(fileNames, collapse=','), parameterK, parameterKmeta)

# python py/metacluster.py fileBase1,fileBase2,... K K_meta

cat('Launching python subprocess...\n')
system2(command, args=allArgs)
cat('...python subprocess finished\n')
