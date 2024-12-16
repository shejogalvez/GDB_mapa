import db
from main import app, UPLOAD_DIR
from fastapi.testclient import TestClient
from test.json_examples import *
import os, os.path

TEST_DB_NAME = "test"

def init():
    init_test_db_query = f"CREATE DATABASE {TEST_DB_NAME} IF NOT EXISTS"
    db.run_query(init_test_db_query, database_ = None)

## TODO: add new database for testing

test_client = TestClient(app)
# Header variables
login_token = ""
admin_token = ""

piece_created_id = None
exposicion_id = None

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
    print(response)
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
    db.delete_node_by_id_key(["user"], "username", CREATE_USER["username"])
    response = test_client.get("/user/" + query_parameters)
    assert not response.json()

## main test
def test_create_piece_full():
    global piece_created_id
    response = test_client.put("/add-piece", headers={"Authorization": admin_token}, data=CREATE_PIECE_FORM, files=None)
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    piece_created_id = data[0]['id']
    assert len(data) == 2
    assert data[0]['pieza']['id'] == CREATE_PIECE_BODY['properties']['id']
    assert data[1]['componente'] == CREATE_PIECE_BODY['components'][0]['properties']

def test_create_component():
    CREATE_COMPONENT_FORM['piece_id'] = piece_created_id
    print(CREATE_COMPONENT_FORM)
    response = test_client.put("/add-component", headers={"Authorization": admin_token}, data=CREATE_COMPONENT_FORM, files=None)
    print(response.json())
    assert response.status_code == 200

def test_get_piezas_no_filters():
    response = test_client.post("/pieces", headers={"Authorization": admin_token}, json={})
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 50

def test_get_piezas_with_match_id_filter():
    response = test_client.post("/pieces", headers={"Authorization": admin_token}, json=FILTERS_0, files=None)
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data[1]['count'] == 1

def test_get_piezas_with_multi_no_intersection_filters():
    response = test_client.post("/pieces", headers={"Authorization": admin_token}, json=FILTERS_1, files=None)
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 50

def test_get_piezas_with_single_filter():
    response = test_client.post("/pieces", headers={"Authorization": admin_token}, json=FILTERS_1, files=None)
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 50

def test_create_exposicion():
    request_body = {
        "piezas_element_ids": [piece_created_id],
        "properties": {
            "name": "Sellos de excelencia a la Artesanía Chile. 10 años de creación",
            "fecha": "Noviembre de 2018 - marzo 2019",
            "lugar_de_exposicion": "Sala MAPA/GAM",
        },
    }
    response = test_client.put("/exposicion", headers={"Authorization": admin_token}, json=request_body)
    assert response.status_code == 200
    response = test_client.get("/nodes")

def test_get_piece_and_components():
    response = test_client.get("/components", headers={"Authorization": admin_token}, params={"piece_id": piece_created_id})
    assert response.status_code == 200
    piece, components = response.json()
    assert len(components) == 2
    assert piece["exposicion"]["name"] == "Sellos de excelencia a la Artesanía Chile. 10 años de creación"
    assert any([c["ubicacion"] for c in components])
    

def test_delete_pieza():
    response = test_client.delete("/pieces", headers={"Authorization": admin_token}, params={"node_id": "12345"})
    print(response.json())
    assert response.status_code == 200

def test_delete_exposicion():
    response = test_client.delete("/nodes/id", headers={"Authorization": admin_token}, 
                                  params={"label": 'exposicion',
                                          'key': 'name',
                                          'val': 'Sellos de excelencia a la Artesanía Chile. 10 años de creación'
                                        })
    print(response.json())
    assert response.status_code == 200

def test_create_pieza_with_image():
    files_count = len(os.listdir(UPLOAD_DIR))
    with open(os.path.join("test", "apple.jpg"), "rb") as f:
        print(f)
        files = [("images", f)]
        response = test_client.put("/add-piece", headers={"Authorization": admin_token},
                                data=CREATE_PIECE_FORM,
                                files=files
                                )
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['pieza']['id'] == CREATE_PIECE_BODY['properties']['id']
    assert data[1]['componente'] == CREATE_PIECE_BODY['components'][0]['properties']
    new_files_count = len(os.listdir(UPLOAD_DIR))
    assert new_files_count == files_count + 1

def test_delete_pieza_with_image():
    files_count = len(os.listdir(UPLOAD_DIR))
    response = test_client.delete("/pieces", headers={"Authorization": admin_token}, params={"node_id": "12345"})
    print(response.json())
    assert response.status_code == 200
    new_files_count = len(os.listdir(UPLOAD_DIR))
    assert new_files_count == files_count - 1

def test_get_non_existant_label_nodes():
    response = test_client.get("/nodes", headers={"Authorization": admin_token}, params={"labels": ['made_up_label']})
    assert response.status_code == 422

def test_get_no_intersection_labels_nodes():
    response = test_client.get("/nodes", headers={"Authorization": admin_token}, params={"labels": ['pieza', 'exposicion']})
    data = response.json()
    print(data)
    assert response.status_code == 200
    assert not data

