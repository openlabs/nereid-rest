# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from rest import NereidRest


def register():
    Pool.register(
        NereidRest,
        module='nereid_rest', type_='model'
    )
