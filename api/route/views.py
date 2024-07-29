from flask import jsonify, request
from flask.views import MethodView
# keeping seprate schema for different payload 
from api.schema.sensor import SensorSchema 
from extensions import db
from api.model import Sensor
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError 
from sqlalchemy import func, extract,text
import pandas as pd

import json
sensor_schema = SensorSchema(many=True)

def aggregation( df, aggregate_type):
        # applying aggregation
        json_data = {}
        if len(df) >0 and 'yearly' in aggregate_type:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[['timestamp','temperature','humidity', 'pressure']]
            df_year = df.groupby(df['timestamp'].dt.year).mean().round(2)
            
            print("Datafrane mean is ", df_year)
            yearly_data = df_year.to_dict(orient='records')

            json_data['yearly_avg'] = yearly_data

        if len(df) >0 and 'hourly' in aggregate_type:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[['timestamp','temperature','humidity', 'pressure']]
            df_hour = df.groupby(df['timestamp'].dt.hour).mean().round(2)
            
            print("Datafrane mean is ", df_hour)
            hourly_data = df_hour.to_dict(orient='records')

            json_data['hourly_avg'] = hourly_data

        if len(df) >0 and 'daily' in aggregate_type:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[['timestamp','temperature','humidity', 'pressure']]
            df_day = df.groupby(df['timestamp'].dt.day).mean().round(2)
            daily_data = df_day.to_dict(orient='records')

            # Return as JSON response
            json_data['daily_avg'] = daily_data
        
        return json_data

