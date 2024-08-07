### Basic Test Case Design for CoulombAI-Task Sensor app


## * AUTH Test Cases

#### 1. Test Case: User Registration

**Test Case Name**: `test_register_route`

- **Input**:
  ```json
  {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "password123"
  }
  ```

- **Expected Output**:
  ```json
  {
    "message": "User registered successfully"
  }
  ```

- **Steps**:
  1. Send a POST request to `/auth/register` with the input data.
  2. Verify that the response status code is `201`.
  3. Verify that the response message is `"User registered successfully"`.

#### 2. Test Case: Register Existing User

**Test Case Name**: `test_register_route_existing_user`

- **Input**:
  ```json
  {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "password123"
  }
  ```

- **Expected Output**:
  ```json
  {
    "message": "User already exists"
  }
  ```

- **Steps**:
  1. Ensure a user with the email `"testuser@example.com"` already exists.
  2. Send a POST request to `/auth/register` with the input data.
  3. Verify that the response status code is `400`.
  4. Verify that the response message is `"User already exists"`.

#### 3. Test Case: User Login

**Test Case Name**: `test_login_route`

- **Input**:
  ```json
  {
    "email": "testuser@example.com",
    "password": "password123"
  }
  ```

- **Expected Output**:
  ```json
  {
    "access_token": "<token>",
    "refresh_token": "<token>"
  }
  ```

- **Steps**:
  1. Send a POST request to `/auth/login` with the input data.
  2. Verify that the response status code is `200`.
  3. Verify that the response contains `access_token` and `refresh_token`.

#### 4. Test Case: Invalid User Login

**Test Case Name**: `test_login_invalid_user_route`

- **Input**:
  ```json
  {
    "email": "testuser@example.com",
    "password": "wrongpassword"
  }
  ```

- **Expected Output**:
  ```json
  {
    "message": "Invalid email or password"
  }
  ```

- **Steps**:
  1. Send a POST request to `/auth/login` with the input data.
  2. Verify that the response status code is `401`.
  3. Verify that the response message is `"Invalid email or password"`.


## * Sensor API 

#### Test Case: Fetch Sensor Data Without Sensor ID

**Test Case Name**: `test_sensor_fetch_api`

- **Input**:
  - Request Headers:
    ```
    {
      'Authorization': 'Bearer <auth_token>'
    }
    ```
  - Endpoint: `/v1/data`
  - Method: `GET`

- **Expected Output**:
  ```json
  {
    "data": [<sensor_data_objects>]
  }
  ```

- **Steps**:
  1. Obtain an access token using a valid login.
  2. Send a GET request to `/v1/data` with the authorization token in the headers.
  3. Verify that the response status code is `200`.
  4. Verify that the response contains a `data` field with sensor data objects.

#### Test Case: Fetch Sensor Data By Sensor ID

**Test Case Name**: `test_sensor_fetch_by_sensor_id_api`

- **Input**:
  - Request Headers:
    ```
    {
      'Authorization': 'Bearer <auth_token>'
    }
    ```
  - Endpoint: `/v1/data/sensor_test_2`
  - Method: `GET`

- **Expected Output**:
  ```json
  {
    "data": [<sensor_data_objects>]
  }
  ```

- **Steps**:
  1. Obtain an access token using a valid login.
  2. Send a GET request to `/v1/data/sensor_test_2` with the authorization token in the headers.
  3. Verify that the response status code is `200`.
  4. Verify that the response contains a `data` field with sensor data objects.

#### Test Case: Fetch Sensor Data By Parameters

**Test Case Name**: `test_sensor_fetch_by_params`

- **Input**:
  - Request Headers:
    ```
    {
      'Authorization': 'Bearer <auth_token>'
    }
    ```
  - Endpoint: `/v1/data`
  - Method: `GET`
  - Query Parameters:
    ```json
    {
      "aggregate": ["monthly", "hourly"],
      "per_page": 10,
      "page": 1,
      "start_time": "2022-08-20T17:30:00",
      'end_time': '2022-09-21T23:59:59',
      'min_humidity': 40,
      'max_humidity': 60,
      'min_pressure': 380,
      'max_pressure': 400,
      'min_temperature': 20.0,
      'max_temperature': 30.0
    }
    ```
    (additional optional parameters can be uncommented and included as needed)

