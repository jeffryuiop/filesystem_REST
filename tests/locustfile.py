from locust import HttpUser, task, between

class TestUser(HttpUser):
    wait_time = between(0.5, 2.5)

    def login(self):
        data = {"username": "johndoe", "password": "secret"}
        r = self.client.post("http://127.0.0.1:8000/token", data=data)
        auth_token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {auth_token}"}
        return headers

    @task
    def ping(self):
        headers = self.login()
        self.client.get('/ping', headers=headers)

    @task
    def upload_and_delete(self):

        with open("samples/bean.jpg", "rb") as f:
            data = f.read()

        headers = self.login()
        # headers = {"filesize": str(len(data))}
        headers["filesize"] = str(len(data))

        self.client.post("/uploadFileStream/outputs/bean.jpg", data=data, headers=headers)
        # file = {'file': open('samples/bean.jpg', 'rb')}
        # self.client.post("/uploadFile/outputs/bean.jpg", files=file)
        
        self.client.delete('/deleteFile/outputs/bean.jpg', headers=headers)

    @task
    def update(self):
        headers = self.login()
        file = {'file': open('samples/bean.jpg', 'rb')}
        self.client.patch("/updateFile/outputs/bean2.jpg", files=file, headers=headers)

        # with open("samples/bean.jpg", "rb") as f:
        #     data = f.read()
        # self.client.patch("/updateFileStream/outputs/bean2.jpg", data=data)
    
    @task
    def retrieve(self):
        headers = self.login()
        self.client.get("/retrieve/static/", headers=headers)
        self.client.get("/retrieve/static?orderBy=size&orderByDirection=ascending&filterByName=swag", headers=headers)
        self.client.get("/retrieve/static/favicon.png", headers=headers)
