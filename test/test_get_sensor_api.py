from .test_auth import auth_token

def test_sensor_fetch_api(test_client, auth_token):
    ''' Fetch sensor data without id'''
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    response = test_client.get('/v1/data', headers=headers)

    assert response.status_code == 200
    data =  response.get_json()
    assert 'data' in data
    

def test_sensor_fetch_by_sensor_id_api(test_client, auth_token):
    ''' fetch sensor data by sensor id'''
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    response = test_client.get('/v1/data/sensor_test_2', headers=headers)

    assert response.status_code == 200
    data =  response.get_json()
    assert 'data' in data


def test_sensor_fetch_by_params(test_client, auth_token):
    ''' fetch sensor data by params'''
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    params = {
        'aggregate': ['monthly', 'hourly'],
        'per_page': 10,
        'page': 1,
        'start_time': '2022-08-20T17:30:00',
        # 'end_time': '2022-09-21T23:59:59',
        # 'min_humidity': 40,
        # 'max_humidity': 60,
        # 'min_pressure': 380,
        # 'max_pressure': 400,
        # 'min_temperature': 20.0,
        # 'max_temperature': 30.0
    }
    response = test_client.get('/v1/data', 
                query_string =params,
                headers = headers)
    
    assert response.status_code == 200
    data =  response.get_json()
    assert 'data' in data
    