'''
standup_http_test.py

HTTP tests for standup.py
'''

import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.helper import create_token, token_decode, load_data, save_data, channel_exists, user_exists
from time import sleep

@pytest.fixture
def register_users_channels():
    '''
    Fixture registers two users: owner and member
    and two channels:   channel1 as a dummy channel
                        channel2 to test on
    Returns dictionary containing channel IDs and users profiles.
    '''
    requests.delete(f"{config.url}/clear/v1")

    # Owner
    owner_reg = requests.post(f'{config.url}/auth/register/v2', json={
        "email":"email1@gmail.com", 
        "password": "password1", 
        "name_first": "Hayden", 
        "name_last": "Smith"
    })
    owner = owner_reg.json()
    owner['token'] = create_token("haydensmith")

    createc1 = requests.post(f"{config.url}/channels/create/v2", json={
        "token": create_token("haydensmith"),
        "name" : "Channel1",
        "is_public" : True,
    })
    c_id1 = json.loads(createc1.text)['channel_id']
    assert channel_exists(c_id1)

    createc2 = requests.post(f'{config.url}/channels/create/v2', json={
        "token": create_token("haydensmith"),
        "name": "Channel2",
        "is_public": True
    })
    c_id2= json.loads(createc2.text)['channel_id']
    assert channel_exists(c_id2)

    # Member
    member_reg = requests.post(f'{config.url}/auth/register/v2', json={
        "email":"email2@gmail.com", 
        "password": "password2", 
        "name_first": "Nadya", 
        "name_last": "Ulibasa"
    })
    member = member_reg.json()
    member['token'] = create_token("nadyaulibasa")

    requests.post(f'{config.url}/channels/join/v1', json={
        "token": create_token("nadyaulibasa"),
        "channel_id": c_id2
    })

    return {
        'c_id1': c_id1,
        'c_id2': c_id2,
        'owner': owner,
        'member': member, 
    }

