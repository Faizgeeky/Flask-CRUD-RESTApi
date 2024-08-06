from .test_auth import auth_token


def test_analytic_with_no_filters_api(test_client, auth_token):
    ''' Adding batch sensor data '''
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    print("Sending POST request to /v1/data with batch sensor data.")
    response = test_client.get('/v1/data/aggregate', json=[], headers=headers)
    print(f"Response status code: {response.status_code}")
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data


def test_analytic_with_no_filters_api(test_client, auth_token):
    ''' Adding batch sensor data '''
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    params = {
        'start_date' : '2022-07-01T00:00:00',
        'end_date' :'2029-07-01T00:00:00'
    }
    response = test_client.get('/v1/data/aggregate',query_string =params , headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data