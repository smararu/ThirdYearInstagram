import os
import csv
import time
import urllib
from selenium import webdriver
from bs4 import BeautifulSoup

# constants
initialTags = ["memorable", "unforgettable"]
initialPage = 'http://www.pictame.com/tag/' + initialTags[0]
fileName = initialTags[0] + "Tags.csv"
chromePath= "./chromedriver"

driver = webdriver.Chrome(chromePath)

if not os.path.exists(fileName):
	with open(fileName, 'w') as csvfile:
		fieldnames = ['userLink', 'mediaLink', 'imageTags']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()

def getLinks(linkPage):
	global driver
	linkPage = linkPage
	driver.get(linkPage)
	html = driver.page_source
	soup = BeautifulSoup(html, "html.parser")
	links = []
	for link in soup.find_all('a'):
		links.append(link.get('href'))

	return links


# soup.find_all('a', class_='user-name')
   	# with open('names.csv', 'w') as csvfile:
#     fieldnames = ['first_name', 'last_name']
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#     writer.writeheader()
#     writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
#     writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
#     writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})

#prints under the form of LINK, LINK USERNAME TAG
def tokenizeAndProcess(pageLinks):
	pageLinks = pageLinks
	index = 0
	rowNumber = -1
	nextPage = 'http://www.pictame.com/tag/' + initialTags[1]
	#prepare 3 arrays to load into csv
	arrayLinks = []
	arrayUsernames = []
	arrayTags = []
	while index < len(pageLinks):
		#media
		if "/media" in pageLinks[index]: 
			if rowNumber != -1:
				with open(fileName, 'a') as csvfile:
					fieldnames = ['userLink', 'mediaLink', 'imageTags']
					writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
					writer.writerow({'userLink': arrayUsernames[rowNumber].encode('utf-8'), 'mediaLink': arrayLinks[rowNumber].encode('utf-8'), 'imageTags': arrayTags[rowNumber].encode('utf-8') })
			rowNumber += 1
			print "[" + str(rowNumber) + "]" + " LINK: " 
			print(pageLinks[index])
			arrayLinks.append(pageLinks[index])
			#skip the extra link generated
			index += 2
			continue
		#user
		if "/user" in pageLinks[index]: 
			print "[" + str(rowNumber) + "]" + " USERNAME: "
			print(pageLinks[index])
			arrayUsernames.append(pageLinks[index])
		#tags
		if "/tag/" + initialTags[0] + "/" in pageLinks[index]:
			nextPage = pageLinks[index]
		if "/tag" in pageLinks[index]: 
			pageLinks[index] = pageLinks[index].replace('/tag/','#') 
			print "[" + str(rowNumber) + "]" 
			print(pageLinks[index])
			if len(arrayTags) > rowNumber:
				arrayTags[rowNumber] = arrayTags[rowNumber] + " " + pageLinks[index]
			elif len(arrayTags) <= rowNumber:
				arrayTags.append(pageLinks[index])
		if "/tag/unforgettable/" in pageLinks[index]:
			with open(fileName, 'a') as csvfile:
				fieldnames = ['userLink', 'mediaLink', 'imageTags']
				writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
				writer.writerow({'userLink': arrayUsernames[rowNumber].encode('utf-8'), 'mediaLink': arrayLinks[rowNumber].encode('utf-8'), 'imageTags': arrayTags[rowNumber].encode('utf-8') })
			nextPage = pageLinks[index]
		index += 1

	return nextPage

loop = 0

links = getLinks(initialPage)
time.sleep(10)
nextPage = tokenizeAndProcess(links)

while loop < 9:
	links = getLinks(nextPage)
	time.sleep(10)
	nextPage = tokenizeAndProcess(links)
	loop += 1


# for tag in soup.find_all('a'):
#     # if "http://www.pictame.com/media" in tag:
#     results.append(tag)



# for tag in soup.find_all(a=re.compile("http://www.pictame$")) :
#     print tag

# for node in soup.find_all(text=lambda x: x and "price" in x):
#     print node

 
# driver.maximize_window()
# images = driver.find_element_by_xpath('//a[contains(@href,"http://www.pictame.com/media/")]')
# currentWindow = driver.current_window_handle


# images.click()

 
driver.quit()   


