#!/usr/bin/python3
import sys
import requests
import bs4
import datetime
import hashlib
from util import Util
from encyclopedia_scraper import EncyclopediaScraper
from google_entities import GoogleEntities
from google.cloud import firestore
from storage import Storage

google_analyze_entities_url = 'https://language.googleapis.com/v1beta2/documents:analyzeEntities?key=AIzaSyBMRqcfiOOFgRxgNiQW39i7JVdyx8GYioo'

def get_day_for_wiki(date):
    return date.strftime("%B_%-d")

def is_empty(text):
    return len(text) == 0

def get_events_list(wiki):
    if is_gregorian_events_available(wiki) :
        calendar = list(wiki.select('#Gregorian_calendar')[0].parent.next_siblings)
        return calendar[1].select('li')
    return list(wiki.select('#Events')[0].parent.next_siblings)[1].select('li')

def is_gregorian_events_available(wiki):
    return len(wiki.select('#Gregorian_calendar')) > 0

def remove_reference_from_event(event):
    if len(event.select('.reference')) > 0:
        event.select('.reference')[0].extract()

def get_cite_link_for_event(event, wiki):
    try:
        refs = event.select('.reference a')
        if len(refs) > 0 :
            links = []
            for ref in refs :
                href = ref['href']
                external_links = wiki.select(href+' a.external')
                if (len(external_links) > 0) :
                    for link in external_links:
                        links.append(link['href'])
                    return links
        return []
    except:
        return []

def get_datetime(event_date):
    date = datetime.datetime.strptime(event_date, '%m/%d/%Y').date()
    return datetime.datetime.combine(date, datetime.time())

def get_year(year):
    year = Util.sanitize_text(year)
    if (year.find('BC') >= 0) :
        return None
    year = Util.sanitize_text(year.strip('AD'))
    if len(year) < 4:
        return year.rjust(4,'0')
    return year

def get_uniq_id(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()

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

def fetch_from_wiki_save_to_firestore(start_date, end_date):
    start_date = datetime.date(2000, 1, 1)
    end_date = datetime.date(2000, 1, 2)
    storage = Storage()

    for date in Util.get_date_range(start_date,end_date):
        url = 'https://en.wikipedia.org/wiki/' + (get_day_for_wiki(date))
        print('Fetching wiki for :' + url)
        res = requests.get(url)
        res.raise_for_status()

        wiki = bs4.BeautifulSoup(res.text, "lxml")
        events_list = get_events_list(wiki)
        events = 0
        print(str(len(events_list))+' events found in wiki')
        for event in events_list:

            wiki_cite_link = get_cite_link_for_event(event, wiki)
            remove_reference_from_event(event)

            eventText = event.getText().split(" – ")
            day = date.strftime('%d')
            year = get_year(eventText[0])
            if (year == None) :
                continue
            month = date.strftime('%m')
            event_desc = Util.sanitize_text(eventText[1])
            event_date = month+'/'+day+'/'+year
            event_date = get_datetime(event_date)
            event_obj = {
                'year': int(year),
                'description': event_desc,
                'event_date': event_date,
                'wiki_cite_link': wiki_cite_link
            }
            storage.save_doc(event_obj)
            events += 1

        print(str(events) + ' events stored')

# fetch_and_save_keywords()
start_date = datetime.date(2000, 1, 1)
end_date = datetime.date(2000, 1, 4)
scraper = EncyclopediaScraper()
scraper.fetch_and_save(start_date,end_date)
