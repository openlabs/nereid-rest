# -*- coding: utf-8 -*-
"""
    Rest

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from flask import json

from trytond.pool import Pool
from trytond.model import ModelSQL, ModelView, fields
from nereid import route, jsonify, request, login_required, abort, current_user
from nereid.contrib.pagination import Pagination

__all__ = ['NereidRest', 'NereidRestPermission']


class NereidRest(ModelSQL):
    "Nereid REST"
    __name__ = "nereid.rest"

    @classmethod
    def serialize(cls, record):
        """
        Try and check if there is a serialize method in the record. If there is
        then use that to serialize. If not just return 'id' and 'rec_name'.
        """

        if hasattr(record, 'serialize'):
            return record.serialize()
        return {
            'id': record.id,
            'rec_name': record.rec_name
        }

    @classmethod
    @route('/rest/model/<model_name>', methods=['GET', 'POST'])
    @login_required
    def collection(cls, model_name):
        """
        Get the model name from the url and return all the records.

        :param model_name: Name of model

        GET: Return JSON serialized list of records.
        POST: Create new record of the model.
        """
        Model = cls._validate_model(model_name)

        if request.method == 'GET':
            domain = json.loads(
                request.args.get('domain', '[]')
            )
            order = json.loads(
                request.args.get('order', '[]')
            )
            records = Pagination(
                Model, domain,
                page=request.args.get('page', 1, int),
                per_page=min([request.args.get('per_page', 10, int), 100]),
                order=order
            )
            return jsonify(records.serialize())

        elif request.method == 'POST':
            return jsonify(
                items=map(cls.serialize, Model.create([request.json]))
            ), 201

    @classmethod
    @login_required
    @route(
        '/rest/model/<model_name>/<int:record_id>',
        methods=['GET', 'PUT', 'DELETE']
    )
    def element(cls, model_name, record_id):
        """
        Get model name and record ID from the URL and return JSON serialized
        data of that record.

        :param model_name: Name of model
        :param record_id: Record ID.

        GET: Return JSON serialized data of a record.
        PUT: Update record.
        DELETE: Delete a record.
        """
        Model = cls._validate_model(model_name)

        domain = [('id', '=', record_id)]
        record = Model.search(domain)
        if not record:
            return 'Record not found', 404
        record, = record

        if request.method == 'GET':
            return jsonify(
                cls.serialize(Model(record.id))
            )

        elif request.method == 'PUT':
            # Write to the record and return the updated record
            Model.write([record], request.json)
            return jsonify(
                cls.serialize(Model(record.id))
            )

        elif request.method == 'DELETE':
            Model.delete([record])
            return 'Record deleted.', 204

    @classmethod
    def _validate_model(cls, model_name):
        """
        Returns model if current Nereid user has permission otherwise
        throws 403.
        """
        RestPermission = Pool().get('nereid.rest.permission')

        permission = RestPermission.search([
            ('model.model', '=', model_name),
            ('allow_%s' % request.method.lower(), '=', True),
            ('permission', 'in', current_user.permissions),
        ])
        if not permission:
            abort(403)
        Model = Pool().get(model_name, type='model')
        return Model


class NereidRestPermission(ModelSQL, ModelView):
    "Nereid REST Permission"
    __name__ = "nereid.rest.permission"

    permission = fields.Many2One(
        'nereid.permission', 'Nereid Permission', required=True, select=True
    )
    model = fields.Many2One('ir.model', 'Model', required=True, select=True)
    allow_get = fields.Boolean('GET')
    allow_post = fields.Boolean('POST')
    allow_put = fields.Boolean('PUT')
    allow_patch = fields.Boolean('PATCH')
    allow_delete = fields.Boolean('DELETE')

    @classmethod
    def __setup__(cls):
        super(NereidRestPermission, cls).__setup__()
        cls._sql_constraints += [
            (
                'unique_model_permission',
                'UNIQUE(permission, model)',
                'Model must be unique per Nereid permission.',
            ),
        ]
