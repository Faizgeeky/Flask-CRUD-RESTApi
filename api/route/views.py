from flask import request, jsonify, request
from flask.views import MethodView
# keeping seprate schema for different payload 
from api.schema.sensor import SensorSchema 
from extensions import db
from api.model import Sensor
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError 
import pandas as pd
sensor_schema = SensorSchema(many=True)


class SensorDataAPI(MethodView):
    # Handle filter args dynamically
    def filter_sensor_Data(self,header_agrs, **args):
        # print(args)
        filters = []

      
        if 'sensor_id' in args:
            filters.append(Sensor.sensor_id == str(args['sensor_id']))
        if 'start_time' in header_agrs:
            filters.append(Sensor.timestamp >= header_agrs['start_time'])
        if 'end_time' in header_agrs:
            filters.append(Sensor.timestamp <= header_agrs['end_time'])
        if 'min_humidity' in header_agrs:
            filters.append(Sensor.humidity >= header_agrs['min_humidity'])
        if 'max_humidity' in header_agrs:
            filters.append(Sensor.humidity <= header_agrs['max_humidity'])
        if 'min_pressure' in header_agrs:
            filters.append(Sensor.pressure >= header_agrs['min_pressure'])
        if 'max_pressure' in header_agrs:
            filters.append(Sensor.pressure <= header_agrs['max_pressure'])
        if 'min_temperature' in header_agrs:
            filters.append(Sensor.temperature >= header_agrs.get('min_temperature', type=float))
        if 'max_temperature' in header_agrs:
            filters.append(Sensor.temperature <= header_agrs.get('max_temperature', type=float))
        
        # print("filters", filters) //checkpoint
        # return sql filtered obj
        return filters
    
    def aggregration(self, df, aggregate_type):
        print("types are", aggregate_type)
        # applyiung aggregation
        if len(df) >0 and 'hourly' in aggregate_type and 'daily' in aggregate_type:
            print("Dataframe is", df)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[['timestamp','temperature','humidity', 'pressure']]
            df_hour = df.groupby(df['timestamp'].dt.hour).mean()
            df_day = df.groupby(df['timestamp'].dt.day).mean()

            hourly_data = df_hour.to_dict(orient='records')
            daily_data = df_day.to_dict(orient='records')

            return {'daily_avg':daily_data,'hourly_avg':hourly_data}

        elif len(df) >0 and 'hourly' in aggregate_type:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[['timestamp','temperature','humidity', 'pressure']]
            df_hour = df.groupby(df['timestamp'].dt.hour).mean()
            
            print("Datafrane mean is ", df_hour)
            hourly_data = df_hour.to_dict(orient='records')

            return {'hourly_avg':hourly_data}

        elif len(df) >0 and 'daily' in aggregate_type:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[['timestamp','temperature','humidity', 'pressure']]
            df_day = df.groupby(df['timestamp'].dt.day).mean()
            daily_data = df_day.to_dict(orient='records')

            # Return as JSON response
            return {'daily_avg':daily_data}
        
    def get(self, sensor_id=None):
        if sensor_id is None:
            json_data = request.args
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            
            # Handle dynamic args to filter
            filters = self.filter_sensor_Data(json_data)
            # retured filterd sqlalchemy obj 
            query = Sensor.query.filter(*filters)
            
            
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            sensor_data = pagination.items
            result = sensor_schema.dump(sensor_data)
            df = pd.DataFrame(result)

            
            # If aggregation requested return aggregate data only
            aggregate = request.args.get('aggregate')
            if aggregate != None:
                result = self.aggregration(df, aggregate)
                if result is not None :
                    return jsonify({
                            'aggregate': result,
                        }), HTTPStatus.OK
                else:
                    return jsonify({"message":"No data found"}), HTTPStatus.OK
            
            # else return all sensor data
            else:
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
        else:
            # print("id is", id)
            try:
                json_data = request.args
                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', 10))
                # Handle dynamic args to filter
                filters = self.filter_sensor_Data(json_data, sensor_id = sensor_id)

                # retured filterd sqlalchemy obj 
                query = Sensor.query.filter(*filters)
                pagination = query.paginate(page=page, per_page=per_page, error_out=False)
                sensor_data = pagination.items
                result = sensor_schema.dump(sensor_data)
                df = pd.DataFrame(result)

                # If aggregation requested return aggregate data only
                aggregate = request.args.get('aggregate')
                if aggregate != None:
                    result = self.aggregration(df, aggregate)
                    if result is not None :
                        return jsonify({
                                'aggregate': result,
                            }), HTTPStatus.OK
                    else:
                        return jsonify({"message":"No data found"}), HTTPStatus.OK
                # else return all sensor data
                else:
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
            

    def put(self, sensor_id):
        # Handle deletion of data with the given id
        return jsonify({"message": f"Data with id {sensor_id} deleted"})
