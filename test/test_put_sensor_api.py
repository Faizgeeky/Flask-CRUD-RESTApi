from .test_auth import auth_token

def test_update_sensor_data(test_client, auth_token):
    ''' Adding batch sensor data '''
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    
    response = test_client.post('/v1/data', headers=headers)
    params = {
        'humidity':'122',
        'temperature' :'32',
        'pressure' :'232' 
    }
    response = test_client.put('/v1/data/1', query_string=params, headers=headers)

    assert response.status_code == 201  
    data = response.get_json()
    assert data['message'] == 'Data updated successfully'



def test_update_sensor_data_incorrect_id(test_client, auth_token):
    ''' Adding batch sensor data '''
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    params = {
        'humidity':'122',
        'temperature' :'32',
        'pressure' :'232' 
    }
    response = test_client.put('/v1/data/500', 
    query_string=params, headers=headers)

    assert response.status_code == 404  
    data = response.get_json()
    assert data['message'] == 'Data not found'