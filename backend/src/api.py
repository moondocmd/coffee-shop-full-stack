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
'''
#db_drop_and_create_all()

## ROUTES
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
	drinks = [drink.short() for drink in Drink.query.order_by(Drink.id).all()]
	return jsonify({
		"success": True,
		"drinks": drinks
	}), 200

	#add failure codes

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
def get_drinks_detail(token):
	try:
		drinks = [drink.long() for drink in Drink.query.order_by(Drink.id).all()]
		return jsonify({
			"success": True,
			"drinks": drinks
		}), 200
	
	except Exception as e:
		print("WEVE GOT AN EXCEPTIONSSS")
		print(e)
		abort(404)
	#add failure codes

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
def new_drink(token):
	print("TIME TO ADD A DRINK")
	try:
		data = request.get_json()
		title = data.get('title', None)
		recipe = data.get('recipe', None)
		print(type(recipe))
		print("TITLE = "  +str(title) + " ...Recipe = " + str(recipe))
		new_drink = Drink(title=title, recipe=json.dumps(recipe))
		print("created a new drink " + str(new_drink))
		new_drink.insert()
		return jsonify({
			'success': True,
			'drinks': [new_drink.long()]
		}), 200
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
#MIKE COMMENT..... TRY AND REFACTOR THIS (did it a little)
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token, id):
	print("Lets try to update a drink")
	try:
		drink = Drink.query.filter(Drink.id == id).one_or_none() 
		if drink is None: #lets make the other methods consistent with this, THIS DOES WORK!
			print("DRINK IS NONE!")
			abort(404)
		print("patching : " + str(drink))
		body = request.get_json()
		drink.title = body.get('title', drink.title)
		recipe = json.dumps(body.get('recipe'))
		drink.recipe = recipe if recipe != 'null' else drink.recipe
		drink.update()
		return  jsonify({
			'success': True, 
			'drinks': [drink.long()]
		}), 200
	except: #refactor this part, what is it really doing?
		abort(422)

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
###### MIKE ADDITION ON 8/25 UPDATE!
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks') 
def delete_drinks(payload, drink_id):
	print("CALLING DELETE")
	#pseudocode for if id is not found in Drink return 404
	try:
		drink = Drink.query.get(drink_id)
		drink.delete()
		return jsonify({
			'success': True,
			'deleted': drink_id,
		}), 200
	except:
		print("Nothing to delete mate")
		abort(422)

## Error Handling
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

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
	each error handler should return (with approprate messages):
			 jsonify({
					"success": False, 
					"error": 404,
					"message": "resource not found"
					}), 404

'''
@app.errorhandler(422) ##### UPDATE SYNTAX
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422
'''
@TODO implement error handler for 404
	error handler should conform to general task above 
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
	error handler should conform to general task above 
'''
@app.errorhandler(AuthError) #update syntax
def auth_error(ex):
    return jsonify({
        "success": False,
        "error": ex.status_code,
        "message": ex.error['code']
    }), 401