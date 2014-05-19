Nereid Rest
============
Nereid Rest is a tryton module which adds RESTful API to `Nereid <https://github.com/openlabs/nereid>`_.

Installation
------------
Get the latest code from github and install::

    pip install git+ssh://git@github.com/openlabs/nereid-rest.git@develop

Usage
-----
After installing nereid-rest, access data of any model just by accessing ``/rest/model`` followed by the model name in the URL, which gives you model records as JSON:

================    ===============================================

GET, POST           /rest/model/<mode.name>

================    ===============================================

To request a specific record from a model:

================    ===============================================

GET, PUT, DELETE    /rest/model/<mode.name>/<record_id>

================    ===============================================

For example
-----------
To get all the records of ``party.party`` ::

    /rest/model/party.party

Get data of record with id 5 from ``party.party`` model::

    /rest/model/party.party/5

By default you only get the ``id`` and ``rec_name`` if there's no ``serialize`` method in the model.

But, if there's a ``serialize`` method in the model, nereid-rest will return whatever ``serialize`` method returns.
