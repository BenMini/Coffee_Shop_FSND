import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
'''
# db_drop_and_create_all()

# ROUTES
@app.route('/drinks', methods=['GET', 'POST'])
def drinks():
    if request.method == 'GET':
        # @requires_auth('get:drinks')
        def get_drinks():
            '''Gets all drinks in short form'''
            try:
                return jsonify({
                    'success': True,
                    'drinks': [drink.short() for drink in Drink.query.all()]
                }), 200
            except Exception:
                abort(404)
        return get_drinks()

    if request.method == 'POST':
        @requires_auth('post:drinks')
        def create_drink(payload):
            '''Creates new drink'''
            try:
                new_drink = Drink(
                    title=request.json['title'],
                    recipe=json.dumps(request.json['recipe']))
                new_drink.insert()
                return jsonify({
                    "success": True,
                    "drinks": [new_drink.long()]
                }), 200
            except Exception:
                abort(422)
        return create_drink()


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    '''Gets drink details in long form'''
    try:
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in Drink.query.all()]
        }), 200
    except Exception:
        abort(404)


@app.route('/drinks/<drink_id>', methods=['PATCH', 'DELETE'])
def alter_drinks(drink_id):
    if request.method == 'PATCH':
        @requires_auth('patch:drinks')
        def update_drinks(payload, drink_id):
            '''Updates drink by id'''
            try:
                drink = Drink.query.filter(Drink.id == drink_id).first_or_404()
                drink.title = request.json.get('title')

                drink.update()
                return jsonify({
                    'success': True,
                    'drinks': [drink.long()]
                }), 200
            except Exception:
                abort(404)
        return update_drinks(drink_id)

    if request.method == 'DELETE':
        @requires_auth('delete:drinks')
        def delete_drink(payload):
            try:
                '''Deletes selected drink by id'''
                drink = Drink.query.filter(Drink.id == drink_id).first_or_404()
                drink.delete()
                return jsonify({
                    "success": True,
                    "delete": drink.id
                }), 200
            except Exception:
                abort(404)
        return delete_drink()

# Error Handling
@app.errorhandler(400)
def bad_request(error):
    '''Error handling for Bad Request'''
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    '''Error handling for Unauthorized Access'''
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized'
    }), 401


@app.errorhandler(403)
def forbidden(error):
    '''Error handling for Authentication Error'''
    return jsonify({
        'success': False,
        'error': 403,
        'message:': 'Forbidden Authentication Error'
    }), 403


@app.errorhandler(422)
def unprocessable(error):
    '''Error handling for Unprocessable Entity'''
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


@app.errorhandler(AuthError)
def auth_error(error):
    '''Error handling for Authorization Error'''
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error
    }), error.status_code
