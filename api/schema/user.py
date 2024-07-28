from marshmallow import Schema, fields, validate, post_load
from api.model import User

class UserSchema(Schema):
    class Meta:
        fields = ("username", "email", "password") 
    username = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=6))

    @post_load
    def create_user(self, data, **kwargs):
        user = User(
            username = data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        return user
    

class UserLoginSchema(Schema):
    class Meta:
        fields = ("email", "password")
    email = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=6))

    