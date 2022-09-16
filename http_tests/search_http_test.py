import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.helper import create_token, token_decode, valid_message, load_data, save_data
import src.data as d

@pytest.fixture
def Case1():
    clear_v1()
    requests.post(f"{config.url}/auth/register/v2", json = {"email":"email2@gmail.com", "password":"password2", "name_first":"David", "name_last":"Peng"})
    requests.post(f"{config.url}/channels/create/v2", json = {"token": create_token("davidpeng"), "name": "example channel", "is_public": True})

def test_str_query_too_long(Case1):
    requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": 1, "message": "HelloWorld"})
    r = requests.get(f"{config.url}/search/v2", params = {"token": create_token("davidpeng"), "query_str": "HelloWorld" * 500000})
    data = json.loads(r.text)
    print(data)
    assert data['code'] == 400

def test_str_query_valid(Case1):
    for _ in range(50):
        requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": 1, "message": "HelloWorld"})
    for _ in range(10):
        requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": 1, "message": "HelloWorld2"})
    r = requests.get(f"{config.url}/search/v2", params = {"token": create_token("davidpeng"), "query_str": "HelloWorld"})
    data = json.loads(r.text)
    assert len(data['messages']) == 50