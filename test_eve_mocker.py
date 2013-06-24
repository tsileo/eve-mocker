# -*- coding: utf-8 -*-

""" test_eve_mocker.py - Test the eve_mocker module. """

import unittest
import requests
from httpretty import HTTPretty
from sure import expect
from eve_mocker import EveMocker
from urlparse import urljoin
from functools import partial
import json

BASE_URL = "http://localhost/api/"
api_url = partial(urljoin, BASE_URL)


class TestEveMocker(unittest.TestCase):
    def setUp(self):
        HTTPretty.enable()
        EveMocker(BASE_URL, default_pk="testpk")

    def tearDown(self):
        HTTPretty.disable()

    def testAPI(self):
        """ Test """
        mymodel_url = api_url("mymodel")
        mymodel1 = {"testpk": "mypk1", "content": "test content"}

        # Check that mymodel resource is empty
        response = requests.get(mymodel_url)
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("_items")
        expect(data["_items"]).to.be.empty

        # Posting mymodel1
        response = requests.post(mymodel_url,
                                 {"mymodel1": json.dumps(mymodel1)})
        data = response.json()

        # Check the status of the item and if it has an etag
        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("mymodel1")
        expect(data["mymodel1"]["status"]).to.equal("OK")
        expect(data["mymodel1"]).to.have.key("etag")

        # Storing the ETag for later
        mymodel1_etag = data["mymodel1"]["etag"]

        # Check that it has actually been created
        response = requests.get(mymodel_url)
        mymodel1_test = mymodel1.copy()
        mymodel1_test.update({"etag": data["mymodel1"]["etag"]})

        expect(response.status_code).to.equal(200)
        expect(response.json()).to.equal({"_items": [mymodel1_test]})

        # Check if we can retrieve the item via its URI
        response = requests.get(api_url("mymodel/mypk1"))
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.equal(mymodel1_test)

        # Check that we CAN'T rePOST mymodel1 with the same primary key
        response = requests.post(mymodel_url,
                                 {"mymodel1": json.dumps(mymodel1)})
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("mymodel1")
        expect(data["mymodel1"]["status"]).to.equal("ERR")

        # Now we try to PATCH the item without If-Match header
        mymodel1_patch = {"content": "new content"}
        response = requests.patch(api_url("mymodel/mypk1/"),
                                  {"data": json.dumps(mymodel1_patch)})

        expect(response.status_code).to.equal(403)

        # Check that it doesn't work with the wrong ETag
        response = requests.patch(api_url("mymodel/mypk1/"),
                                  {"data": json.dumps(mymodel1_patch)},
                                  headers={"If-Match": "falsyetag"})

        expect(response.status_code).to.equal(412)

        # Finally we PATCH with the good ETag
        response = requests.patch(api_url("mymodel/mypk1/"),
                                  {"data": json.dumps(mymodel1_patch)},
                                  headers={"If-Match": mymodel1_etag})
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("data")
        expect(data["data"]["status"]).to.equal("OK")
        expect(data["data"]).to.have.key("etag")

        mymodel1_etag = data["data"]["etag"]
        mymodel1_test.update({"etag": mymodel1_etag,
                              "content": "new content"})

        # Check if the item has been updated
        response = requests.get(api_url("mymodel/mypk1"))
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.equal(mymodel1_test)

        # Delete without ETag should return 403
        response = requests.delete(api_url("mymodel/mypk1/"))

        expect(response.status_code).to.equal(403)

        # Delete with a WRONG ETag should return 412
        response = requests.delete(api_url("mymodel/mypk1/"),
                                   headers={"If-Match": "wrongetag"})

        expect(response.status_code).to.equal(412)

        # Now we delete it the right way
        response = requests.delete(api_url("mymodel/mypk1/"),
                                   headers={"If-Match": mymodel1_etag})

        expect(response.status_code).to.equal(200)

        # Check that mymodel resource is empty
        response = requests.get(mymodel_url)
        data = response.json()

        expect(response.status_code).to.equal(200)
        expect(data).to.have.key("_items")
        expect(data["_items"]).to.be.empty

    def testContextManager(self):
        """ Test EveMocker within a context manager. """
        with EveMocker("http://myapi.com/api/"):
            response = requests.get("http://myapi.com/api/mymodel")
            expect(response.status_code).to.equal(200)
            expect(response.json()).to.equal({"_items": []})


if __name__ == '__main__':
    unittest.main()
