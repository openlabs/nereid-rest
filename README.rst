Nereid Rest
============

.. image:: https://travis-ci.org/openlabs/nereid-rest.svg?branch=develop
    :target: https://travis-ci.org/openlabs/nereid-rest
.. image:: https://coveralls.io/repos/openlabs/nereid-rest/badge.png
  :target: https://coveralls.io/r/openlabs/nereid-rest

Nereid Rest is a tryton module which adds RESTful API to `Nereid <https://github.com/openlabs/nereid>`_.


* `Installation <#installation>`_
* `Screenshot <#screenshot>`_
* `Usage <#usage>`_
* `How to grant permission for a model <#installation>`_
* `Example <#for-example>`_


Installation
------------
Get the latest code from github and install::

    pip install git+ssh://git@github.com/openlabs/nereid-rest.git@develop

Screenshot
------------
.. image:: images/nereid_rest.png

Usage
-----

To access a tryton model using nereid-rest API, you must first grant access of the
model to the Nereid user using tryton. From tryton a Nereid user can be given access
to any tryton model with explicit permission for any of the HTTP methods 
(``GET``, ``POST``, ``PUT``, ``PATCH``, ``DELETE``)

How to grant permission for a model from tryton?
````````````````````````````````````````````````

Start tryton and look for ``Nereid`` on the left sidebar, expand ``Nereid``. There
you'll find ``Configuration`` -> ``Nereid Rest``.

Open ``Nereid Rest`` create new permission. You must fill ``Nereid Permission``
which can be any permission created in Nereid; and ``Model`` name.

Also select any of the HTTP methods you want the users having the selected ``Nereid Permission``
to access.

Any user who tries to access a model or an HTTP method on a model which is not
selected in nereid-rest will get ``403`` (Forbidden) response.

So, for example, user having access to only ``GET``, won't be able to access
any of the other HTTP methods, like ``POST`` to create a new record for that model.


**Tip** : 
*It's advisable to only allow HTTP methods which the user should have access to.
You don't want to create a security hole in your application by allowing access to models
and HTTP methods, which the user shouldn't have access to.*



After granting access of a model in nereid-rest, access data of any model just by accessing ``/rest/model``
followed by the model name in the URL, which gives you model records as JSON:

================    ===============================================

GET, POST           /rest/model/<mode.name>

================    ===============================================

To request a specific record from a model:

================    ===============================================

GET, PUT, DELETE    /rest/model/<mode.name>/<record_id>

================    ===============================================

For example
-----------
Considering, current Nereid User has permission to access model ``party.party``'s ``GET`` method.
To get all the records of ``party.party`` ::

    /rest/model/party.party

Get data of record with id 5 from ``party.party`` model::

    /rest/model/party.party/5

By default you only get the ``id`` and ``rec_name`` if there's no ``serialize`` method in the model.

But, if there's a ``serialize`` method in the model, nereid-rest will return whatever ``serialize`` method returns.
