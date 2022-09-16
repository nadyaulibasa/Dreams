import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.helper import create_token
import src.data as d

@pytest.fixture
def Case1():
    clear_v1()
    requests.post(f"{config.url}/auth/register/v2", json = {"email":"email2@gmail.com", "password":"password2", "name_first":"David", "name_last":"Peng"})
    requests.post(f"{config.url}/auth/register/v2", json = {"email":"email3@gmail.com", "password":"password3", "name_first":"Kirshnan", "name_last":"Winter"})
    requests.post(f"{config.url}/auth/register/v2", json = {"email":"email4@gmail.com", "password":"password4", "name_first":"Joel", "name_last":"Engelman"})
    requests.post(f"{config.url}/auth/register/v2", json = {"email":"email@gmail.com", "password":"password1", "name_first":"David", "name_last":"Peng"})

def test_details_no_DM():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': 'Peng',
    }
    requests.post(f"{config.url}/auth/register/v2", json = user_data)
    r = requests.get(f"{config.url}/dm/details/v1", params={'token':create_token("davidpeng"), 'dm_id': 100})
    data = json.loads(r.text)
    assert data['code'] == 400

def test_details_no_Auth(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    r = requests.get(f"{config.url}/dm/details/v1", params={'token':create_token("davidpeng0"), 'dm_id': 0})
    data = json.loads(r.text)
    print(d.data)
    assert data['code'] == 403

def test_details_no_Token(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    r = requests.get(f"{config.url}/dm/details/v1", params={'token': "OAIEFNIOAENOAE", 'dm_id': 0})
    data = json.loads(r.text)
    print(d.data)
    assert data['code'] == 403

def test_details_valid(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    r = requests.get(f"{config.url}/dm/details/v1", params={'token':create_token("davidpeng"), 'dm_id': 0})
    data = json.loads(r.text)
    print(data)
    assert data == {
        'name': "davidpeng, joelengelman, kirshnanwinter",
        'members': [{'email': 'email3@gmail.com',
                    'handle_str': 'kirshnanwinter',
                    'name_first': 'Kirshnan',
                    'name_last': 'Winter',
                    'u_id': 1},
                    {'email': 'email4@gmail.com',
                    'handle_str': 'joelengelman',
                    'name_first': 'Joel',
                    'name_last': 'Engelman',
                    'u_id': 2},
                    {'email': 'email2@gmail.com',
                    'handle_str': 'davidpeng',
                    'name_first': 'David',
                    'name_last': 'Peng',
                    'u_id': 0}]}

def test_list_no_DM(Case1):
    r = requests.get(f"{config.url}/dm/list/v1", params={'token':create_token("davidpeng")})
    data = json.loads(r.text)
    assert data == {"dms": []}

def test_list_yes_DM(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    r = requests.get(f"{config.url}/dm/list/v1", params={'token':create_token("davidpeng")})
    data = json.loads(r.text)
    assert data == {'dms': [{'dm_id': 0, 'name': 'davidpeng, joelengelman, kirshnanwinter'}]}

def test_list_no_Token(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    r = requests.get(f"{config.url}/dm/details/v1", params={'token': "OAIEFNIOAENOAE", 'dm_id': 0})
    data = json.loads(r.text)
    print(d.data)
    assert data['code'] == 403

def test_create_invalidID(Case1):
    uids = [1, 2, 500]
    r = requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})   
    data = json.loads(r.text)
    assert data['code'] == 400

def test_create_no_Token(Case1):
    uids = [1, 2, 3]
    r = requests.post(f"{config.url}/dm/create/v1", json = {"token": "AOINFOIEFIONAEI", "uids": uids})   
    data = json.loads(r.text)
    assert data['code'] == 403

def test_create_valid(Case1):
    uids = [1, 2, 3]
    r = requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids})   
    data = json.loads(r.text)
    assert data['dm_id'] == 0
    assert data['dm_name'] == 'davidpeng, davidpeng0, joelengelman, kirshnanwinter'

def test_remove_notCreator(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    r = requests.delete(f"{config.url}/dm/remove/v1", json = {"token":create_token("kirshnanwinter"), "dm_id": 0})
    data = json.loads(r.text)
    assert data['code'] == 403

def test_remove_no_Token(Case1):
    uids = [1, 2, 3]
    requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids})   
    r = requests.delete(f"{config.url}/dm/remove/v1", json = {"token": "AEFEAOFNAFOAEI", "dm_id": 0})
    data = json.loads(r.text)
    assert data['code'] == 403

def test_remove_valid(Case1):
    uids = [1, 2, 3]
    requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids}) 
    r = requests.delete(f"{config.url}/dm/remove/v1", json = {"token":create_token("davidpeng"), "dm_id": 0})  
    data = json.loads(r.text)
    assert data == {}

