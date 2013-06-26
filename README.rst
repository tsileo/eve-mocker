============
 Eve-Mocker
============

Mocking tool for `Eve powered REST API <http://python-eve.org>`_, based on the excellent `HTTPretty <http://falcao.it/HTTPretty>`_, aimed to be used in your unit tests, when you rely on an Eve API.

Features
========

Eve-Mocker doesn't try to replicate every Eve features, by design, it doesn't need any Eve settings files, doesn't support schema validation and more advanced features. Don't hesitate to contribute if you need more complex features.

* Everything is stored in memory (``self.items``)
* Support all methods except HEAD requests
* Handle ETags, and always return meaningful status code, like Eve.
* Partial support of filtering (only mongo query syntax)
* No need to change your code for testing, HTTPretty does everything for you, it works well with `requests <http://www.python-requests.org>`_.
* It renders only JSON, no XML yet.

Installing
==========

(soon to be released on pypy.)

.. code-block::

    $ pip install eve-mocker


Usage
=====

You should read `HTTPretty <http://falcao.it/HTTPretty>`_ documentation before starting.

Here is a basic example:

.. code-block:: python

    from httpretty import HTTPretty
    import requests

    HTTPretty.enable()
    EveMocker("http://myapi.com/api/")
    
    response = requests.get("http://myapi.com/api/mymodel/")
    assert response.status_code == 200
    assert response.json() == {"_items": []}

    HTTPretty.disable()

You can add data directly with ``EveMocker.set_resource``:

.. code-block:: python

    from httpretty import HTTPretty
    import requests

    HTTPretty.enable()
    eve_mocker = EveMocker("http://myapi.com/api/")

    mymodel_data = [{"_id": "fakeid", "content": "mycontent"}]
    eve_mocker.set_resource("mymodel", mymodel_data)

    response = requests.get("http://myapi.com/api/mymodel/")
    assert response.status_code == 200
    assert response.json() == {"_items": mymodel_data}

    HTTPretty.disable()


Alternatively, you use ``EveMocker`` within a context manager, and it will automatically call ``HTTPretty.enable()`` and ``HTTPretty.disable()``.

.. code-block:: python

    from eve_mocker import EveMocker
    import requests

    with EveMocker("http://myapi.com/api/"):
        response = requests.get("http://myapi.com/api/mymodel/")
        assert response.status_code == 200
        assert response.json() == {"_items": []}

Check the tests (in ``test_eve_mocker.py``) if you want to check more examples.

Getting started
===============

Let's say you want to test the following class stored in ``remote_items.py`` that need to call an Eve powered REST API:

.. code-block:: python

    from functools import partial
    import requests

    API_URL = "http://my-eve-api.com/api/"

    class RemoteItems(object):
        def __init__(self, api_url=API_URL):
            self.api_url = api_url
            self.endpoint_url = partial("{0}/{1}/".format, self.api_url)

        def get_latest(self):
            r = requests.get(self.endpoint_url("items"))
            r.raise_for_status()
            return r.json().get("_items", [])

Here is how you can do it with Eve-Mocker:

.. code-block:: python

    from eve_mocker import EveMocker
    import unittest
    from remote_items import RemoteItems, API_URL


    class TestRemoteItems(unittest.TestCase):
        def testGetLatestItems(self):
            items = [{"_id": "fakeid", "content": "my content"},
                     {"_id": "fakeid2", "content": "another_content"}]
            with EveMocker(API_URL) as eve_mocker:
                # We feed EveMocker DB with some items
                eve_mocker.set_resource("items", items)

                remote_items = RemoteItems()
                latest_items = remote_items.get_latest()

                self.assertEqual(sorted(latest_items), sorted(items))

    if __name__ == '__main__':
        unittest.main()

You can find these two files in the **examples** directory.


Advanced Usage
==============

``EveMocker`` takes two additonals arguments, ``default_pk`` if you need a primary key other than ``_id``, and ``pk_maps`` which is a mapping resource => primary key: ``{"resource": "pk_field", "resource2": "pk_field"}``.

License (MIT)
=============

Copyright (c) 2013 Thomas Sileo

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
