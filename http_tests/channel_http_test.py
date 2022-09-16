import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.helper import create_token, token_decode, valid_message, load_data, save_data
import src.data as d

d.data = load_data()

@pytest.fixture
def Case1():
    clear_v1()
    requests.post(f"{config.url}/auth/register/v2", json = {"email":"email2@gmail.com", "password":"password2", "name_first":"David", "name_last":"Peng"})
    requests.post(f"{config.url}/auth/register/v2", json = {"email":"email3@gmail.com", "password":"password3", "name_first":"Krishnan", "name_last":"Winter"})
    requests.post(f"{config.url}/auth/register/v2", json = {"email":"email4@gmail.com", "password":"password4", "name_first":"Joel", "name_last":"Engelman"})
    CH1json = requests.post(f"{config.url}/channels/create/v2", json = {"token": create_token("davidpeng"), "name": "example channel", "is_public": True})
    CH2json = requests.post(f"{config.url}/channels/create/v2", json = {"token": create_token("krishnanwinter"), "name": "example channel2", "is_public": True})
    CH3json = requests.post(f"{config.url}/channels/create/v2", json = {"token": create_token("joelengelman"), "name": "example channel3", "is_public": False})
    CH1 = CH1json.json()
    CH2 = CH2json.json()
    CH3 = CH3json.json()
    d.data = load_data()
    return {"CH1": CH1['channel_id'], "CH2": CH2['channel_id'], "CH3": CH3['channel_id']}

# Error testing for channel_invite 

def test_channel_invite_no_user(Case1):
    r = requests.post(f"{config.url}/channel/invite/v2", json = {"token": create_token("krishnanwinter"), "channel_id": Case1["CH1"], "u_id": 999999})
    data = r.json()

    assert data['code'] == 400

def test_channel_invite_no_channel(Case1):
    r = requests.post(f"{config.url}/channel/invite/v2", json = {"token": create_token("krishnanwinter"), "channel_id": 999999, "u_id": 0})
    data = r.json()

    assert data['code'] == 400

def test_channel_invite_already_member(Case1):
    r = requests.post(f"{config.url}/channel/invite/v2", json = {"token": create_token("krishnanwinter"), "channel_id": Case1["CH2"], "u_id": 1})
    data = r.json()

    assert data['code'] == 400

def test_channel_invite_no_access(Case1):
    r = requests.post(f"{config.url}/channel/invite/v2", json = {"token": create_token("joelengelman"), "channel_id": Case1["CH2"], "u_id": 0})
    data = r.json()

    assert data['code'] == 403

def test_channel_invite_no_access_but_global(Case1):
    r = requests.post(f"{config.url}/channel/invite/v2", json = {"token": create_token("davidpeng"), "channel_id": Case1["CH2"], "u_id": 0})
    data = r.json()

    assert data == {}

# Error testing for channel_details
def test_channel_details_no_channel(Case1):
    r = requests.get(f"{config.url}/channel/details/v2", params = {"token": create_token("davidpeng"), "channel_id": 99999})
    data = r.json()

    assert data['code'] == 400

def test_channel_details_no_access(Case1):
    r = requests.get(f"{config.url}/channel/details/v2", params = {'token': create_token("krishnanwinter"), 'channel_id': Case1['CH1']})
    data = r.json()
    print(d.data)
    assert data['code'] == 403

# Error testing for channel_messages
def test_channel_messages_past_start(Case1):
    c = requests.get(f"{config.url}/channel/messages/v2", params = {'token': create_token("davidpeng"), "channel_id": Case1['CH1'], "start": 50000})
    data = c.json()

    assert data['code'] == 400

def test_channel_messages_not_member(Case1):
    c = requests.get(f"{config.url}/channel/messages/v2", params = {'token': create_token("joelengelman"), "channel_id": Case1['CH2'], "start": 0})
    data = c.json()

    assert data['code'] == 403

