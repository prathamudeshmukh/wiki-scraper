import hashlib

from google.cloud import firestore
import pymongo

class Storage(object):
    keyfile = 'history-47b77-b615bd2b5b7f.json'
    db_user = 'mongouser'
    db_password = 'fR!rG425FGeej!V'
    db_name = 'heroku_188x7kc9'
    db_url = 'mongodb://{username}:{password}@ds251819.mlab.com:51819/heroku_188x7kc9?retryWrites=false&gssapiServiceName=mongodb'
    db_url = db_url.format(username=db_user, password=db_password)
    db = None
    collection = None
    collection_name = 'events'

    def __init__(self):
        self.client = pymongo.MongoClient(self.db_url)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def get_uniq_id(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def get_order_by(self, column):
        return self.collection.order_by(column).stream()

    def save_doc(self, event_obj):
        description = event_obj['description']
        uniq_doc_id = str(self.get_uniq_id(description))
        exists = self.collection.find_one({"_id": uniq_doc_id})
        if exists is None :
            event_obj["_id"] = uniq_doc_id
            self.collection.insert_one(event_obj)

    def save_bulk_docs(self, events):
        requests = []
        print('Saving events...')
        for event in events:
            description = event['description']
            uniq_doc_id = str(self.get_uniq_id(description))
            requests.append(pymongo.UpdateOne({'_id': uniq_doc_id}, {"$set": event}, upsert=True))
        self.collection.bulk_write(requests, False)
        print('Events saved')

    def get_collection(self):
        return self.collection

    def update(self, id, event_object):
        doc_ref = self.collection.document(id)
        doc_ref.update(event_object)
