import datetime

import bs4
import requests

from storage import Storage
from util import Util


class WikipediaScraper(object):

    @staticmethod
    def get_day_for_wiki(date):
        return date.strftime("%B_%-d")

    @staticmethod
    def is_empty(text):
        return len(text) == 0

    @staticmethod
    def get_events_list(wiki):
        if WikipediaScraper.is_gregorian_events_available(wiki):
            calendar = list(wiki.select('#Gregorian_calendar')[0].parent.next_siblings)
            return calendar[1].select('li')
        return list(wiki.select('#Events')[0].parent.next_siblings)[1].select('li')

    @staticmethod
    def is_gregorian_events_available(wiki):
        return len(wiki.select('#Gregorian_calendar')) > 0

    @staticmethod
    def remove_reference_from_event(event):
        if len(event.select('.reference')) > 0:
            event.select('.reference')[0].extract()

    @staticmethod
    def get_cite_link_for_event(event, wiki):
        try:
            refs = event.select('.reference a')
            if len(refs) > 0:
                links = []
                for ref in refs:
                    href = ref['href']
                    external_links = wiki.select(href + ' a.external')
                    if (len(external_links) > 0):
                        for link in external_links:
                            links.append(link['href'])
                        return links
            return []
        except:
            return []

    @staticmethod
    def get_datetime(event_date):
        date = datetime.datetime.strptime(event_date, '%m/%d/%Y').date()
        return datetime.datetime.combine(date, datetime.time())

    @staticmethod
    def get_year(year):
        year = Util.sanitize_text(year)
        if (year.find('BC') >= 0):
            return None
        year = Util.sanitize_text(year.strip('AD'))
        if len(year) < 4:
            return year.rjust(4, '0')
        return year

    def fetch_and_save(self, start_date, end_date):
        storage = Storage()

        for date in Util.get_date_range(start_date, end_date):
            url = 'https://en.wikipedia.org/wiki/' + (WikipediaScraper.get_day_for_wiki(date))
            print('Fetching wiki for :' + url)
            res = requests.get(url)
            res.raise_for_status()

            wiki = bs4.BeautifulSoup(res.text, "lxml")
            events_list = WikipediaScraper.get_events_list(wiki)
            events = 0
            print(str(len(events_list)) + ' events found in wiki')
            for event in events_list:

                wiki_cite_link = WikipediaScraper.get_cite_link_for_event(event, wiki)
                WikipediaScraper.remove_reference_from_event(event)

                eventText = event.getText().split(" – ")
                day = date.strftime('%d')
                year = WikipediaScraper.get_year(eventText[0])
                if (year == None):
                    continue
                month = date.strftime('%m')
                event_desc = Util.sanitize_text(eventText[1])
                event_date = month + '/' + day + '/' + year
                event_date = WikipediaScraper.get_datetime(event_date)
                event_obj = {
                    'year': int(year),
                    'description': event_desc,
                    'event_date': event_date,
                    'wiki_cite_link': wiki_cite_link
                }
                storage.save_doc(event_obj)
                events += 1

            print(str(events) + ' events stored')
