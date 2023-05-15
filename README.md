# filesystem_rest

This repository aims to provide a basic REST API service for filesystem CRUD using FastAPI on Python 3.8.   
For an easier deployment, a Dockerfile is prepared.   
Currently only support Ubuntu OS.

## Getting Started

These instructions will cover usage information and setup

### Prerequisities

As of right now, only Linux version is tested.
In order to run this container you'll need [Docker](https://docs.docker.com/linux/started/) and [Docker Compose](https://docs.docker.com/compose/install/compose-plugin/#installing-compose-on-linux-systems)

### Running the Server with Docker

1. Clone/copy the repo
2. Edit Dockerfile and/or docker-compose settings if necessary
3. At the repo's root, run:
```shell
docker compose up
```
4. Go to [http://localhost:8000/docs](http://localhost:8000/docs) to access documentation of each of the APIs and interactive UI (Swagger)

### Testing
1. install additional prerequisites to help us with tests
```shell
pip install pytest locust
```
2. [Optional] Run a basic unit test (test_main.py).     
At {root}/tests folder, run:
```shell
pytest
```   

3. [Optional] Run a basic concurrency test using locust.    
Please also make sure that {root}/src/outputs/bean2.jpg exists.   
At {root}/tests folder, run:
```shell
locust
```
to run a locust swarm test on [0.0.0.0:89](0.0.0.0:89) where we can test concurrency tests

### Features
1. Basic security:  
- OAuth2 with Password (and hashing), Bearer with JWT tokens.  
- The only endpoint that is open is /token where the user can login.  
- Right now sign up is not yet implemented. so the only user that can get a token is:  
    - username: johndoe; password: secret
2. Basic requirements are implemented as requested.
3. Can use gunicorn with uvicorn workers to create replication of processes to take advantage of multiple cores and to be able to handle more requests.
4. Additional Features:    
- For upload (POST) and update (PATCH) file to the api, 2 ways each are provided, where the user can choose to upload the stream directly or not.    
The streaming version is much faster on bigger files > 1GB but right now still cannot be tried on the Swagger UI. Although in the tests it works just fine.
- Check if file exist before upload or update or delete
- Check after upload or update if the transfer complete by comparing byte in and out
- Create intermediary folder if needed for upload
- Check if there is enough free space before transferring

### Known Issues & Future Works
1. Will fail if we try to access the same file using different endpoints. As occasionally seen in locust test result.
2. Windows is not tested, most likely will fail due to path and os operations.
3. Security features is still a basic version.  
 Not using https nor proxy like traefik or nginx.

### Acknowledgements
[FastAPI Documentations](https://fastapi.tiangolo.com/)     
[Locust](https://locust.io/)    
[Docker](https://docs.docker.com/)