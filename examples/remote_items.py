from urlparse import urljoin
from functools import partial
import requests

API_URL = "http://my-eve-api.com/api/"


class RemoteItems(object):
    def __init__(self, api_url=API_URL):
        self.api_url = api_url
        self.endpoint_url = partial(urljoin, self.api_url)

    def get_latest(self):
        r = requests.get(self.endpoint_url("items"))
        r.raise_for_status()
        return r.json().get("_items", [])
