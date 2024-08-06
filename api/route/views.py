from flask import jsonify, request, current_app
from flask.views import MethodView
# keeping seprate schema for different payload 
from api.schema.sensor import SensorSchema 
from extensions import db
from api.model import Sensor
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError 
from sqlalchemy import func
import pandas as pd
from flask_jwt_extended import jwt_required

sensor_schema = SensorSchema(many=True)


def aggregation( df, aggregate_type):
        # applying aggregation
        json_data = {}
        if len(df) >0 and 'yearly' in aggregate_type:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[['timestamp','temperature','humidity', 'pressure']]
            df_year = df.groupby(df['timestamp'].dt.year).mean().round(2)
            
            # print("Datafrane mean is ", df_year)
            yearly_data = df_year.to_dict(orient='records')

            json_data['yearly_avg'] = yearly_data

        if len(df) >0 and 'hourly' in aggregate_type:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df[['timestamp','temperature','humidity', 'pressure']]
            df_hour = df.groupby(df['timestamp'].dt.hour).mean().round(2)
            
            # print("Datafrane mean is ", df_hour)
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
    
    
    def aggregate_sensor_query(self,query, aggregate):
        
        common_entities = [
            Sensor.id,
            Sensor.sensor_id,
            func.avg(Sensor.temperature).label('temperature'),
            func.avg(Sensor.humidity).label('humidity'),
            func.avg(Sensor.pressure).label('pressure'),
            Sensor.timestamp,
        ]
        
        # mention grouping and additional entities based on the aggregation type
        if 'hourly' in aggregate and 'daily' in aggregate:
            entities = common_entities + [
                func.extract('day', Sensor.timestamp).label('day'),
                func.extract('hour', Sensor.timestamp).label('hour')
            ]
            group_by = [
                Sensor.sensor_id,
                func.extract('day', Sensor.timestamp),
                func.extract('hour', Sensor.timestamp)
            ]
        elif 'hourly' in aggregate:
            entities = common_entities + [
                func.extract('hour', Sensor.timestamp).label('hour')
            ]
            group_by = [
                Sensor.sensor_id,
                func.extract('hour', Sensor.timestamp)
            ]
        elif 'daily' in aggregate:
            entities = common_entities + [
                func.extract('day', Sensor.timestamp).label('day')
            ]
            group_by = [
                Sensor.sensor_id,
                func.extract('day', Sensor.timestamp)
            ]
        elif 'monthly' in aggregate:
            entities = common_entities + [
                func.extract('month', Sensor.timestamp).label('month')
            ]
            group_by = [
                Sensor.sensor_id,
                func.extract('day', Sensor.timestamp)
            ]
        else:
            raise ValueError("Invalid aggregation type")
        
        # print("Entities and groupby")

        # Construct the query with entities, grouping, and ordering
        query = query.with_entities(*entities).group_by(*group_by).order_by(Sensor.sensor_id)
        # print("query", query)
        return query
    
    @jwt_required()
    def get(self, sensor_id=None):
        try:
            if sensor_id is None:
                json_data = request.args
                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', 10))
                offset = (page - 1) * per_page
                
                print("Aggre type", request.args.get('aggregate'))
                # Handle dynamic args to filter
                filters = self.filter_sensor_Data(json_data)
                # retured filterd sqlalchemy obj 
                query = Sensor.query.filter(*filters)
                aggregate = request.args.get('aggregate')

                if aggregate:
                    query = self.aggregate_sensor_query(query,aggregate)

                # add pagination
                paginated_data = query.paginate(page=page, per_page=per_page, error_out=False)
                # deserialize data
                result = sensor_schema.dump(paginated_data.items)
                
                return jsonify({
                    "data": result,
                    "pagination": {
                        "total": paginated_data.total,
                        "pages": paginated_data.pages,
                        "current_page": paginated_data.page,
                        "next_page": paginated_data.next_num,
                        "prev_page": paginated_data.prev_num,
                        "per_page": paginated_data.per_page
                    }
                }), HTTPStatus.OK
            else:
                try:
                    json_data = request.args
                    page = int(request.args.get('page', 1))
                    per_page = int(request.args.get('per_page', 10))
                    # Handle dynamic args to filter
                    filters = self.filter_sensor_Data(json_data, sensor_id = sensor_id)
                    # retured filterd sqlalchemy obj 
                    query = Sensor.query.filter(*filters)
        
                    aggregate = request.args.get('aggregate')
                    if aggregate:
                        query = self.aggregate_sensor_query(query,aggregate)
                    
                    # add pagination
                    paginated_data = query.paginate(page=page, per_page=per_page, error_out=False)
                    # deserialize data
                    result = sensor_schema.dump(paginated_data.items)
                    if len(result)>0:
                        return jsonify({
                            "data": result,
                            "pagination": {
                                "total": paginated_data.total,
                                "pages": paginated_data.pages,
                                "current_page": paginated_data.page,
                                "next_page": paginated_data.next_num,
                                "prev_page": paginated_data.prev_num,
                                "per_page": paginated_data.per_page
                            }
                        }), HTTPStatus.OK
                    else:
                        return jsonify({'data':[],'message':'no data found'}) , HTTPStatus.OK

                except Exception as e:
                    return jsonify({'error':str(e)}) , HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            return jsonify({'message':'Internal error','error':str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    
    @jwt_required()
    def post(self):
        try:
            json_data = request.get_json()
            sensor_data = sensor_schema.load(json_data, session=db.session)
            
            db.session.add_all(sensor_data)
            db.session.commit()
            result = sensor_schema.dump(sensor_data)
            return jsonify({"message": "Data created successfully", "data": result}), HTTPStatus.CREATED
        
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Invalid request", "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
            
    @jwt_required()
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
                    return jsonify({"message": "Data not found"}), HTTPStatus.NOT_FOUND
                
                sensor_data_serialized = sensor_schema.dump(sensor_data)
                return jsonify({"data": sensor_data_serialized, "message":"Data updated successfully"}), 201
                
            except Exception as e:
                return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

# Can be enhanced with more features like to predictive , avg, history , graph , sorting , etc
class SensorAnalysisAPI(MethodView):
    @jwt_required()
    def get(self):
        try:
            # data = aggregation)
            json_data = request.args
            # check for date filters 
            filters = []
            if json_data.get('start_date', type=str):
                filters.append(Sensor.timestamp >= json_data.get('start_date', type=str ))
            if json_data.get('end_date',type=str):
                filters.append(Sensor.timestamp <= json_data.get('end_date', type=str))
            if filters:
                paginated_data = Sensor.query.filter(*filters).paginate(page=1, per_page=2, error_out=False)
                sensor_data = paginated_data.items
            else:
                paginated_data = Sensor.query.paginate(page=1, per_page=2, error_out=False)
                sensor_data = paginated_data.items
            data = sensor_schema.dump(sensor_data)
            sensor_data = aggregation(pd.DataFrame(data), aggregate_type=['daily','hourly','yearly'])

            pagination = {
                    "current_page": paginated_data.page,
                    "next_page": paginated_data.next_num if paginated_data.has_next else None,
                    "prev_page": paginated_data.prev_num if paginated_data.has_prev else None,
                    "pages": paginated_data.pages,
                    "per_page": paginated_data.per_page,
                    "total": paginated_data.total
                }
            
            return jsonify({
                'data': sensor_data,
                'pagination': pagination
                }), HTTPStatus.OK

        except Exception as e:
            return jsonify({"message":"Internal error!"}), HTTPStatus.INTERNAL_SERVER_ERROR