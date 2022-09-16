'''
user_http_test.py
'''

import pytest
import requests
import json
from src.config import url
from src.other import clear_v1
from src.helper import create_token, get_user, load_data
import src.data as d

@pytest.fixture
def register_login():
    '''
    Fixture registers a user and then logs them in
    Returns dictionary containing their u_id and token.
    '''
    clear_v1()
    # User 1
    result1 = requests.post(url + '/auth/register/v2', json={
        "email":"email1@gmail.com", 
        "password": "password1", 
        "name_first": "Hayden", 
        "name_last": "Smith"
    })

    # User 2
    requests.post(url + '/auth/register/v2', json={
        "email":"email2@gmail.com", 
        "password": "password2", 
        "name_first": "Nadya", 
        "name_last": "Ulibasa"
    })


    payload = result1.json()
    return payload

@pytest.fixture
def setup_multiple_users():
    """
    Fixture to access and use multiple users. Used in testing for users_all, user_stats, users_stats
    """
    clear_v1()
    #d.data = load_data()
    # User 1
    user1 = requests.post(url + '/auth/register/v2', json={
        "email":"email1@gmail.com", 
        "password": "password1", 
        "name_first": "Hayden", 
        "name_last": "Smith"
    })

    # User 2
    user2 = requests.post(url + '/auth/register/v2', json={
        "email":"email2@gmail.com", 
        "password": "password2", 
        "name_first": "Nadya", 
        "name_last": "Ulibasa"
    })

    # User 3
    user3 = requests.post(url + '/auth/register/v2', json={
        "email":"email3@gmail.com", 
        "password": "password3", 
        "name_first": "Alex", 
        "name_last": "Fulton"
    })

    # Create some channels
    channel1 = requests.post(f"{url}/channels/create/v2", json={
        "token": json.loads(user1.text)["token"],
        "name" : "Channel1",
        "is_public" : True,
    })
    channel2 = requests.post(f"{url}/channels/create/v2", json={
        "token": json.loads(user1.text)["token"],
        "name" : "Channel2",
        "is_public" : False,
    })
    channel3 = requests.post(f"{url}/channels/create/v2", json={
        "token": json.loads(user2.text)["token"],
        "name" : "Channel3",
        "is_public" : True,
    })
    channel4 = requests.post(f"{url}/channels/create/v2", json={
        "token": json.loads(user2.text)["token"],
        "name" : "Channel4",
        "is_public" : True,
    })
    return {
        'user1' : json.loads(user1.text),
        'user2' : json.loads(user2.text),
        'user3' : json.loads(user3.text),
        'channel1' : json.loads(channel1.text),
        'channel2' : json.loads(channel2.text),
        'channel3' : json.loads(channel3.text),
        'channel4' : json.loads(channel4.text),
    }

##########################################################################################
# user_profile tests

def test_user_profile(register_login):
    user = register_login
    token = user['token']
    u_id = user['auth_user_id']

    res = requests.get(url + '/user/profile/v2', 
                        params={'token': token, 'u_id': u_id})

    assert json.loads(res.text) == {
        'user': {
        	'u_id': 0,
        	'email': 'email1@gmail.com',
        	'name_first': 'Hayden',
        	'name_last': 'Smith',
        	'handle_str': 'haydensmith',
        },
    }

def test_user_profile_invalid_token(register_login):
    user = register_login
    token = create_token('invalid')
    u_id = user['auth_user_id']

    res = requests.get(url + '/user/profile/v2', 
                        params={'token': token, 'u_id': u_id})
    payload = json.loads(res.text)
    assert payload['code'] == 403

def test_user_profile_invalid_uid(register_login):
    user = register_login
    token = user['token']
    u_id = 1234567

    res = requests.get(url + '/user/profile/v2', 
                        params={'token': token, 'u_id': u_id})
    payload = json.loads(res.text)
    assert payload['code'] == 400

##########################################################################################
# user_profile_setname tests

def test_user_profile_setname_valid(register_login):
    user = register_login
    token = user['token']
    u_id = user['auth_user_id']
    name_first = 'First'
    name_last = 'Last'
    
    requests.post(url + '/user/profile/setname/v2',
                        json={
                            'token': token,
                            'name_first': name_first,
                            'name_last': name_last
                        })
    
    res_test = requests.get(url + '/user/profile/v2', 
                        params={'token': token, 'u_id': u_id})
    changed_user = json.loads(res_test.text)['user']
    
    assert changed_user['name_first'] == name_first
    assert changed_user['name_last'] == name_last

    
