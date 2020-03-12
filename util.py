import datetime

class Util(object):
    @staticmethod
    def get_date_range(start_date, end_date):
        for ordinal in range(start_date.toordinal(), end_date.toordinal()):
            yield datetime.date.fromordinal(ordinal)

    @staticmethod
    def sanitize_text(text):
        return str(text).strip('\n').strip(' ')
