# CoulombAI-Task



###  Features

- **Authentication**: Users can log in using JWT (JSON Web Tokens) for secure authentication.
- **Inject Sensor data**: Authenticate user can inject data in batch.
- **Filter and Update**: Sensor data can be fetched by filtering parameters.
- **Analysys**: Get informative insignts from sensor data using analysis api.




## Setup Instructions

### Clone the Repository

To get started, clone the repository to your local machine:

```sh
git clone https://github.com/Faizgeeky/CoulombAI-Task.git
cd CoulombAI-Task
```

### Setting Up the Django WebSocket Server



1. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

2. Setup Env varibales:
    ```sh
    export FLASK_APP=app.py
    export FLASK_DEBUG=1
    ```
3. Config env variable [Currently it is defined in confg.py that can be use din env var]
 ```sh
    export SECRET_KEY = 'jkbkjbvc-bkjbjkb-jka-kjbjkbkbda'
    export JWT_SECRET_KEY = 'kjbjkaebk-kjbjba-kjbajb'  
    ```

###   🚀🚀 Ready to launch your server

4. Run flask server:
    ```sh
    flask run
    ```

### API's

 ```sh
    /auth/register
    /auth/login

    /v1/data/ // POST & GET Sensor data injection and filtering 
    /v1/data/<sensor_id> // Retrive Sensor data by sensor_id
    /v1/data/<id> // PUT update sensor data
    /v1/data/aggregate // GET - all you want to know about sensor data
    ``` 

### Postman Collection

A `CoulombAI.postman_collection.json` file is included for easy testing of the API endpoints with Postman. Simply import this file into Postman to get started.

### File strcuture

  |-app.py  (entry point and regiterd all blueprints)
  |-config.py  (configurations and env variables - can be stored in env for better security)
  |-requirements.txt  
  |-extension.py  (to keep all 3rd party modeuls at one place)
  |-instance
     |-app.db (database)
  |-api
     |-model.py (User and Sensor database model defined)
     |-route 
        |- auth.py (auth routes)
        |- sensor.py (sensor routes)
        |- views.py (bussiness logic)
     |-schema (used marsmallow seriaizers)
        |- user.py
        |-sensor.py
    
### API Postman collection

* It has all the api's endpoint with request and response
* You can import it in postman and use it to test the api's

## NOTE

* There are some filters might be missing in collection but you can add in filter 
for example
 ```sh
 /v1/data/?sensor_id=1&start_date=2022-01

    //  You can pass many filters here as per task like start_date, end_date, aggregate =['hourly','daily'] , pressure, temperature
 ```

### Enhancement 
1. Handling large data injest asynly while storing 
2. Data analysis - can get more details about sensor like , predictive analysis , correlation over time , increment or decrement by month , year , etc 



     