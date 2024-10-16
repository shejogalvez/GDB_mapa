import db
from main import app
from fastapi.testclient import TestClient
from test.json_examples import *

# TEST_DB_NAME = "test"

# def init():
#     init_test_db_query = f"CREATE DATABASE {TEST_DB_NAME} IF NOT EXISTS"
#     db.run_query(init_test_db_query, database_ = None)

## TODO: add new database for testing

test_client = TestClient(app)
login_token = ""
admin_token = ""

## user tests
def test_create_user_fail():
    response = test_client.post("/user", data=CREATE_USER, headers={"Authorization": login_token})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_login_admin():
    global admin_token
    new_response = test_client.post("/token", data=LOGIN_ADMIN)
    assert new_response.status_code == 200
    data = new_response.json()
    assert "access_token" in data
    admin_token = "Bearer "+data["access_token"]

def test_create_user():
    assert admin_token
    response = test_client.post("/user", data=CREATE_USER, headers={"Authorization": admin_token})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "test_reader"

def test_login_user():
    global login_token
    response = test_client.post("/token", data=WRONG_USER)
    assert response.status_code == 401
    new_response = test_client.post("/token", data=LOGIN_USER)
    assert new_response.status_code == 200
    data = new_response.json()
    assert "access_token" in data
    login_token = "Bearer "+data["access_token"]

def test_reader_user():
    response = test_client.get("/user/read-data")
    assert response.status_code == 401
    print(login_token)
    new_response = test_client.get("/user/read-data", headers={"Authorization": login_token})
    assert new_response.status_code == 200
    data = new_response.json()
    assert data["data"] == "This is read-only data"

def test_reader_user_fail():
    new_response = test_client.post("/user/write-data", headers={"Authorization": login_token})
    assert new_response.status_code == 403
    data = new_response.json()
    assert data["detail"] == "Permission denied: No write access"
    
    response = test_client.post("/user", data=CREATE_USER, headers={"Authorization": login_token})
    assert response.status_code == 403, response.text
    data = response.json()
    assert data["detail"] == "Permission denied: only administrator can access"

def test_delete_user():
    query_parameters = f"?username={CREATE_USER['username']}"
    response = test_client.get("/user/" + query_parameters)
    assert response.json()
    db.delete_user(CREATE_USER["username"])
    response = test_client.get("/user/" + query_parameters)
    assert not response.json()

## main test
def test_create_piece_full():
    response = test_client.put("/add-piece", headers={"Authorization": admin_token}, data=CREATE_PIECE_FORM, files=None)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['p']['id'] == CREATE_PIECE_BODY['id']
    assert { "funcion": "Simbólica-utilitaria", "nombre_comun": "Alfiler", "nombre_especifico": "Ketawue"} == data[1]['c']

def test_create_component():
    response = test_client.put("/add-component", headers={"Authorization": admin_token}, data=CREATE_PIECE_FORM, files=None)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['p']['id'] == CREATE_PIECE_BODY['id']
    assert { "funcion": "Simbólica-utilitaria", "nombre_comun": "Alfiler", "nombre_especifico": "Ketawue"} == data[1]['c']