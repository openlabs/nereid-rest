# -*- coding: utf-8 -*-
"""
    Test nereid REST

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
from flask import json

DIR = os.path.abspath(os.path.normpath(
    os.path.join(__file__, '..', '..', '..', '..', '..', 'trytond')
))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, CONTEXT, USER, DB_NAME
from trytond.transaction import Transaction

from nereid.testing import NereidTestCase


class RestTestCase(NereidTestCase):
    '''
    Test Nereid REST
    '''

    def setUp(self):
        trytond.tests.test_tryton.install_module('nereid_rest')
        self.Party = POOL.get('party.party')
        self.Company = POOL.get('company.company')
        self.NereidUser = POOL.get('nereid.user')
        self.Currency = POOL.get('currency.currency')
        self.Model = POOL.get('ir.model')
        self.UrlMap = POOL.get('nereid.url_map')
        self.Language = POOL.get('ir.lang')
        self.NereidWebsite = POOL.get('nereid.website')
        self.Locale = POOL.get('nereid.website.locale')
        self.nereid_permission = POOL.get('nereid.permission')
        self.nereid_rest_permission = POOL.get('nereid.rest.permission')
        self.Model = POOL.get('ir.model')

    def setup_defaults(self):
        '''
        Setting Defaults for Test Nereid REST
        '''
        self.usd, = self.Currency.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }])
        self.company_party, = self.Party.create([{
            'name': 'Openlabs',
        }])
        self.company, = self.Company.create([{
            'party': self.company_party.id,
            'currency': self.usd.id
        }])
        self.guest_party, self.registered_party, self.user = self.Party.create(
            [
                {'name': 'Guest User'},
                {'name': 'Normal User'},
                {'name': 'Registered User'},
            ])
        self.guest_user, = self.NereidUser.create([{
            'party': self.guest_party.id,
            'display_name': 'Guest User',
            'email': 'guest@openlabs.co.in',
            'password': 'password',
            'company': self.company.id,
        }])

        # Create website
        url_map, = self.UrlMap.search([], limit=1)
        en_us, = self.Language.search([('code', '=', 'en_US')], limit=1)

        self.locale_en_us, = self.Locale.create([{
            'code': 'en_US',
            'language': en_us.id,
            'currency': self.usd.id,
        }])
        self.NereidWebsite.create([{
            'name': 'localhost',
            'url_map': url_map.id,
            'company': self.company.id,
            'application_user': USER,
            'default_locale': self.locale_en_us.id,
            'guest_user': self.guest_user.id,
            'currencies': [('set', [self.usd.id])],
        }])

        self.user_party, = self.Party.create([{
            'name': 'User1',
        }])

        self.currency, = self.Currency.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }])

        self.party, = self.Party.create([{
            'name': 'openlabs',
        }])

        self.actor_party, = self.Party.create([{
            'name': 'Party1',
        }])

        # Nereid permission for Admin
        perm_admin, = self.nereid_permission.create([{
            'name': 'Admin',
            'value': 'admin',
        }])
        # Nereid permission for users
        perm_user, = self.nereid_permission.create([{
            'name': 'User',
            'value': 'user',
        }])
        # Nereid Rest permission to admin for party.party model
        rest_admin_party, = self.nereid_rest_permission.create([{
            'permission': perm_admin,
            'model': self.Model.search(['model', '=', 'party.party'])[0],
            'allow_get': True,
            'allow_put': True,
            'allow_patch': True,
            'allow_delete': True,
            'allow_post': True,
        }])

        # Nereid Rest permission to admin for nereid.user model
        rest_admin_nereid_user, = self.nereid_rest_permission.create([{
            'permission': perm_admin,
            'model': self.Model.search(['model', '=', 'nereid.user'])[0],
            'allow_get': True,
        }])

        # Nereid Rest permission to User for party.party model
        rest_user_party, = self.nereid_rest_permission.create([{
            'permission': perm_user,
            'model': self.Model.search(['model', '=', 'party.party'])[0],
            'allow_post': True,
        }])

        self.admin_user, = self.NereidUser.create([{
            'party': self.registered_party.id,
            'display_name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company.id,
            'permissions': [('set', [perm_admin])],
        }])
        self.user, = self.NereidUser.create([{
            'party': self.user_party.id,
            'display_name': 'Normal User',
            'email': 'user@example.com',
            'password': 'password',
            'company': self.company.id,
            'permissions': [('set', [perm_user])],
        }])

    def test0010_rest(self):
        '''
        Test Nereid REST API for GET, POST, PUT, DELETE
        '''
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                # Login success
                rv = c.post('/login', data={
                    'email': 'email@example.com',
                    'password': 'password'
                })
                self.assertEqual(rv.location, 'http://localhost/')
                self.assertEqual(rv.status_code, 302)

                # Get all parties from DB to compare.
                parties = self.Party.search([])

                # Get all party records
                rv = c.get('/rest/model/party.party')
                json_rv = json.loads(rv.data)
                self.assertEqual(json_rv['count'], len(parties))

                # Get party with id 1
                rv = c.get('/rest/model/party.party/%d' % self.party.id)
                self.assertEqual(rv.status_code, 200)
                json_rv = json.loads(rv.data)
                self.assertEqual(json_rv['rec_name'], 'openlabs')

                # Edit party details
                rv = c.put(
                    '/rest/model/party.party/%d' % self.party.id,
                    data=json.dumps({
                        'name': 'Openlabs Technologies'
                    }), headers={'content-type': 'application/json'})
                self.assertEqual(rv.status_code, 200)

                # Name should be changed now, from PUT request.
                self.assertEqual(self.party.name, 'Openlabs Technologies')

                # Try to update a nonexisting record
                rv = c.put(
                    '/rest/model/party.party/111', data={
                        'name': 'Openlabs Technologies'
                    })
                self.assertEqual(rv.status_code, 404)

                # Create new record
                rv = c.post(
                    '/rest/model/party.party',
                    data=json.dumps({'name': 'Some User'}),
                    headers={'content-type': 'application/json'}
                )
                self.assertEqual(rv.status_code, 201)

                # Get all parties from DB to compare.
                parties = self.Party.search([])

                # There should be one more record after successful POST.
                self.assertEqual(len(self.Party.search([])), len(parties))

                rv = c.delete('/rest/model/party.party/6')
                self.assertEqual(rv.status_code, 204)

                rv = c.get('/rest/model/party.party/6')
                # Get 404 when GETting non-existent record. Record is deleted.
                self.assertEqual(rv.status_code, 404)

                # Get all parties from DB to compare.
                parties = self.Party.search([])

                # There should be one less record after successful DELETE.
                self.assertEqual(len(self.Party.search([])), len(parties))

                user = self.NereidUser(1)
                # Accessing model which has serialize method
                rv = c.get('/rest/model/nereid.user/%d' % user.id)
                json_rv = json.loads(rv.data)
                self.assertIn('display_name', json_rv)

    def test0020_rest_permission(self):
        '''
        Test Nereid REST permission
        '''
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                # Login success
                rv = c.post('/login', data={
                    'email': 'user@example.com',
                    'password': 'password'
                })
                self.assertEqual(rv.location, 'http://localhost/')
                self.assertEqual(rv.status_code, 302)

                # User doesn't have GET permission for party.party
                rv = c.get('/rest/model/party.party')
                self.assertEqual(rv.status_code, 403)

                # User has POST permission for party.party
                rv = c.post(
                    '/rest/model/party.party',
                    data=json.dumps({'name': 'Some User'}),
                    headers={'content-type': 'application/json'}
                )
                self.assertEqual(rv.status_code, 201)

                # User doesn't have DELETE permission for party.party
                rv = c.get('/rest/model/party.party/%d' % self.party.id)
                self.assertEqual(rv.status_code, 403)


def suite():
    '''
    Test Suite
    '''
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        RestTestCase)
    )
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