class SensorDataAPI(MethodView):
    # Handle filter args dynamically
    def filter_sensor_Data(self,header_agrs, **args):
        # print(args)
        filters = []
        if 'id' in args:
            filters.append(Sensor.id == int(args['id']))
        if 'sensor_id' in args:
            filters.append(Sensor.sensor_id == str(args['sensor_id']))
        if 'sensor_id' in header_agrs:
            filters.append(Sensor.sensor_id == header_agrs['sensor_id'])
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
    
    def aggregate_sensor_data(self, filters, group_by_field, average_fields):
        query = self.filter_sensor_data(filters)

        # Apply aggregation
        aggregates = {
            'average_temperature': func.avg(Sensor.temperature),
            'average_pressure': func.avg(Sensor.pressure),
            'average_humidity': func.avg(Sensor.humidity)
        }

        # Select required fields and apply aggregation
        query = query.with_entities(
            Sensor.sensor_id,
            func.date_trunc(group_by_field, Sensor.timestamp).label('period'),
            *[aggregate for aggregate in aggregates.values()]
        ).group_by(
            Sensor.sensor_id,
            func.date_trunc(group_by_field, Sensor.timestamp)
        )

        return query

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
            aggregate = request.args.get('aggregate')
            if aggregate and len(result)>0:
                df = pd.DataFrame(result)[['sensor_id','timestamp','temperature','pressure','humidity']]
                print("Data", df)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                aggregate_data = {}

                if 'hourly' in aggregate:
                    df_grouped = df.groupby(['sensor_id', df['timestamp'].dt.hour]).mean().round(2)
                    df_grouped = df_grouped.rename_axis(['sensor_id', 'date']).reset_index()
                    df_dict = df_grouped.to_dict(orient='records')

                    # Format dictionary to include sensor_id in values
                    formatted_dict = [
                        {
                            "sensor_id": item["sensor_id"],
                            "date": str(item["timestamp"]),
                            "temperature": item["temperature"],
                            "humidity": item["humidity"],
                            "pressure": item["pressure"]
                        }
                        for item in df_dict
                    ]
                    aggregate_data['hourly_avg'] = formatted_dict
    
                if 'daily' in aggregate:
                    df_grouped = df.groupby(['sensor_id', df['timestamp'].dt.date]).mean().round(2)
                    df_grouped = df_grouped.rename_axis(['sensor_id', 'date']).reset_index()
                    # Convert to dictionary format
                    df_dict = df_grouped.to_dict(orient='records')
                    formatted_dict = [
                        {
                            "sensor_id": item["sensor_id"],
                            "date": str(item["timestamp"].date()),
                            "temperature": item["temperature"],
                            "humidity": item["humidity"],
                            "pressure": item["pressure"]
                        }
                        for item in df_dict
                    ]
                    aggregate_data['daily_avg'] = formatted_dict
            
                # Return the JSON response
                return jsonify({
                    "data": aggregate_data
                }), HTTPStatus.OK

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

                aggregate = request.args.get('aggregate')
                if aggregate and len(result)>0:
                    df = pd.DataFrame(result)[['sensor_id','timestamp','temperature','pressure','humidity']]
                    print("Data", df)
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    aggregate_data = {}

                    if 'hourly' in aggregate:
                        df_grouped = df.groupby(['sensor_id', df['timestamp'].dt.hour]).mean().round(2)
                        df_grouped = df_grouped.rename_axis(['sensor_id', 'date']).reset_index()
                        df_dict = df_grouped.to_dict(orient='records')

                        # Format dictionary to include sensor_id in values
                        formatted_dict = [
                            {
                                "sensor_id": item["sensor_id"],
                                "date": str(item["timestamp"]),
                                "temperature": item["temperature"],
                                "humidity": item["humidity"],
                                "pressure": item["pressure"]
                            }
                            for item in df_dict
                        ]
                        aggregate_data['hourly_avg'] = formatted_dict

                    if 'daily' in aggregate:
                        df_grouped = df.groupby(['sensor_id', df['timestamp'].dt.date]).mean().round(2)
                        df_grouped = df_grouped.rename_axis(['sensor_id', 'date']).reset_index()
                        # Convert to dictionary format
                        df_dict = df_grouped.to_dict(orient='records')
                        formatted_dict = [
                            {
                                "sensor_id": item["sensor_id"],
                                "date": str(item["timestamp"].date()),
                                "temperature": item["temperature"],
                                "humidity": item["humidity"],
                                "pressure": item["pressure"]
                            }
                            for item in df_dict
                        ]
                        aggregate_data['daily_avg'] = formatted_dict
                
                    # Return the JSON response
                    return jsonify({
                        "data": aggregate_data
                    }), HTTPStatus.OK
                
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
            
    def put(self, id):
        # override sensor_schema many to false as we only working with 1 entry here
        sensor_schema = SensorSchema(many=False)
        if id is None:
            return jsonify({"message": "Invalid request", "error": "Sensor id is required"}), HTTPStatus.BAD_REQUEST
        else:
            try:
                json_data = request.args
                if len(json_data) >0:
                    sensor_data = Sensor.query.filter_by(id = id).first()
                    if sensor_data:
                        # check and update
                        if json_data.get('temperature', type=float):
                            sensor_data.temperature = json_data.get('temperature', type=float)
                        if json_data.get('pressure', type=float):
                            sensor_data.pressure = json_data.get('pressure', type=float)
                        if json_data.get('humidity', type=float):
                            sensor_data.humidity = json_data.get('humidity', type=float)
                        # commit the changes
                        db.session.commit()
                else:
                    # return data with id if no fileds to update
                    sensor_data = Sensor.query.filter(Sensor.id == int(id)).first()
                    
                if sensor_data is None:
                    return jsonify({"message": "Sensor data not found"}), HTTPStatus.NOT_FOUND
                
                sensor_data_serialized = sensor_schema.dump(sensor_data)
                return jsonify({"data": sensor_data_serialized}), HTTPStatus.OK
                
            except Exception as e:
                return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


class SensorAnalysisAPI(MethodView):
    def get(self):
        try:
            print("reached here")
            # data = aggregation)
            sensor_data = Sensor.query.all()
            data = sensor_schema.dump(sensor_data)
            sensor_data = aggregation(pd.DataFrame(data), aggregate_type=['daily','hourly','yearly'])
            print("Sensor data", sensor_data)
            return jsonify({'data':sensor_data}), HTTPStatus.OK
        except Exception as e:
            return jsonify({"message":"Internal error!"}), HTTPStatus.INTERNAL_SERVER_ERROR