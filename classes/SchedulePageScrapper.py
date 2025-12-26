from classes.EventPageScraper import EventPageScraper
from classes.Requestor import Requestor
from classes.Parser import EventPageParser
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

def extract_data_from_links(links):
    dates_found = []

    if not links:
        return ""
    for link in links:
        match = re.search(r'(\d{1,2})-(\d{1,2})-(\d{4})', link)
        if match:
            month, day, year = match.groups()
            try:
                date_obj = datetime.strptime(f"{month}-{day}-{year}", "%m-%d-%Y")
                dates_found.append(date_obj)
            except ValueError:
                pass

        if not match:
            match = re.search(r'(\d{1,2})-(\d{1,2})-(\d{2})(?![\d])', link)
            if match:
                month, day, year = match.groups()
                try:
                    full_year = f"20{year}"
                    date_obj = datetime.strptime(f"{month}-{day}-{full_year}", "%m-%d-%Y")
                    dates_found.append(date_obj)
                except ValueError:
                    pass
    if not dates_found:
        return "Dates not found"
        
    unique_dates = sorted(list(set(dates_found)))

    first_date = unique_dates[0]
    dates = [d for d in unique_dates if (d - first_date).days <= 2]

    if len(dates) == 1:
         return dates[0].strftime("%B %d, %Y")
    else:
        first_date = dates[0]
        last_date = dates[-1]
    
        if first_date.month == last_date.month:
            days = " & ".join([str(d.day) for d in dates])
            return f"{first_date.strftime('%B')} {days}, {first_date.year}"
        else:
            return f"{first_date.strftime('%B %d')} & {last_date.strftime('%B %d, %Y')}"


def get_schedule():
    try: 
        requestor = Requestor()
        scrapper = EventPageScraper(requestor)

        schedule_url = "https://ccsportscarclub.org/autocross/schedule/"

        logger.info(f"Fetching schedule page from {schedule_url}")

        origin_data = requestor.makeRequest(schedule_url)

        if origin_data["status_code"] != 200:
            logger.error(f"Failed to fetch schedule page, status code: {origin_data['status_code']}")
            return []
        logger.info("Successfully fetched schedule page")

        parsed_data = EventPageParser.parseEventsPageContent(origin_data["content"])

        if not parsed_data.get("events"):
            logger.warning("No events found in the schedule page")
            return []
        
        events = parsed_data["events"]
        logger.info(f"Extracted {len(events)} events from the schedule page")

        schedule_events = []

        for event in events:
            date = extract_data_from_links(event.get("session_data_links", []))
            event_data = {
                "name": event.get("name"),
                "date": date,
                "chairs": ", ".join(event.get("chairs", [])),
                "links": event.get("session_data_links", []),
                "registration_link": event.get("link", ""),
                "raw_data": event
            }
            schedule_events.append(event_data)
        return schedule_events
    
    except Exception as e:
        logger.error(f"An error occurred while fetching the schedule: {e}", exc_info=True)
        return []
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    schedule = get_schedule()
    print(f"\n{'='*80}")
    print(f"Found {len(schedule)} events")
    print(f"{'='*80}\n")
    
    for event in schedule:
        print(f"Event: {event['name']}")
        print(f"  Date: {event['date']}")
        print(f"  Links: {len(event['links'])} links")
        print()