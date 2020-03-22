#!/usr/bin/python3
import datetime

from google_entities import GoogleEntities
from storage import Storage
from wikipedia_scraper import WikipediaScraper

def fetch_and_save_keywords():
    storage = Storage()
    events_collection = storage.get_order_by('event_date')
    for event_doc in events_collection:
        event_desc = event_doc.to_dict()['description']
        entities = GoogleEntities(event_desc).get_entities('name')
        update_doc = {
            'entities': entities
        }
        storage.update(event_doc.id, update_doc)


# fetch_and_save_keywords()
start_date = datetime.date(2000, 1, 1)
end_date = datetime.date(2000, 1, 4)
# scraper = EncyclopediaScraper()
scraper = WikipediaScraper()
scraper.fetch_and_save(start_date, end_date)