def test_user_profile_setname_invalid_token(register_login):
    token = create_token('invalid')
    name_first = 'First'
    name_last = 'Last'
    
    res = requests.post(url + '/user/profile/setname/v2',
                        json={
                            'token': token,
                            'name_first': name_first,
                            'name_last': name_last
                        })
    payload = json.loads(res.text)

    assert payload['code'] == 403

def test_user_profile_setname_invalid_firstname1(register_login):
    user = register_login
    token = user['token']
    name_first = ''
    name_last = 'Last'
    
    res = requests.post(url + '/user/profile/setname/v2',
                        json={
                            'token': token,
                            'name_first': name_first,
                            'name_last': name_last
                        })
    payload = json.loads(res.text)

    assert payload['code'] == 400

def test_user_profile_setname_invalid_firstname2(register_login):
    user = register_login
    token = user['token']
    name_first = 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijk'
    name_last = 'Last'
    
    res = requests.post(url + '/user/profile/setname/v2',
                        json={
                            'token': token,
                            'name_first': name_first,
                            'name_last': name_last
                        })
    payload = json.loads(res.text)

    assert payload['code'] == 400

def test_user_profile_setname_invalid_lastname1(register_login):
    user = register_login
    token = user['token']
    name_first = 'First'
    name_last = ''
    
    res = requests.post(url + '/user/profile/setname/v2',
                        json={
                            'token': token,
                            'name_first': name_first,
                            'name_last': name_last
                        })
    payload = json.loads(res.text)

    assert payload['code'] == 400

def test_user_profile_setname_invalid_lastname2(register_login):
    user = register_login
    token = user['token']
    name_first = 'First'
    name_last = 'abcasdjsdjhkqwhioqwuheiqwhuekjwqdhkashdkasjhdksahjdkfnkqwjnfkqwhuriqwhsa'
    
    res = requests.post(url + '/user/profile/setname/v2',
                        json={
                            'token': token,
                            'name_first': name_first,
                            'name_last': name_last
                        })
    payload = json.loads(res.text)

    assert payload['code'] == 400

##########################################################################################
# user_profile_setemail tests

def test_user_profile_setemail_valid(register_login):
    user = register_login
    token = user['token']
    u_id = user['auth_user_id']
    email = 'mynewemail@gmail.com'
    
    requests.post(url + '/user/profile/setemail/v2',
                        json={
                            'token': token,
                            'email': email
                        })
    res_test = requests.get(url + '/user/profile/v2', 
                        params={'token': token, 'u_id': u_id})
    changed_user = json.loads(res_test.text)['user']
    
    assert changed_user['email'] == email

def test_user_profile_setemail_invalid_token(register_login):
    token = create_token('invalid')
    email = 'mynewemail@gmail.com'
    
    res = requests.post(url + '/user/profile/setemail/v2',
                        json={
                            'token': token,
                            'email': email
                        })
    payload = json.loads(res.text)

    assert payload['code'] == 403

def test_user_profile_setemail_invalid_email_format(register_login):
    user = register_login
    token = user['token']
    email = 'definitelynoatavalidEMAIL'
    
    res = requests.post(url + '/user/profile/setemail/v2',
                        json={
                            'token': token,
                            'email': email
                        })
    payload = json.loads(res.text)

    assert payload['code'] == 400

def test_user_profile_setemail_invalid_email_otheruser(register_login):
    user = register_login
    token = user['token']
    email = 'email2@gmail.com'
    
    res = requests.post(url + '/user/profile/setemail/v2',
                        json={
                            'token': token,
                            'email': email
                        })
    payload = json.loads(res.text)

    assert payload['code'] == 400

##########################################################################################
# user_profile_sethandle tests

def test_user_profile_sethandle_valid(register_login):
    user = register_login
    token = user['token']
    u_id = user['auth_user_id']
    handle_str = 'mynewhandle'
    
    res = requests.post(url + '/user/profile/sethandle/v1',
                        json={
                            'token': token,
                            'handle_str': handle_str
                        })
    payload = json.loads(res.text)
    print(payload)
    
    res_test = requests.get(url + '/user/profile/v2', 
                        params={'token': token, 'u_id': u_id})
    changed_user = json.loads(res_test.text)['user']
    
    assert changed_user['handle_str'] == handle_str

