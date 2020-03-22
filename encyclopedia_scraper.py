import datetime

import bs4
import requests

from google_entities import GoogleEntities
from storage import Storage
from util import Util


class EncyclopediaScraper:

    @staticmethod
    def get_day(date):
        return date.strftime("%B-%-d")

    def get_events_list(self, wiki):
        featured_event = wiki.select('.md-history-featured-date')[0].getText()
        featured_event = Util.sanitize_text(featured_event)
        event_description = wiki.select('.md-history-featured-content .description')[0]
        event_list = {}
        event_list[featured_event] = event_description

        events = wiki.select('.md-history-event')
        for event in events:
            event_date = event.select('.md-history-event-date')[0].getText()
            event_description = event.select('.description')[0]
            event_list[event_date] = event_description

        return event_list

    def get_event_text(self, event):
        buttons = event.select('.md-button')
        if len(buttons) > 0:
            for button in buttons:
                button.extract()
        return Util.sanitize_text(event.getText())

    def get_db_event_date(self, event_date):
        event_date = datetime.datetime.strptime(event_date, '%m/%d/%Y').date()
        return datetime.datetime.combine(event_date, datetime.time())

    def fetch_and_save(self, start_date, end_date):
        storage = Storage()
        for date in Util.get_date_range(start_date, end_date):
            url = 'https://www.britannica.com/on-this-day/' + (EncyclopediaScraper.get_day(date))
            print('Fetching encyclopaedia for :' + url)
            res = requests.get(url)
            res.raise_for_status()

            wiki = bs4.BeautifulSoup(res.text, "lxml")
            events_list = self.get_events_list(wiki)

            for year in events_list:
                day = date.strftime('%d')
                month = date.strftime('%m')
                event_date = month + '/' + day + '/' + year
                event_date = self.get_db_event_date(event_date)
                event_desc = self.get_event_text(events_list[year])
                wiki_cite_link = [url]
                google_entities = GoogleEntities(event_desc).get_entities('name')
                event_obj = {
                    'year': int(year),
                    'description': event_desc,
                    'event_date': event_date,
                    'wiki_cite_link': wiki_cite_link,
                    'entities': google_entities
                }
                storage.save_doc(event_obj)
