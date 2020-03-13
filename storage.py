from google.cloud import firestore
import hashlib

class Storage(object):
    keyfile = 'history-47b77-b615bd2b5b7f.json'
    db = None
    collection = None
    collection_name = 'events'
    
    def __init__(self):
        self.db = firestore.Client.from_service_account_json(self.keyfile)
        self.collection = self.db.collection(self.collection_name)

    def get_uniq_id(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def get_order_by(self, column):
        return self.collection.order_by(column).stream()

    def save_doc(self, event_obj):
        description = event_obj['description']
        uniq_doc_id = str(self.get_uniq_id(description))
        self.collection.document(uniq_doc_id).set(event_obj)

    def get_collection(self):
        return self.collection
    
    def update(self, id, event_object):
        doc_ref = self.collection.document(id)
        doc_ref.update(event_object)