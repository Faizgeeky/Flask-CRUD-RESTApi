from flask import request, jsonify, request
from flask.views import MethodView
# keeping seprate schema for different payload 
from api.schema.sensor import SensorSchema 
from extensions import db
from api.model import Sensor
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError 
# from sqlalchemy import and_
import pandas as pd
sensor_schema = SensorSchema(many=True)


class SensorDataAPI(MethodView):

    # Handle filter args dynamically
    def filter_sensor_Data(self,args):
        filters = []

        if 'sensor_id' in args:
            print("here")
            filters.append(Sensor.sensor_id == args.get('sensor_id', type=str))
        if 'start_time' in args:
            filters.append(Sensor.timestamp >= args['start_time'])
        if 'end_time' in args:
            filters.append(Sensor.timestamp <= args['end_time'])
        if 'min_humidity' in args:
            filters.append(Sensor.humidity >= args['min_humidity'])
        if 'max_humidity' in args:
            filters.append(Sensor.humidity <= args['max_humidity'])
        if 'min_pressure' in args:
            filters.append(Sensor.pressure >= args['min_pressure'])
        if 'max_pressure' in args:
            filters.append(Sensor.pressure <= args['max_pressure'])
        if 'min_temperature' in args:
            filters.append(Sensor.temperature >= args.get('min_temperature', type=float))
        if 'max_temperature' in args:
            filters.append(Sensor.temperature <= args.get('max_temperature', type=float))
        
        # print("filters", filters) //checkpoint
        # return sql filtered obj
        return filters
    

    def get(self, id=None):
        if id is None:
            sensor_data = Sensor.query.filter().all()
            sensor_data = sensor_schema.dump(sensor_data)
            return jsonify(sensor_data)
        else:
            try:
                json_data = request.args
                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', 10))
                aggregate = request.args.get('aggregate')
                # Handle dynamic args to filter
                filters = self.filter_sensor_Data(json_data)
                # retured filterd sqlalchemy obj 
                query = Sensor.query.filter(*filters)
                df = pd.DataFrame(query)
                print("Data", df)
                if aggregate:
                    if aggregate == 'hourly':
                        query = query.with_entities(
                            Sensor.sensor_id,
                            db.func.strftime('%Y-%m-%d %H:00:00', Sensor.timestamp).label('timestamp'),
                            db.func.avg(Sensor.temperature).label('temperature'),
                            db.func.avg(Sensor.humidity).label('humidity'),
                            db.func.avg(Sensor.pressure).label('pressure')
                        ).group_by('sensor_id', 'timestamp')
                    elif aggregate == 'daily':
                        query = query.with_entities(
                            Sensor.sensor_id,
                            db.func.strftime('%Y-%m-%d', Sensor.timestamp).label('timestamp'),
                            db.func.avg(Sensor.temperature).label('temperature'),
                            db.func.avg(Sensor.humidity).label('humidity'),
                            db.func.avg(Sensor.pressure).label('pressure')
                        ).group_by('sensor_id', 'timestamp')
                # use pagination dynamic with oage number
                pagination = query.paginate(page=page, per_page=per_page, error_out=False)
                
                sensor_data = pagination.items
                result = sensor_schema.dump(sensor_data)
                return jsonify({
                    "data": result,
                    "pagination": {
                        "total": pagination.total,
                        "pages": pagination.pages,
                        "current_page": pagination.page,
                        "next_page": pagination.next_num,
                        "prev_page": pagination.prev_num,
                        "per_page": pagination.per_page
                    }
                }), HTTPStatus.OK

            except Exception as e:
                return jsonify({'error':str(e)}) , HTTPStatus.INTERNAL_SERVER_ERROR

    # Handle post req
    def post(self):
        try:
            json_data = request.get_json()
            sensor_data = sensor_schema.load(json_data, session=db.session)
            
            db.session.add_all(sensor_data)
            db.session.commit()
            result = sensor_schema.dump(sensor_data)
            return jsonify({"message": "Data created successfully", "data": result}), HTTPStatus.CREATED
        
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({"message": "Invalid request", "error": "A sensor with the same sensor_id already exists."}), HTTPStatus.CONFLICT
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Invalid request", "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
            

    def delete(self, id):
        # Handle deletion of data with the given id
        return jsonify({"message": f"Data with id {id} deleted"})
