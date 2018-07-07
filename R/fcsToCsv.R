# helper script to convert fcs file to csv equivalent

source(file.path('.', 'R', 'util.R'))

args <- commandArgs(trailingOnly=TRUE)
filePathFcs <- args[1]

convertFcsToCsv(filePathFcs)
