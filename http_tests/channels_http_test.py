import pytest
import requests
import json
from src import config
from src.helper import create_token, token_decode, load_data, get_channel, channel_exists, get_channel_listformat
from src.other import clear_v1
import src.data as d

@pytest.fixture
def case1():
    """
    creates 4 users and 3 channels for testing

    """
    clear_v1()
    user1 = requests.post(f"{config.url}/auth/register/v2", json={
        "email" : "email@gmail.com",
        "password" : "password",
        "name_first" : "Alex",
        "name_last" : "Fulton",
    })
    user2 = requests.post(f"{config.url}/auth/register/v2", json={
        "email" : "email2@gmail.com",
        "password" : "password123",
        "name_first" : "Nadya",
        "name_last" : "Ulibasa",
    })
    channel1 = requests.post(f"{config.url}/channels/create/v2", json={
        "token": create_token("alexfulton"),
        "name" : "Channel1",
        "is_public" : True,
    })
    channel2 = requests.post(f"{config.url}/channels/create/v2", json={
        "token": create_token("nadyaulibasa"),
        "name" : "Channel2",
        "is_public" : True,
    })
    channel3 = requests.post(f"{config.url}/channels/create/v2", json={
        "token": create_token("alexfulton"),
        "name" : "Channel3",
        "is_public" : False,
    })

    return {
        'user1' : json.loads(user1.text),
        'user2' : json.loads(user2.text),
        'channel1' : json.loads(channel1.text),
        'channel2' : json.loads(channel2.text),
        'channel3' : json.loads(channel3.text),
    }


def test_channels_create():
    '''
    Tests the create function. Creates a user and tests to see if they exist

    '''
    clear_v1()
    d.data = load_data()
    requests.delete(f"{config.url}/clear/v1")
    requests.post(f"{config.url}/auth/register/v2", json={
        "email" : "email@gmail.com",
        "password" : "password",
        "name_first" : "Alex",
        "name_last" : "Fulton",
    })
    channel1 = requests.post(f"{config.url}/channels/create/v2", json={
        "token": create_token("alexfulton"),
        "name" : "Channel1",
        "is_public" : True,
    })
    data = json.loads(channel1.text)
    assert channel_exists(data["channel_id"])

def test_channels_create_exception(case1):
    """
    tests if the exception handeling by the server works when a name with
    more than 20 characters is entered.

    """
    r = requests.post(f"{config.url}/channels/create/v2", json={
        "token": create_token("alexfulton"),
        "name" : "a name that is too long",
        "is_public" : True,
    })
    data = json.loads(r.text)
    assert data['code'] == 400

def test_channels_list(case1):
    """
    tests using the fixture that thr channels_list function returns a list
    of only channels that the user is in.

    """
    d.data = load_data()
    channels = requests.get(f"{config.url}/channels/list/v2", params={
        "token" : create_token("alexfulton")
    })
    data = json.loads(channels.text)
    assert get_channel_listformat(case1["channel1"]['channel_id']) in data['channels']
    assert get_channel_listformat(case1["channel2"]['channel_id']) not in data['channels']
    assert get_channel_listformat(case1["channel3"]['channel_id']) in data['channels']

def test_channels_list_exception(case1):
    """
    raises and tests an access error.

    """
    r = requests.get(f"{config.url}/channels/list/v2", params={
        "token" : 999
    })
    data = json.loads(r.text)
    assert data['code'] == 403

def test_channels_list_all(case1):
    """
    tests that a list of all channels is returned

    """
    d.data = load_data()
    channels = requests.get(f"{config.url}/channels/listall/v2", params={
        "token" : create_token("alexfulton")
    })
    data = json.loads(channels.text)
    assert get_channel_listformat(case1["channel1"]['channel_id']) in data['channels']
    assert get_channel_listformat(case1["channel2"]['channel_id']) in data['channels']
    assert get_channel_listformat(case1["channel3"]['channel_id']) in data['channels']

def test_channels_list_all_exception(case1):
    """
    raises and tests an access error.

    """
    r = requests.get(f"{config.url}/channels/listall/v2", params={
        "token" : 999
    })
    data = json.loads(r.text)
    assert data['code'] == 403
    