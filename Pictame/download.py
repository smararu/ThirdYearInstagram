import sys
import urllib, urllib2
import csv
import os
import glob
import re
import time
from selenium import webdriver
from bs4 import BeautifulSoup

#  while sleep 1; do python download.py; done
# open and read the csv file into memory and download images


# Create a listing of all CSV files
allCSVFiles = []
index = 0
chromePath= "./chromedriver"
# define directories
allCSVDirectory = os.getcwd()
workingDirectory = os.getcwd()

# create a list of all the CSV files
os.chdir(allCSVDirectory)
for CSVfile in glob.glob("*.csv"):
    allCSVFiles.append(CSVfile)
os.chdir(workingDirectory)

driver = webdriver.Chrome(chromePath)

# For all CSV files
while index < len(allCSVFiles):

    fileName = allCSVFiles[index]
    directoryName = fileName.replace(".csv", "")


    # Create and move the CSV file to its own directory
    if not os.path.exists(directoryName):
        os.makedirs(directoryName)
        os.rename("./" + fileName, "./" + directoryName + "/" + fileName)

    os.chdir(directoryName)
    print "File Name: " + fileName
    file = open(fileName)
    reader = csv.reader(file)


    skipFirst = 0

    # iterate through the lines and print them to stdout, this column is the scontent link
    for line in reader:
        if skipFirst == 0:
            skipFirst = 1
            continue

        url = line[1]
        driver.get(url)
        time.sleep(10)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        tokens = []
        link = soup.find_all('figure') #only one 
        tokens = str(link).split()
        for token in tokens:
            if 'src=' in token:
                downloadLink = token
                downloadLink = downloadLink.replace('"', ' ')
                downloadLink = re.search("(?P<url>https?://[^\s]+)", downloadLink).group("url")
                urlName = directoryName + url.split('/')[-1]
                print "Downloading: " + str(downloadLink)
                urllib.urlretrieve (downloadLink, urlName)    

    index += 1
    os.chdir(workingDirectory)

    # u = urllib2.urlopen(url)
    # f = open(urlName, 'wb')
    # meta = u.info()
    # fileSize = int(meta.getheaders("Content-Length")[0])
    # print "Downloading: %s Bytes: %s" % (urlName, fileSize)

    # fileSizeDownload = 0
    # blockSize = 8192
    # while True:
    #     buffer = u.read(blockSize)
    #     if not buffer:
    #         break

    #     fileSizeDownload += len(buffer)
    #     f.write(buffer)
    #     status = r"%10d  [%3.2f%%]" % (fileSizeDownload, fileSizeDownload * 100. / fileSize)
    #     status = status + chr(8)*(len(status)+1)
    #     print status,

    # f.close()

driver.quit()