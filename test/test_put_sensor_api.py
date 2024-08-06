from .test_auth import auth_token

def test_update_sensor_data(test_client, auth_token):
    ''' Adding batch sensor data '''
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    response = test_client.post('/v1/data', json=[
        {
            "sensor_id": "sensor_test_1",
            "timestamp": "2022-09-20T17:30:00",
            "humidity": 49.5,
            "pressure": 383.25,
            "temperature": 22.2
        },
        {
            "sensor_id": "sensor_test_2",
            "timestamp": "2022-09-21T17:30:00",
            "humidity": 4.5,
            "pressure": 873.25,
            "temperature": 77
        }
    ], headers=headers)

    
    
    response = test_client.put('/v1/data/1', json=[
        {
            "sensor_id": "sensor_test_00",
            "timestamp": "2022-09-20T17:30:00",
            "humidity": 49.5,
            "pressure": 383.25,
            "temperature": 22.444
        }
    ], headers=headers)

    assert response.status_code == 201  
    data = response.get_json()
    assert data['message'] == 'Data updated successfully'



def test_update_sensor_data_incorrect_id(test_client, auth_token):
    ''' Adding batch sensor data '''
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    
    response = test_client.put('/v1/data/500', json=[
        {
            "sensor_id": "sensor_test_00",
            "timestamp": "2022-09-20T17:30:00",
            "humidity": 49.5,
            "pressure": 383.25,
            "temperature": 22.444
        }
    ], headers=headers)

    assert response.status_code == 404  
    data = response.get_json()
    assert data['message'] == 'Data not found'