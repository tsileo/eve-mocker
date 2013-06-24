# -*- coding: utf-8 -*-
import re
import json
from httpretty import HTTPretty
from urlparse import parse_qs, urljoin
from collections import defaultdict
import time
import hashlib

PK = "_id"


def generate_etag():
    """ Helper function for generating random etag. """
    return hashlib.sha1(str(time.time())).hexdigest()


class EveMocker(object):
    """ Eve API mocker

    Everything is stored in self.items.

    Support:
        - All methods except HEAD
        - Handle etags
        - Return good status_code

    Not (yet?) supported:
        - HATEOAS links
        - schema validation

    :type base_url: str
    :param base_url: API base url

    :type pk_maps: dict
    :param pk_maps: Primary key mapping {resource: pk}

    :type default_pk: str
    :param default_pk: Default primary key, _id by default.

    """
    def __init__(self, base_url, pk_maps={}, default_pk="_id"):
        self.items = defaultdict(dict)
        self.base_url = base_url
        self.default_pk = default_pk
        self.pk_maps = pk_maps
        self.etag = {}

        # Register all URIs for resources
        resource_url = urljoin(self.base_url, "([^/]+/?$)")
        resource_regex = re.compile(resource_url)

        HTTPretty.register_uri(HTTPretty.GET,
                               resource_regex,
                               body=self.generate_resource_response)
        HTTPretty.register_uri(HTTPretty.POST,
                               resource_regex,
                               body=self.generate_resource_response)

        HTTPretty.register_uri(HTTPretty.DELETE,
                               resource_regex,
                               body=self.generate_resource_response)

        # Register URIs for items
        item_regex = re.compile(urljoin(self.base_url, "([a-zA-Z0-9-_]+)/([a-zA-Z0-9-_]+)"))

        HTTPretty.register_uri(HTTPretty.GET,
                               item_regex,
                               body=self.generate_item_response)

        HTTPretty.register_uri(HTTPretty.PATCH,
                               item_regex,
                               body=self.generate_item_response)

        HTTPretty.register_uri(HTTPretty.DELETE,
                               item_regex,
                               body=self.generate_item_response)

    def __enter__(self):
        HTTPretty.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        HTTPretty.disable()

    def get_pk(self, resource):
        return self.pk_maps.get(resource, self.default_pk)

    def get_resource(self, resource):
        """ Retrieve all items for a resource from self.items """
        return [item for key, item in self.items[resource].items()]

    def generate_resource_response(self, request, uri, headers):
        """ Generate a response for a resource,
            support all methods, except HEAD. """
        headers["content_type"] = "application/json"
        path = filter(lambda x: x not in ["api", ""], request.path.split('/'))
        resource = path[0]

        if request.method == "GET":
            return [200,
                    headers,
                    json.dumps({"_items": self.get_resource(resource)})]

        elif request.method == "POST":
            qs = parse_qs(request.body)
            out = {}
            for key, data in qs.items():
                item = json.loads(data[0])
                pk = item[self.get_pk(resource)]
                if pk in self.items[resource]:
                    out[key] = {"status": "ERR", "issues": ["pk not unique"]}
                else:
                    item_etag = generate_etag()
                    item["etag"] = item_etag
                    self.items[resource][pk] = item
                    out[key] = {"status": "OK", "etag": item_etag}
            return [200, headers, json.dumps(out)]

        elif request.method == "DELETE":
            del self.items[resource]
            return [200, headers, "{}"]

    def generate_item_response(self, request, uri, headers):
        """ Generate a response for an item,
            support all methods, except HEAD. """
        headers["content_type"] = "application/json"
        resource, item_id = filter(lambda x: x not in ["api", ""],
                                   request.path.split('/'))
        if item_id not in self.items[resource]:
            status_code = 405
            if request.method == "GET":
                status_code = 404
            return [status_code, headers, "{}"]

        if request.method in ["PATCH", "DELETE"]:
            if not "If-Match" in request.headers:
                return [403, headers, "{}"]

            old_etag = self.items[resource][item_id]["etag"]

            if request.headers["If-Match"] != old_etag:
                return [412, headers, "{}"]

        if request.method == "GET":
            r = self.items[resource]
            if item_id in r:
                return [200, headers, json.dumps(r[item_id])]

        elif request.method == "DELETE":
            r = self.items[resource]
            if item_id in r:
                del self.items[resource][item_id]
                return [200, headers, "{}"]

        elif request.method == "PATCH":
            qs = parse_qs(request.body)
            out = {}
            for k, patch_data in qs.items():
                patch_data = json.loads(patch_data[0])
                new_etag = generate_etag()
                patch_data.update({"etag": new_etag})
                self.items[resource][item_id].update(patch_data)
                out[k] = {"status": "OK", "etag": new_etag}
            return [200, headers, json.dumps(out)]

        return [405, headers, "{}"]
