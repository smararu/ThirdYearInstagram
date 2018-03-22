import csv
import os


# open and read the csv file into memory
fileName = "7amzahammad.csv"
file = open(fileName)
reader = csv.reader(file)

directoryName = fileName.replace(".csv", "")


# Create and move the CSV file to its own directory
if not os.path.exists(directoryName):
    os.makedirs(directoryName)
    os.rename("./" + fileName, "./" + directoryName + "/" + fileName)



# iterate through the lines and print them to stdout, this column is the scontent link
for line in reader:
	print line[1]
	print "\n"





