from .test_auth import auth_token

def test_sensor_add_api(test_client, auth_token):
    ''' Adding batch sensor data '''
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    response = test_client.post('http://127.0.0.1:5000/v1/data', json=[
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
    
    # print("Response data:", response.data.decode('utf-8'))
    # print("Response status code:", response.status_code)
    
    assert response.status_code == 201  
    data = response.get_json()
    assert data.get('message') == 'Data created successfully'