def test_user_profile_sethandle_invalid_token(register_login):
    token = create_token('invalid')
    handle_str = 'mynewhandle'
    
    res = requests.post(url + '/user/profile/sethandle/v1',
                        json={
                            'token': token,
                            'handle_str': handle_str
                        })
    payload = json.loads(res.text)

    assert payload['code'] == 403

def test_user_profile_sethandle_invalid_handle_short(register_login):
    user = register_login
    token = user['token']
    handle_str = ''
    
    res = requests.post(url + '/user/profile/sethandle/v1',
                        json={
                            'token': token,
                            'handle_str': handle_str
                        })
    payload = json.loads(res.text)

    assert payload['code'] == 400

def test_user_profile_sethandle_invalid_handle_long(register_login):
    user = register_login
    token = user['token']
    handle_str = 'thishandleiswaytoolonglollongerthan20charextraforgoodmeasure'
    
    res = requests.post(url + '/user/profile/sethandle/v1',
                        json={
                            'token': token,
                            'handle_str': handle_str
                        })
    payload = json.loads(res.text)

    assert payload['code'] == 400

def test_user_profile_sethandle_invalid_handle_otheruser(register_login):
    user = register_login
    token = user['token']
    handle_str = 'nadyaulibasa'
    
    res = requests.post(url + '/user/profile/sethandle/v1',
                        json={
                            'token': token,
                            'handle_str': handle_str
                        })
    payload = json.loads(res.text)
    print(payload)
    assert payload['code'] == 400

##########################################################################################
# user_all tests

def test_user_all(setup_multiple_users):
    d.data = load_data()
    token = setup_multiple_users['user1']['token']
    users = requests.get(f"{url}/users/all/v1", params={
        "token" : token
    })
    data = users.json()
    assert get_user(setup_multiple_users['user2']['auth_user_id']) in data['users']
    assert get_user(setup_multiple_users['user3']["auth_user_id"]) in data['users']

""" (To do when error handling is fixed)
def test_user_all_access_exception(setup_multiple_users):
    d.data = load_data()
    users = requests.get(f"{url}/users/all/v1", params={
        "token" : 999
    })
    data = users.json()
    assert data['code'] == 403
"""

##########################################################################################
# user_stats tests
def test_user_stats(setup_multiple_users):
    # User 1
    token1 = setup_multiple_users["user1"]["token"]
    u_id1 = setup_multiple_users["user1"]["auth_user_id"]
    # User 2
    token2 = setup_multiple_users["user2"]["token"]
    u_id2 = setup_multiple_users["user2"]["auth_user_id"]
    # Channels
    channel1 = setup_multiple_users["channel1"]
    channel2 = setup_multiple_users["channel2"]
    channel3 = setup_multiple_users["channel3"]
    channel4 = setup_multiple_users["channel4"]

    requests.post(f"{url}/channel/invite/v2", json={
        "token": token2,
        "channel_id": channel3["channel_id"],
        "u_id": u_id1
    })
    requests.post(f"{url}/channel/invite/v2", json={
        "token": token1,
        "channel_id": channel1["channel_id"],
        "u_id": u_id2,
    })

    # Create and send some dm's
    dm = requests.post(f"{url}/dm/create/v1", json={
        "token": token1,
        "uids": [u_id2],
    })
    dm_id = json.loads(dm.text)["dm_id"]

    requests.post(f"{url}/message/senddm/v1", json={
        "token": token1,
        "dm_id": dm_id,
        "message": "a test dm"
    })
    requests.post(f"{url}/message/senddm/v1", json={
        "token": token2,
        "dm_id": dm_id,
        "message": "a test response"
    })
    requests.post(f"{url}/message/senddm/v1", json={
        "token": token1,
        "dm_id": dm_id,
        "message": "a follow up message"
    })

    # Send some messages into channels (count 3 messages)
    requests.post(f"{url}/message/send/v2", json={
        "token": token1,
        "channel_id": channel1["channel_id"],
        "message": "hello channel 1"
    })
    requests.post(f"{url}/message/send/v2", json={
        "token": token2,
        "channel_id": channel1["channel_id"],
        "message": "hello back channel 1"
    })
    requests.post(f"{url}/message/send/v2", json={
        "token": token1,
        "channel_id": channel2["channel_id"],
        "message": "this is empty"
    })
    requests.post(f"{url}/message/send/v2", json={
        "token": token1,
        "channel_id": channel3["channel_id"],
        "message": "thanks for the invite"
    })
    requests.post(f"{url}/message/send/v2", json={
        "token": token2,
        "channel_id": channel3["channel_id"],
        "message": "no problem"
    })
    requests.post(f"{url}/message/send/v2", json={
        "token": token2,
        "channel_id": channel4["channel_id"],
        "message": "none is here"
    })
    stats = requests.get(f"{url}/user/stats/v1", params={
        "token": token1
    })
    data = stats.json()
    
    assert data["channels_joined"]["num_channels_joined"] == 3
    assert data["dms_joined"]["num_dms_joined"] == 1
    assert data["messages_sent"]["num_messages_sent"] == 5

