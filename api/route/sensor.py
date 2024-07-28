from flask import Blueprint, request, jsonify
from flask.views import MethodView
from .views import SensorDataAPI
sensor_bp = Blueprint('sensor',__name__)




data_view = SensorDataAPI.as_view('data_api')
# sensor_bp.add_url_rule('/data/', defaults={'id': None}, view_func=data_view, methods=['GET'])
sensor_bp.add_url_rule('/data/', view_func=data_view, methods=['GET','POST'])
sensor_bp.add_url_rule('/data/<string:sensor_id>', view_func=data_view, methods=['GET', 'DELETE'])
