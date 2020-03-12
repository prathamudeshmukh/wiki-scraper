from util import Util
import requests
import bs4

class EncyclopediaScraper(object):

    def get_day(self, date):
        return date.strftime("%B-%-d")

    def get_events_list(self, wiki):
        featured_event = wiki.select('.md-history-featured-date')[0].getText()
        featured_event = Util.sanitize_text(featured_event)
        event_description = wiki.select('.md-history-featured-content .description')[0]
        print('event_description' + event_description)
        event_list = []
        event_list[featured_event] = event_description
        return event_list

    def fetch_and_save(self, start_date, end_date):
        for date in Util.get_date_range(start_date,end_date):
            url = 'https://www.britannica.com/on-this-day/' + (self.get_day(date))
            print('Fetching wiki for :' + url)
            res = requests.get(url)
            res.raise_for_status()

            wiki = bs4.BeautifulSoup(res.text, "lxml")
            print(self.get_events_list(wiki))
