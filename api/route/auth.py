from flask import Blueprint, request, jsonify
# keeping seprate schema for different payload 
from api.schema.user import UserSchema , UserLoginSchema
from extensions import db, jwt
from flask_jwt_extended import create_access_token
from api.model import User
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

# create blueprint route
auth_bp = Blueprint('auth',__name__)

# Userschema instance
user_schema = UserSchema()
login_schema = UserLoginSchema()

@auth_bp.route('/register',methods=['POST'])
def register():
    try:
        json_data = request.get_json()
        errors = user_schema.validate(json_data)
        if errors:
            return jsonify(errors), 401
        
        new_user = User(username=json_data['username'], email=json_data['email'])
        new_user.set_password(json_data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error":'User alredy exist~'}), HTTPStatus.CONFLICT

    except ValidationError as e:
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST

    except Exception as e:
        return jsonify({"message":"Invalid Request",'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


@auth_bp.route('/login',methods=['POST'])
def login():
    try:
        json_data = request.get_json()
        errors = login_schema.validate(json_data)
        if errors:
            return jsonify(errors), 401
        
        user = User.query.filter_by(email=json_data['email']).first()
        if user is None or user.check_password(json_data['password']) is False:
            return jsonify({"error": "Invalid email or password"}), HTTPStatus.UNAUTHORIZED
        
        access_token =  create_access_token(identity= user.id)
        
        return jsonify({"access_token": access_token}), HTTPStatus.OK

    except ValidationError as e:
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST

    except Exception as e:
        return jsonify({"message":"Invalid Request",'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