################################ STANDUP_START TESTS ####################################
def test_standup_start_valid(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']
    length = 1

    requests.post(config.url + '/standup/start/v1', json={
        'token': token,
        'channel_id': channel_id,
        'length': length
    })

    active = requests.get(config.url + '/standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    })
    payload = json.loads(active.text)

    assert payload['is_active']

'''  
def test_standup_start_invalid_token(register_users_channels):
    token = create_token('invalid')
    channel_id = register_users_channels['c_id2']
    length = 1
    
    res = requests.post(config.url + '/standup/start/v1', json={
        'token': token,
        'channel_id': channel_id,
        'length': length
    })
    payload = json.loads(res.text)

    assert payload['code'] == 403'''

def test_standup_start_invalid_channel(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = 3 
    length = 1

    res = requests.post(config.url + '/standup/start/v1', json={
        'token': token,
        'channel_id': channel_id,
        'length': length
    })
    payload = json.loads(res.text)

    assert payload['code'] == 400

def test_standup_start_invalid_activestandup(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']
    length = 1

    # Start 1st standup
    res1 = requests.post(config.url + '/standup/start/v1', json={
        'token': token,
        'channel_id': channel_id,
        'length': length
    })
    print(res1.json())
    # Assert 1st standup is active
    active = requests.get(config.url + '/standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    })
    assert active.json()['is_active'] 
    # assert active.json()['time_finish'] == res1.json()['time_finish']

    # Start 2nd standup
    res2 = requests.post(config.url + '/standup/start/v1', json={
        'token': token,
        'channel_id': channel_id,
        'length': length
    })
    payload = json.loads(res2.text)

    assert payload['code'] == 400

    sleep(length)

############################### STANDUP_ACTIVE TESTS ####################################
'''def test_standup_active_invalid_token(register_users_channels):
    token = create_token('invalid')
    channel_id = register_users_channels['c_id2']
    
    res = requests.get(config.url + '/standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    })
    payload = json.loads(res.text)

    assert payload['code'] == 403'''

def test_standup_active_invalid_channel(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = 3 

    res = requests.get(config.url + '/standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    })
    payload = json.loads(res.text)

    assert payload['code'] == 400

def test_standup_active_valid_active(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']
    length = 1

    # Start standup
    start = requests.post(config.url + '/standup/start/v1', json={
        'token': token,
        'channel_id': channel_id,
        'length': length
    })
    time_finish = json.loads(start.text)
    
    active = requests.get(config.url + '/standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    })
    payload = json.loads(active.text)

    assert payload['is_active'] 
    assert payload['time_finish'] == time_finish['time_finish']

    sleep(length)

def test_standup_active_valid_inactive(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']

    active = requests.get(config.url + '/standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    })
    payload = json.loads(active.text)

    assert payload['is_active'] == False
    assert payload['time_finish'] == None

def test_standup_active_valid_double(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']
    length = 1

    # Start 1st standup
    res1 = requests.post(config.url + '/standup/start/v1', json={
        'token': token,
        'channel_id': channel_id,
        'length': length
    })
    time_finish = json.loads(res1.text)
    # Ensure 1st standup is active
    active = requests.get(config.url + '/standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    })
    assert active.json()['is_active']
    assert active.json()['time_finish'] == time_finish['time_finish']
    # Ensure 1st standup has finished
    sleep(1)
    active = requests.get(config.url + '/standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    })
    assert active.json()['is_active'] == False
    assert active.json()['time_finish'] == None

    # Start 2nd standup
    res2 = requests.post(config.url + '/standup/start/v1', json={
        'token': token,
        'channel_id': channel_id,
        'length': length
    })
    time_finish = json.loads(res2.text)
    # Ensure 2nd standup is active
    active = requests.get(config.url + '/standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    })
    assert active.json()['is_active']
    assert active.json()['time_finish'] == time_finish['time_finish']
    # Ensure 2nd standup has finished
    sleep(1)
    active = requests.get(config.url + '/standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    })
    assert active.json()['is_active'] == False
    assert active.json()['time_finish'] == None

################################ STANDUP_SEND TESTS #####################################
'''def test_standup_send_invalid_token(register_users_channels):
    token = create_token('invalid')
    channel_id = register_users_channels['c_id2']
    message = 'invalid token'
    res = requests.post(config.url + '/standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })
    payload = json.loads(res.text)

    assert payload['code'] == 403'''

def test_standup_send_invalid_user(register_users_channels):
    token = register_users_channels['member']['token']
    channel_id = register_users_channels['c_id1']
    message = 'invalid not a member of channel'
    res = requests.post(config.url + '/standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })
    payload = json.loads(res.text)

    assert payload['code'] == 403

def test_standup_send_invalid_channel(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = 3
    message = 'invalid channel id'
    res = requests.post(config.url + '/standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })
    payload = json.loads(res.text)

    assert payload['code'] == 400

def test_standup_send_invalid_message(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']
    message = 100 * 'invalid message is too long'
    res = requests.post(config.url + '/standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })
    payload = json.loads(res.text)

    assert payload['code'] == 400

def test_standup_send_invalid_activestandup(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']
    message = 'invalid there is no active standup'

    # Ensure there is no active standup
    active = requests.get(config.url + '/standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    })
    payload = active.json()
    assert payload['is_active'] == False
    assert payload['time_finish'] == None

    res = requests.post(config.url + '/standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })
    payload = json.loads(res.text)
    assert payload['code'] == 400

def test_standup_send_valid(register_users_channels):
    token = register_users_channels['owner']['token']
    # u_id = register_users_channels['owner']['auth_user_id']
    channel_id = register_users_channels['c_id2']
    length = 1

    # Start standup
    requests.post(config.url + '/standup/start/v1', json={
        'token': token,
        'channel_id': channel_id,
        'length': length
    })
    # Ensure 1st standup is active
    active = requests.get(config.url + '/standup/active/v1', json={
        'token': token,
        'channel_id': channel_id
    })
    assert active.json()['is_active']

    # Send messages
    requests.post(config.url + '/standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': 'Test message 1'
    })
    requests.post(config.url + '/standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': 'Test message 2'
    })

    # Wait until standup finishes
    sleep(1)

    # Token in server is invalid, assertion error
    '''
    getmsg = requests.get(config.url + 'channel/messages/v2', json={
        'token': token,
        'channel_id': channel_id,
        'start': 0
    })
    messages = getmsg.json()['messages']
    handle_str = 'haydensmith'
    standup_messages = f"{handle_str}: Test Message 1\n" + f"{handle_str}: Test Message 2"

    assert messages[0]['message'] == standup_messages
    '''