# Error testing for channel_join
def test_channel_join_private(Case1):
    r = requests.post(f"{config.url}/channel/join/v2", json = {'token': create_token("krishnanwinter"), 'channel_id': Case1['CH3']})
    data = r.json()

    assert data['code'] == 403

def test_channel_join_already_member(Case1):
    r = requests.post(f"{config.url}/channel/join/v2", json = {'token': create_token("davidpeng"), 'channel_id': Case1['CH1']})
    data = r.json()

    assert data['code'] == 400

def test_channel_join_no_channel(Case1):
    r = requests.post(f"{config.url}/channel/join/v2", json = {'token': create_token("davidpeng"), 'channel_id': 9999})
    data = r.json()

    assert data['code'] == 400

# Error testing for channel_addowner

def test_channel_addowner_no_channel(Case1):
    r = requests.post(f"{config.url}/channel/addowner/v1", json = {'token': create_token("davidpeng"), 'channel_id': 999999, 'u_id': 2})
    data = r.json()

    assert data['code'] == 400

def test_channel_addowner_user_already_owner(Case1):
    r = requests.post(f"{config.url}/channel/addowner/v1", json = {'token': create_token("davidpeng"), 'channel_id': Case1["CH1"], 'u_id': 0})
    data = r.json()

    assert data['code'] == 400

def test_channel_addowner_not_auth(Case1):
    requests.post(f"{config.url}/channel/join/v2", json = {'token': create_token("krishnanwinter"), 'channel_id': Case1['CH1']})
    r = requests.post(f"{config.url}/channel/addowner/v1", json = {'token': create_token("krishnanwinter"), 'channel_id': Case1["CH1"], 'u_id': 0})    
    data = r.json()

    assert data['code'] == 400

# Error testing for channel_removeowner

def test_channel_removeowner_no_channel(Case1):
    r = requests.post(f"{config.url}/channel/removeowner/v1", json = {'token': create_token("krishnanwinter"), 'channel_id': 999999, 'u_id': 0})    
    data = r.json()

    assert data['code'] == 400

def test_channel_removeowner_not_owner(Case1):
    r = requests.post(f"{config.url}/channel/removeowner/v1", json = {'token': create_token("davidpeng"), 'channel_id': Case1["CH1"], 'u_id': 0})    
    data = r.json()

    assert data['code'] == 400

def test_channel_removeowner_single_owner(Case1):
    r = requests.post(f"{config.url}/channel/removeowner/v1", json = {'token': create_token("davidpeng"), 'channel_id': Case1["CH1"], 'u_id': 0})    
    data = r.json()

    assert data['code'] == 400

def test_channel_removeowner_not_auth(Case1):
    requests.post(f"{config.url}/channel/invite/v2", json = {"token": create_token("davidpeng"), "channel_id": Case1["CH1"], "u_id": 1})
    requests.post(f"{config.url}/channel/invite/v2", json = {"token": create_token("davidpeng"), "channel_id": Case1["CH1"], "u_id": 2})

    requests.post(f"{config.url}/channel/addowner/v1", json = {'token': create_token("davidpeng"), 'channel_id': Case1["CH1"], 'u_id': 1})

    r = requests.post(f"{config.url}/channel/removeowner/v1", json = {'token': create_token("joelengelman"), 'channel_id': Case1["CH1"], 'u_id': 0})    
    data = r.json()

    assert data['code'] == 400

# Error testing for channel_leave

def test_channel_leave_invalid_channel(Case1):
    r = requests.post(f"{config.url}/channel/leave/v1", json = {'token': create_token("davidpeng"), 'channel_id': 9999})
    data = r.json()

    assert data['code'] == 400

def test_channel_leave_not_member(Case1):
    r = requests.post(f"{config.url}/channel/leave/v1", json = {'token': create_token("krishnanwinter"), 'channel_id': Case1["CH1"]})
    data = r.json()

    assert data['code'] == 403