- **Expected Output**:
  ```json
  {
    "data": [<sensor_data_objects>],
    "pagination": {
      "total": <total_items>,
      "pages": <total_pages>,
      "current_page": <current_page>,
      "next_page": <next_page>,
      "prev_page": <prev_page>,
      "per_page": <items_per_page>
    }
  }
  ```

- **Steps**:
  1. Obtain an access token using a valid login.
  2. Send a GET request to `/v1/data` with the authorization token in the headers and the query parameters.
  3. Verify that the response status code is `200`.
  4. Verify that the response contains a `data` field with sensor data objects and pagination information.


# Update Sensor Data



**Test Case Name**: `test_update_sensor_data`

- **Input**:
  - Request Headers:
    ```
    {
      'Authorization': 'Bearer <auth_token>'
    }
    ```
  - Endpoint: `/v1/data`
  - Method: `POST`
  - Request Body:
    ```json
    [
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
    ]
    ```

  - Endpoint: `/v1/data/1`
  - Method: `PUT`
  - Params:
    ```json
    params = {
        'humidity':'122',
        'temperature' :'32',
        'pressure' :'232' 
    }
    ```

- **Expected Output**:
  ```json
  {
    "message": "Data updated successfully"
  }
.
- **Steps**:
  1. Obtain an access token using a valid login.
  2. Send a POST request to `/v1/data/` with the authorization token in the headers and body with senor data.
  3. Send a PUT request to `/v1/data/{id}` with the authorization token in the headers and parms to update with correct sensor data id in url.
  4. Verify that the response status code is `201`.
  5. Verify that the response contains a `message` should be `Data updated successfully`.
  
  
  ## * Sensor Analytics API
  
  
## Test Case: Analytics with No Filters

**Test Case Name**: `test_analytic_with_no_filters_api`

- **Input**:
  - Request Headers:
    ```
    {
      'Authorization': 'Bearer <auth_token>'
    }
    ```
  - Endpoint: `/v1/data/aggregate`
  - Method: `GET`
  - Params: {'aggregate':['hourly','daily','yearly'], 'start_date':{},'end_date':{}}
  - Request Body: `[]` (empty list)

- **Expected Output**:
  ```json
  {
    {
    "data": {
        "daily_avg": [
            {
                "humidity": 49.5,
                "pressure": 383.25,
                "temperature": 22.2,
                "timestamp": "Tue, 20 Sep 2022 17:30:00 GMT"
            },
            {
                "humidity": 4.5,
                "pressure": 873.25,
                "temperature": 77.0,
                "timestamp": "Wed, 21 Sep 2022 17:30:00 GMT"
            }
        ],
        "hourly_avg": [
            {
                "humidity": 27.0,
                "pressure": 628.25,
                "temperature": 49.6,
                "timestamp": "Wed, 21 Sep 2022 05:30:00 GMT"
            }
        ],
        "yearly_avg": [
            {
                "humidity": 27.0,
                "pressure": 628.25,
                "temperature": 49.6,
                "timestamp": "Wed, 21 Sep 2022 05:30:00 GMT"
            }
        ]
    },
    "pagination": {
        "current_page": 1,
        "next_page": 2,
        "pages": 2,
        "per_page": 2,
        "prev_page": null,
        "total": 4
    }
}
  }
  .```
  .
- **Steps**:
  1. Obtain an access token using a valid login.
  2. Send a GET request to /v1/data/aggregate with the authorization token in the headers and an empty    3. list as the request body.
  4. Print the response status code to the console.
  5. Verify that the response status code is 200.
  6. Verify that the response contains a key 'data' in the JSON body.
  

