import uuid
import pytest
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_register_route(test_client):
    '''Register new user'''
    logger.info("Sending POST request to /auth/register with user data.")
    response = test_client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    logger.info("Response status code: %d", response.status_code)
    assert response.status_code == 201
    data = response.get_json()
    # logger.info("Response data: %s", data)
    assert data['message'] == 'User registered successfully'


def test_register_route_existing_user(test_client):
    '''Resgister user with existing data'''
    response = test_client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    assert response.status_code == 400 
    data = response.get_json()
    assert data['message'] == 'User already exists'


def test_login_route(test_client):
    '''Login api with correct credentials'''
    response = test_client.post('/auth/login', json={
        'email':'testuser@example.com',
        'password':'password123'
    })
    assert response.status_code == 200
    data =  response.get_json()
    assert 'access_token' in data and 'refresh_token' in data


def test_login_invalid_user_route(test_client):
    '''Login api with invalid credentials'''
    response = test_client.post('/auth/login', json={
        'email': 'testuser@example.com',
        'password': 'password23'
    })
    assert response.status_code == 401
    data = response.get_json()
    assert data['message'] == 'Invalid email or password'


# Token for other unit test routes 
@pytest.fixture
def auth_token(test_client):
    # Register 
    test_client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    # Login
    response = test_client.post('/auth/login', json={
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    data = response.get_json()
    return data['access_token']