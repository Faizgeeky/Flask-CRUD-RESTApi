from flask import Blueprint
from .views import SensorDataAPI, SensorAnalysisAPI
from .auth import auth_required
sensor_bp = Blueprint('sensor',__name__)



# Sensor data Analysis API
analysis_api = auth_required(SensorAnalysisAPI.as_view('analysis_api'))
sensor_bp.add_url_rule('/data/aggregate', view_func=analysis_api, methods=['GET'])

# Using api view is simpler to maintain single class for every individual route
data_view = auth_required(SensorDataAPI.as_view('data_api'))
# add in batch and fetch all data
sensor_bp.add_url_rule('/data/', view_func=data_view, methods=['GET','POST'])
# fetch by sensor id
sensor_bp.add_url_rule('/data/<string:sensor_id>', view_func=data_view, methods=['GET'])
# update by id
sensor_bp.add_url_rule('/data/<int:id>', view_func=data_view, methods=['PUT'])

