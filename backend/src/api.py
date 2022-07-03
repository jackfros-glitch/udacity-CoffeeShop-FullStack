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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES

@app.route('/test')
def test():
    return 'just testing the server great job kudos to you'
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        if not drinks:
            abort(404)
        formatted_drinks = [drink.short() for drink in drinks]
        return jsonify({
            "success": "True",
            "drinks":formatted_drinks
        }) 
    except:
        abort(400)   

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        formatted_drinks = [drink.long() for drink in drinks]
        return jsonify({
            "success": "True",
            "drinks":formatted_drinks
        })    
    except:
        abort(400)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def craete_drink(payload):
    # print('{"title":"test_data","recipe":"[{\"name\": \"water\", \"color\": \"blue\", \"parts\": 1}]"}')
    print(payload)
    try:
        req = request.get_json()
        if not req:
            abort(400)

        title = req['title']
        recipe = json.dumps(req['recipe'])
        print(title, recipe, sep="//")
        new_drink = Drink(title=title, recipe=recipe)
        
        new_drink.insert()
        drink = Drink.query.get(new_drink.id)

        return jsonify({
        "success":"True",
        "drinks": drink.long()
    })
    except Exception as e:
        print(e)
        abort(422)

    
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    try:
        data = request.get_json()
        if not data:
            abort(400)
    
        drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
        if not drink:
            abort(404)

        drink.title = data.get('title')
        drink.recipe = data.get('recipe')
        drink.update()
    except:
        abort(400)

    return jsonify({
        "success":"True",
        "drinks": drink.long()
    })
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink_id = id
    drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
    if not drink:
        abort(404)
    try:
        drink.delete()
    except:
        abort(422)
    return jsonify({
        "success":True,
        "delete":drink_id
    })
# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(403)
def forbiden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "you are forbiden from viewing this resource"
    }), 403


@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "you are not authorized to view this resource"
    }), 401 

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400 

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "server error"
    }), 500

@app.errorhandler(503)
def service_unavailable(error):
    return jsonify({
        "success": False,
        "error": 503,
        "message": "there seems to be a network issue, please check your network and try again "
    }), 500
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
