import os, glob

allFiles = []

for file in glob.glob("*.csv"):
    allFiles.append(file)

print allFiles