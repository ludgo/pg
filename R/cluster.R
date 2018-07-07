source(file.path('.', 'R', 'util.R'))

args <- commandArgs(trailingOnly=TRUE)
parameterK <- strtoi(args[1])
filePathFcs <- args[2]

command <- 'python'
pythonScriptPath <- buildPathFromName(fileName='cluster', fileFormat='py')

fileName <- convertFcsToCsv(filePathFcs)
allArgs <- c(pythonScriptPath, fileName, parameterK)

# python py/cluster.py fileBase K

cat('Launching python subprocess...\n')
system2(command, args=allArgs)
cat('...python subprocess finished\n')
