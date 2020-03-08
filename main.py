#!/usr/bin/python3
import sys
import requests
import bs4
import datetime

from google.cloud import firestore

def get_date_range(start_date, end_date):
    for ordinal in range(start_date.toordinal(), end_date.toordinal()):
        yield datetime.date.fromordinal(ordinal)

def get_day_for_wiki(date):
    return date.strftime("%B_%-d")

def sanitize_text(text):
    return str(text).strip('\n').strip(' ')

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
#############################################################################

start_date = datetime.date(2000, 1, 2)
end_date = datetime.date(2000, 2, 2)
keyfile = 'history-47b77-b615bd2b5b7f.json'
db = firestore.Client.from_service_account_json(keyfile)
events_collection = db.collection('events')

for date in get_date_range(start_date,end_date):
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
        year = sanitize_text(eventText[0])
        if (year.rfind('AD') >= 0):
            continue
        month = date.strftime('%m')
        event_desc = sanitize_text(eventText[1])
        event_date = month+'/'+day+'/'+year
        event_date = get_datetime(event_date)
        event_obj = {
            'year': int(year),
            'description': event_desc,
            'event_date': event_date,
            'wiki_cite_link': wiki_cite_link
        }
        events_collection.add(event_obj)
        events += 1

    print(str(events) + ' events stored')

    