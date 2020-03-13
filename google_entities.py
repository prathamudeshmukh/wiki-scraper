import requests

class GoogleEntities(object):
    event_desc = ''
    google_analyze_entities_url = 'https://language.googleapis.com/v1beta2/documents:analyzeEntities?key=AIzaSyBMRqcfiOOFgRxgNiQW39i7JVdyx8GYioo'

    def __init__(self, event_desc):
        self.event_desc = event_desc

    def get_google_api_body(self):
        return {
            "document": {
                "type": "PLAIN_TEXT",
                "language": "en",
                "content": self.event_desc
            },
            "encodingType": "UTF8"
        }

    def get_all_entity(self, entities, property):
        data = []
        for entity in entities:
            data.append(entity[property])
        return data

    def get_entities(self, entity_attribute):
        request_body = self.get_google_api_body()
        response = requests.post(self.google_analyze_entities_url, json=request_body)
        entities = response.json()['entities']
        if (len(entities) > 0):
            return self.get_all_entity(entities, entity_attribute)
        return []