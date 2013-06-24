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
* No need to change your code for testing, HTTPretty does everything for you, it works well with `requests <http://www.python-requests.org>`_.


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


Alternatively, you use ``EveMocker`` within a context manager, and it will automatically call ``HTTPretty.enable()`` and ``HTTPretty.disable()``.

.. code-block:: python

    from eve_mocker import EveMocker
    import requests

    with EveMocker("http://myapi.com/api/"):
        response = requests.get("http://myapi.com/api/mymodel/")
        assert response.status_code == 200
        assert response.json() == {"_items": []}

Check the tests (in ``test_eve_mocker.py``) if you want to check more examples.

Advanced Usage
==============

``EveMocker`` takes two additonals arguments, ``default_pk`` if you need a primary key other than ``_id``, and ``pk_maps`` which is a mapping resource => primary key: ``{"resource": "pk_field", "resource2": "pk_field"}``.

License (MIT)
=============

Copyright (c) 2013 Thomas Sileo

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