'''(To do when error handling is fixed)
def test_user_stats_exception(setup_multiple_users):
    d.data = load_data()
    stats = requests.get(f"{url}/user/stats/v1", params={
        "token" : 999
    })
    data = stats.json()
    assert data['code'] == 403
'''
##########################################################################################
# users_stats tests
def test_users_stats(setup_multiple_users):
    # User 1
    token1 = setup_multiple_users["user1"]["token"]
    u_id1 = setup_multiple_users["user1"]["auth_user_id"]
    # User 2
    token2 = setup_multiple_users["user2"]["token"]
    u_id2 = setup_multiple_users["user2"]["auth_user_id"]
    # User 3
    u_id3 = setup_multiple_users["user3"]["auth_user_id"]
    # Channels
    channel1 = setup_multiple_users["channel1"]
    channel2 = setup_multiple_users["channel2"]
    channel3 = setup_multiple_users["channel3"]
    channel4 = setup_multiple_users["channel4"]

    requests.post(f"{url}/channel/invite/v2", json={
        "token": token2,
        "channel_id": channel3["channel_id"],
        "u_id": u_id1
    })
    requests.post(f"{url}/channel/invite/v2", json={
        "token": token1,
        "channel_id": channel1["channel_id"],
        "u_id": u_id2,
    })

    # Create and send some dm's
    dm1 = requests.post(f"{url}/dm/create/v1", json={
        "token": token1,
        "uids": [u_id2],
    })
    dm_id1 = json.loads(dm1.text)["dm_id"]
    dm2 = requests.post(f"{url}/dm/create/v1", json={
        "token": token1,
        "uids": [u_id3],
    })
    dm_id2 = json.loads(dm2.text)["dm_id"]
    dm3 = requests.post(f"{url}/dm/create/v1", json={
        "token": token2,
        "uids": [u_id3],
    })
    dm_id3 = json.loads(dm3.text)["dm_id"]

    requests.post(f"{url}/message/senddm/v1", json={
        "token": token1,
        "dm_id": dm_id1,
        "message": "a test dm"
    })
    requests.post(f"{url}/message/senddm/v1", json={
        "token": token1,
        "dm_id": dm_id2,
        "message": "a test response"
    })
    requests.post(f"{url}/message/senddm/v1", json={
        "token": token2,
        "dm_id": dm_id3,
        "message": "a follow up message"
    })

    # Send some messages into channels
    requests.post(f"{url}/message/send/v2", json={
        "token": token1,
        "channel_id": channel1["channel_id"],
        "message": "hello channel 1"
    })
    requests.post(f"{url}/message/send/v2", json={
        "token": token2,
        "channel_id": channel1["channel_id"],
        "message": "hello back channel 1"
    })
    requests.post(f"{url}/message/send/v2", json={
        "token": token1,
        "channel_id": channel2["channel_id"],
        "message": "this is empty"
    })
    requests.post(f"{url}/message/send/v2", json={
        "token": token1,
        "channel_id": channel3["channel_id"],
        "message": "thanks for the invite"
    })
    requests.post(f"{url}/message/send/v2", json={
        "token": token2,
        "channel_id": channel3["channel_id"],
        "message": "no problem"
    })
    requests.post(f"{url}/message/send/v2", json={
        "token": token2,
        "channel_id": channel4["channel_id"],
        "message": "none is here"
    })
    stats = requests.get(f"{url}/users/stats/v1", params={
        "token": token1
    })
    data = stats.json()
    
    assert data["channels_exist"]["num_channels_exist"] == 4
    assert data["dms_exist"]["num_dms_exist"] == 3
    assert data["messages_exist"]["num_messages_exist"] == 9

'''(To do when error handling is fixed)
def test_users_stats_exception(setup_multiple_users):
    d.data = load_data()
    stats = requests.get(f"{url}/users/stats/v1", params={
        "token" : 999
    })
    data = stats.json()
    assert data['code'] == 403
'''
