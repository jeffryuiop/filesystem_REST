import requests
import time

def login():
    data = {"username": "johndoe", "password": "secret"}
    r = requests.post("http://127.0.0.1:8000/token", data=data)
    auth_token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers

headers = login()
uri = "http://127.0.0.1:8000"
# uri = "http://0.0.0.0:80"

def test_ping():
    response = requests.get(uri+"/ping", headers=headers)
    assert response.status_code == 200

def test_retrieve():
    url = uri+'/retrieve/static'
    resp = requests.get(url=url, headers=headers)
    assert resp.status_code == 200

    url = uri+'/retrieve/static/favicon.png'
    resp = requests.get(url=url, headers=headers)
    assert resp.status_code == 200

    url = uri+'/retrieve/static/?orderBy=size&orderByDirection=ascending&filterByName=swagger'
    resp = requests.get(url=url, headers=headers)
    assert resp.status_code == 200


def test_upload_filestream():
    with open("samples/bean.jpg", "rb") as f:
        data = f.read()
    url = uri+'/uploadFileStream/outputs/bean.jpg'
    
    # headers = {"filesize": str(len(data))}
    headers["filesize"] = str(len(data))

    start = time.time()
    resp = requests.post(url=url, data=data, headers=headers)
    end = time.time() - start
    # print(resp.json()) 
    # print(end)
    assert resp.status_code == 200
    assert resp.json() == {"message": "Successfuly uploaded"}

def test_upload_file():
    file = {'file': open('samples/bean2.jpg', 'rb')}
    url = uri+'/uploadFile/outputs/bean2.jpg'

    start = time.time()
    resp = requests.post(url=url, files=file, headers=headers)
    end = time.time() - start
    # print(resp.json())
    # print(end)
    assert resp.status_code == 200
    assert resp.json() == {"message": "Successfuly uploaded"}

def test_update_filestream():
    with open("samples/bean2.jpg", "rb") as f:
        data = f.read()
    url = uri+'/updateFileStream/outputs/bean.jpg'

    # headers = {"filesize": str(len(data))}
    headers["filesize"] = str(len(data))

    start = time.time()
    resp = requests.patch(url=url, data=data, headers=headers)
    end = time.time() - start
    assert resp.status_code == 200
    assert resp.json() == {"message": "Successfuly updated"}
    # print(resp.json())

def test_update_file():
    file = {'file': open('samples/bean.jpg', 'rb')}
    url = uri+'/updateFile/outputs/bean2.jpg'

    start = time.time()
    resp = requests.patch(url=url, files=file, headers=headers)
    end = time.time() - start
    assert resp.status_code == 200
    assert resp.json() == {"message": "Successfuly updated"}
    # print(resp.json())

def test_delete():
    url = uri+'/deleteFile/outputs/bean.jpg'
    resp = requests.delete(url=url, headers=headers)
    assert resp.status_code == 200
    url = uri+'/deleteFile/outputs/bean2.jpg'
    resp = requests.delete(url=url, headers=headers)
    assert resp.status_code == 200

# if __name__ == "__main__":
#     test_ping()
#     test_upload_filestream()
#     test_upload_file()
#     test_update_filestream()
#     test_update_file()
#     test_delete()