def test_invite_notMember(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    r = requests.post(f"{config.url}/dm/invite/v1", json = {"token":create_token("davidpeng0"), "dm_id": 0, "u_id":3})
    data = json.loads(r.text)
    assert data['code'] == 403

def test_invite_noToken(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    r = requests.post(f"{config.url}/dm/invite/v1", json = {"token":"AOFNOAEIFNOIAEFNOAE", "dm_id": 0, "u_id": 3})
    data = json.loads(r.text)
    assert data['code'] == 403

def test_invite_inactive(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids}) 
    requests.delete(f"{config.url}/dm/remove/v1", json = {"token":create_token("davidpeng"), "dm_id": 0}) 
    r = requests.post(f"{config.url}/dm/invite/v1", json = {"token":create_token("davidpeng"), "dm_id": 0, "u_id": 3})  
    data = json.loads(r.text)
    assert data['code'] == 400

def test_invite_valid(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids}) 
    r = requests.post(f"{config.url}/dm/invite/v1", json = {"token":create_token("davidpeng"), "dm_id": 0, "u_id":3})  
    data = json.loads(r.text)
    assert data == {}

def test_leave_notMember(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    r = requests.post(f"{config.url}/dm/leave/v1", json = {"token":create_token("davidpeng0"), "dm_id": 0})
    data = json.loads(r.text)
    assert data['code'] == 403

def test_leave_inactive(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    requests.delete(f"{config.url}/dm/remove/v1", json = {"token":create_token("davidpeng"), "dm_id": 0}) 
    r = requests.post(f"{config.url}/dm/leave/v1", json = {"token":create_token("davidpeng0"), "dm_id": 0})
    data = json.loads(r.text)
    assert data['code'] == 400

def test_leave_noToken(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    r = requests.post(f"{config.url}/dm/leave/v1", json = {"token":"AOFNOAEIFNOIAEFNOAE", "dm_id": 0})
    data = json.loads(r.text)
    assert data['code'] == 403

def test_leave_valid(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    r = requests.post(f"{config.url}/dm/leave/v1", json = {"token":create_token("joelengelman"), "dm_id": 0})
    data = json.loads(r.text)
    assert data == {}

def test_message_valid(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    requests.post(f"{config.url}/message/senddm/v1", json = {"token":create_token("davidpeng"), "dm_id": 0, "message": "Hello World"})
    r = requests.get(f"{config.url}/dm/messages/v1", params={'token':create_token("davidpeng"), 'dm_id': 0, 'start': 0})
    data = json.loads(r.text)
    print(data)
    assert data['start'] == 0
    assert data['end'] == -1

def test_message_outofboundsStart(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    requests.post(f"{config.url}/message/senddm/v1", json = {"token":create_token("davidpeng"), "dm_id": 0, "message": "Hello World"})
    r = requests.get(f"{config.url}/dm/messages/v1", params={'token':create_token("davidpeng"), 'dm_id': 0, 'start': 50})
    data = json.loads(r.text)
    assert data['code'] == 400

def test_message_noToken(Case1):
    uids = [1, 2]
    requests.post(f"{config.url}/dm/create/v1", json = {"token":create_token("davidpeng"), "uids": uids})
    requests.post(f"{config.url}/message/senddm/v1", json = {"token":create_token("davidpeng"), "dm_id": 0, "message": "Hello World"})
    r = requests.get(f"{config.url}/dm/messages/v1", params={'token':"AFUBAEIFBAIEF", 'dm_id': 0, 'start': 0})
    data = json.loads(r.text)
    assert data['code'] == 403

def test_message_noDM(Case1):
    uids = [1, 2]
    token = create_token("davidpeng")
    requests.post(f"{config.url}/dm/create/v1", json = {"token":token, "uids": uids})
    requests.post(f"{config.url}/message/senddm/v1", json = {"token":token, "dm_id": 0, "message": "Hello World"})
    r = requests.get(f"{config.url}/dm/messages/v1", params={'token':token, 'dm_id': 5000, 'start': 0})
    data = json.loads(r.text)
    assert data['code'] == 400

def test_message_DMremoved(Case1):
    uids = [1, 2]
    token = create_token("davidpeng")
    requests.post(f"{config.url}/dm/create/v1", json = {"token":token, "uids": uids})
    requests.post(f"{config.url}/message/senddm/v1", json = {"token":token, "dm_id": 0, "message": "Hello World"})
    requests.delete(f"{config.url}/dm/remove/v1", json = {"token":create_token("davidpeng"), "dm_id": 0}) 
    r = requests.get(f"{config.url}/dm/messages/v1", params={'token':token, 'dm_id': 5000, 'start': 0})
    data = json.loads(r.text)
    assert data['code'] == 400