#File for testing event page scraper
import os
from Parser import EventPageParser
import json

def main():

	print(os.getcwd())
	content = ''
	with open('Scraping/2025Pages/EventSchedule.html','r',encoding='utf-8') as file:
		content = file.read()
	
	result = EventPageParser.parseEventsPageContent(content)

	print(json.dumps(result,indent=4,sort_keys=True))

	for event in result['events']:
		print(event['session_data_links'])



	return 1







if __name__ == '__main__':
    main()