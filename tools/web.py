from HTMLParser import HTMLParser
import urllib

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def handle_entityref(self, name):
        self.fed.append('&%s;' % name)
    def get_data(self):
        return ''.join(self.fed)

_stripper = MLStripper()

def html_to_text(html):
    _stripper.feed(html)
    return _stripper.get_data()
