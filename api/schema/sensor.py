from flask_marshmallow import Schema
from marshmallow import fields
from api.model import Sensor
from extensions import ma

class SensorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sensor
        load_instance = True

    timestamp = ma.DateTime(format='%Y-%m-%dT%H:%M:%S')

    # # id = ma.auto_field()
    # sensor_id = ma.auto_field()
    # timestamp = ma.auto_field()
    # temperature = ma.auto_field()
    # humidity = ma.auto_field()
    # pressure = ma.auto_field()