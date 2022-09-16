import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.helper import create_token, token_decode, valid_message
import src.data as d
import time

@pytest.fixture
def testing_data():
    clear_v1()
    requests.post(f"{config.url}/auth/register/v2", json = {"email":"email2@gmail.com", "password":"password2", "name_first":"David", "name_last":"Peng"})
    requests.post(f"{config.url}/auth/register/v2", json = {"email":"email3@gmail.com", "password":"password3", "name_first":"Krishnan", "name_last":"Winter"})
    requests.post(f"{config.url}/auth/register/v2", json = {"email":"email4@gmail.com", "password":"password4", "name_first":"Joel", "name_last":"Engelman"})
    CH1json = requests.post(f"{config.url}/channels/create/v2", json = {"token": create_token("davidpeng"), "name": "example channel", "is_public": True})
    CH2json = requests.post(f"{config.url}/channels/create/v2", json = {"token": create_token("krishnanwinter"), "name": "example channel2", "is_public": True})
    CH1 = CH1json.json()
    CH2 = CH2json.json()
    return {"CH1": CH1['channel_id'], "CH2": CH2['channel_id']}
# Error testing for message_send HTTP implementation

def test_message_send_long(testing_data):
    message = "a"
    for i in range(0, 1100):
        message += "a"
        i += 1

    r = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": message})
    data = json.loads(r.text)
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Message is more than 1000 characters</p>'}

def test_message_unauth(testing_data):
    r = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH2'], "message": "This is a message"})
    data = json.loads(r.text)
    assert data == {'code': 403, 'name': 'System Error', 'message': '<p>User is not apart of channel</p>'}

# Error testing for message_remove HTTP implementation
def test_message_remove_not_exist(testing_data):

    r = requests.delete(f"{config.url}/message/remove/v1", json = {"token": create_token("davidpeng"), "message_id": 9999999})
    data = json.loads(r.text)
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Message no longer exists</p>'}
    
def test_message_remove_not_auth_user(testing_data):
    m = requests.post(f"{config.url}/message/send/v2", json = {"token": create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message = m.json()
    print(message)
    r = requests.delete(f"{config.url}/message/remove/v1", json = {"token":create_token("krishnanwinter"), "message_id": message['message_id']})
    data = r.json()
    assert data == {'code': 403, 'name': 'System Error', 'message': '<p>User is not authorised to delete message</p>'}

# Error testing for message_edit HTTP implementation

def test_message_edit_long(testing_data):
    text = "a"
    for i in range(0, 1100):
        text += "a"
        i += 1

    m = requests.post(f"{config.url}/message/send/v2", json = {"token": create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message = m.json()
    m_id = message['message_id']

    r = requests.put(f"{config.url}/message/edit/v2", json = {"token" : create_token("davidpeng"), "message_id": m_id, "message": text})
    data = r.json()
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Message is too long</p>'}

def test_message_edit_does_not_exist(testing_data):
    requests.post(f"{config.url}/message/send/v2", json = {"token": create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})

    r = requests.put(f"{config.url}/message/edit/v2", json = {"token" : create_token("davidpeng"), "message_id": 99999999999, "message": "hello"})
    data = r.json()
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Message no longer exists</p>'}

def test_message_edit_not_auth_user(testing_data):
    m = requests.post(f"{config.url}/message/send/v2", json = {"token": create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message = m.json()
    m_id = message['message_id']

    r = requests.put(f"{config.url}/message/edit/v2", json = {"token" : create_token("krishnanwinter"), "message_id": m_id, "message": "hello"})
    data = r.json()
    assert data == {'code': 403, 'name': 'System Error', 'message': '<p>User is not authorised to edit message</p>'}

# Error testing for message_share HTTP implementation

def test_message_share_not_auth(testing_data):
    m = requests.post(f"{config.url}/message/send/v2", json = {"token": create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message = m.json()
    m_id = message['message_id']

    r = requests.post(f"{config.url}/message/share/v1", json = {"token": create_token("krishnanwinter"), "og_message_id": m_id, "message": "", "channel_id": testing_data['CH1'], "dm_id": -1})
    data = r.json()

    assert data == {'code': 403, 'name': 'System Error', 'message': '<p>User is not apart of channel</p>'}
# Error testing for message_senddm HTTP implementation

def test_message_senddm_long(testing_data):
    message = "a"
    for i in range(0, 1100):
        message += "a"
        i += 1

    r = requests.post(f"{config.url}/message/senddm/v1", json = {"token":create_token("davidpeng"), "dm_id": 0, "message": message})
    data = json.loads(r.text)
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Message is more than 1000 characters</p>'}

def test_message_senddm_not_auth(testing_data):
    uids = [1]
    dmjson = requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids})
    dm = dmjson.json()
    dm_id = dm['dm_id']

    r = requests.post(f"{config.url}/message/senddm/v1", json = {"token":create_token("joelengelman"), "dm_id": dm_id, "message": "message"})

    data = r.json()

    assert data == {'code': 403, 'name': 'System Error', 'message': '<p>User is not apart of the dm</p>'}

# Successful message_send
def test_message_send_valid(testing_data):
    requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    c = requests.get(f"{config.url}/channel/messages/v2", params = {'token': create_token("davidpeng"), "channel_id": testing_data['CH1'], "start": 0})
    messages = c.json()

    numOfMessages = len(messages['messages'])

    assert numOfMessages == 1
    first_message = messages['messages'][0]
    message_text = first_message['message']
    assert message_text == "This is a message"

# Successful message_remove
def test_message_remove(testing_data):
    r = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
   
    message_data = r.json()
    m_id = message_data["message_id"]

    requests.delete(f"{config.url}/message/remove/v1", json = {"token":create_token("davidpeng"), "message_id": m_id})

    c = requests.get(f"{config.url}/channel/messages/v2", params = {'token': create_token("davidpeng"), "channel_id": testing_data['CH1'], "start": 0})
    messages = c.json()

    numOfMessages = len(messages['messages'])

    assert numOfMessages == 0

# Successful message_edit
def test_message_edit_valid(testing_data):
    r = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
   
    message_data = r.json()
    m_id = message_data["message_id"]

    requests.put(f"{config.url}/message/edit/v2", json = {"token" : create_token("davidpeng"), "message_id": m_id, "message": "Hello"})

    c = requests.get(f"{config.url}/channel/messages/v2", params = {'token': create_token("davidpeng"), "channel_id": testing_data['CH1'], "start": 0})
    messages = c.json()
    first_message = messages['messages'][0]
    message_text = first_message['message']
    assert message_text == "Hello"

# Successful message_share
def test_message_share_valid(testing_data):
    r = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
   
    message_data = r.json()
    m_id = message_data["message_id"]

    n = requests.post(f"{config.url}/message/share/v1", json = {"token": create_token("davidpeng"), "og_message_id": m_id, "message": "", "channel_id": testing_data['CH1'], "dm_id": -1})
    
    shared_data = n.json()
    shared_id = shared_data["shared_message_id"]

    c = requests.get(f"{config.url}/channel/messages/v2", params = {'token': create_token("davidpeng"), "channel_id": testing_data['CH1'], "start": 0})
    messages = c.json()
    latest_message = messages['messages'][0]
    message_text = latest_message['message']
    latest_message_id = latest_message['message_id']
    assert latest_message_id == shared_id
    assert message_text == "This is a message"

# Successful message_senddm
def test_message_senddm_valid(testing_data):
    uids = [1]
    dmjson = requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids})
    dm = dmjson.json()
    dm_id = dm['dm_id']

    r = requests.post(f"{config.url}/message/senddm/v1", json = {"token":create_token("davidpeng"), "dm_id": dm_id, "message": "message"})
    message = r.json()
    m_id = message['message_id']

    c = requests.get(f"{config.url}/dm/messages/v1", params = {'token': create_token("davidpeng"), "dm_id": dm_id, "start": 0})
    dm_messages = c.json()
    first_message = dm_messages['messages'][0]

    assert m_id == first_message['message_id']

# Message React error testing
def test_message_react_invalid_messaage(testing_data):
    # Testing an invalid message
    r = requests.post(f"{config.url}/message/react/v1", json = {'token': create_token("davidpeng"), 'message_id': 999999, 'react_id': 1})

    data = r.json()

    assert data['code'] == 400

def test_message_react_invalid_react_id(testing_data):
    # Testing an invalid react id
    m = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message_data = m.json()
    m_id = message_data["message_id"]

    r = requests.post(f"{config.url}/message/react/v1", json = {'token': create_token("davidpeng"), 'message_id': m_id, 'react_id': 555})
    data = r.json()

    assert data['code'] == 400

def test_message_react_uid_exists(testing_data):
    # Testing reacting to a message when we have already reacted
    m = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message_data = m.json()
    m_id = message_data["message_id"]

    requests.post(f"{config.url}/message/react/v1", json = {'token': create_token("davidpeng"), 'message_id': m_id, 'react_id': 1})

    r = requests.post(f"{config.url}/message/react/v1", json = {'token': create_token("davidpeng"), 'message_id': m_id, 'react_id': 1})
    data = r.json()

    assert data['code'] == 400

def test_messaage_react_unauth_user(testing_data):
    # Testing reacting as an unauthorised user
    m = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message_data = m.json()
    m_id = message_data["message_id"]

    r = requests.post(f"{config.url}/message/react/v1", json = {'token': create_token("krishnanwinter"), 'message_id': m_id, 'react_id': 1})
    data = r.json()

    assert data['code'] == 403

def test_message_react_user_not_in_dm(testing_data):
    # Testing reacting when user is not in dm
    uids = [1]
    dmjson = requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids})
    dm = dmjson.json()
    dm_id = dm['dm_id']

    r = requests.post(f"{config.url}/message/senddm/v1", json = {"token":create_token("davidpeng"), "dm_id": dm_id, "message": "message"})
    message = r.json()
    m_id = message['message_id']

    react = requests.post(f"{config.url}/message/react/v1", json = {'token': create_token("joelengelman"), 'message_id': m_id, 'react_id': 1})

    data = react.json()

    assert data['code'] == 403

# Message unreact error testing

def test_message_unreact_user_not_in_dm(testing_data):
    # Testing unreacting when user is not in dm
    uids = [1]
    dmjson = requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids})
    dm = dmjson.json()
    dm_id = dm['dm_id']

    r = requests.post(f"{config.url}/message/senddm/v1", json = {"token":create_token("davidpeng"), "dm_id": dm_id, "message": "message"})
    message = r.json()
    m_id = message['message_id']

    unreact = requests.post(f"{config.url}/message/unreact/v1", json = {'token': create_token("joelengelman"), 'message_id': m_id, 'react_id': 1})

    data = unreact.json()

    assert data['code'] == 403

def test_message_unreact_invalid_message(testing_data):
    # Testing an invalid message
    r = requests.post(f"{config.url}/message/unreact/v1", json = {'token': create_token("davidpeng"), 'message_id': 999999, 'react_id': 1})

    data = r.json()

    assert data['code'] == 400

def test_message_unreact_invalid_react_id(testing_data):
    # Testing an invalid react id
    m = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message_data = m.json()
    m_id = message_data["message_id"]

    r = requests.post(f"{config.url}/message/unreact/v1", json = {'token': create_token("davidpeng"), 'message_id': m_id, 'react_id': 555})
    data = r.json()

    assert data['code'] == 400

def test_message_unreact_not_reacted(testing_data):
    # Testing when the user tries to unreact a message they have not reacted to
    m = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message_data = m.json()
    m_id = message_data["message_id"]

    r = requests.post(f"{config.url}/message/unreact/v1", json = {'token': create_token("davidpeng"), 'message_id': m_id, 'react_id': 1})
    data = r.json()

    assert data['code'] == 400

def test_message_unreact_invalid_user(testing_data):
    # Testing unreacting as an unauthorised user
    m = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message_data = m.json()
    m_id = message_data["message_id"]

    r = requests.post(f"{config.url}/message/unreact/v1", json = {'token': create_token("krishnanwinter"), 'message_id': m_id, 'react_id': 1})
    data = r.json()

    assert data['code'] == 403

# Message pin error testing

def test_message_pin_not_valid(testing_data):
    # Testing an invalid message id
    r = requests.post(f"{config.url}/message/pin/v1", json = {'token': create_token("davidpeng"), 'message_id': 99999})

    data = r.json()

    assert data['code'] == 400

def test_message_pin_already_pinned(testing_data):
    # Testing pinning a message that has already been pinned
    m = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message_data = m.json()
    m_id = message_data["message_id"]

    requests.post(f"{config.url}/message/pin/v1", json = {'token': create_token("krishnanwinter"), 'message_id': m_id})

    r = requests.post(f"{config.url}/message/pin/v1", json = {'token': create_token("davidpeng"), 'message_id': 99999})

    data = r.json()

    assert data['code'] == 400

def test_message_pin_user_not_auth(testing_data):
    # Unauth user trying to pin a message
    m = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message_data = m.json()
    m_id = message_data["message_id"]

    r = requests.post(f"{config.url}/message/pin/v1", json = {'token': create_token("joelengelman"), 'message_id': m_id})

    data = r.json()

    assert data['code'] == 403

def test_message_pin_user_not_in_dm(testing_data):
    # User who is not apart of dm attempting to pin message
    uids = [1]
    dmjson = requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids})
    dm = dmjson.json()
    dm_id = dm['dm_id']

    r = requests.post(f"{config.url}/message/senddm/v1", json = {"token":create_token("davidpeng"), "dm_id": dm_id, "message": "message"})
    message = r.json()
    m_id = message['message_id']

    pin = requests.post(f"{config.url}/message/pin/v1", json = {'token': create_token("joelengelman"), 'message_id': m_id})

    data = pin.json()

    assert data['code'] == 403

# Message unpin error testing

def test_message_unpin_not_valid(testing_data):
    # Testing an invalid message id
    r = requests.post(f"{config.url}/message/unpin/v1", json = {'token': create_token("davidpeng"), 'message_id': 99999})

    data = r.json()

    assert data['code'] == 400

def test_message_unpin_already_unpinned(testing_data):
    m = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message_data = m.json()
    m_id = message_data["message_id"]

    r = requests.post(f"{config.url}/message/unpin/v1", json = {'token': create_token("davidpeng"), 'message_id': m_id})

    data = r.json()

    assert data['code'] == 400

def test_message_unpin_not_auth(testing_data):
    m = requests.post(f"{config.url}/message/send/v2", json = {"token":create_token("davidpeng"), "channel_id": testing_data['CH1'], "message": "This is a message"})
    message_data = m.json()
    m_id = message_data["message_id"]

    requests.post(f"{config.url}/message/pin/v1", json = {'token': create_token("davidpeng"), 'message_id': m_id})

    r = requests.post(f"{config.url}/message/unpin/v1", json = {'token': create_token("joelengelman"), 'message_id': m_id})
    data = r.json()

    assert data['code'] == 403

def test_message_unpin_not_in_dm(testing_data):
    # User who is not apart of dm attempting to unpin message
    uids = [1]
    dmjson = requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids})
    dm = dmjson.json()
    dm_id = dm['dm_id']

    r = requests.post(f"{config.url}/message/senddm/v1", json = {"token":create_token("davidpeng"), "dm_id": dm_id, "message": "message"})
    message = r.json()
    m_id = message['message_id']

    requests.post(f"{config.url}/message/pin/v1", json = {'token': create_token("davidpeng"), 'message_id': m_id})

    unpin = requests.post(f"{config.url}/message/unpin/v1", json = {'token': create_token("joelengelman"), 'message_id': m_id})

    data = unpin.json()

    assert data['code'] == 403

# Message sendlater error testing

def test_message_sendlater_channel_invalid(testing_data):
    # Test sending a message to a non existant channel
    timestamp = time.time()
    timestamp += 5
    r = requests.post(f"{config.url}/message/sendlater/v1", json = {'token': create_token("davidpeng"), 'channel_id': 10000, 'message': "Hello", 'time_sent': timestamp})
    data = r.json()

    assert data['code'] == 400

def test_message_sendlater_message_long(testing_data):
    # Test sending a message that is too long
    text = "a"
    for i in range(0, 1100):
        text += "a"
        i += 1

    timestamp = time.time()
    timestamp += 5
    r = requests.post(f"{config.url}/message/sendlater/v1", json = {'token': create_token("davidpeng"), 'channel_id': testing_data['CH1'], 'message': text, 'time_sent': timestamp})
    data = r.json()

    assert data['code'] == 400

def test_message_sendlater_time_past(testing_data):
    # Testing passing a time that is in the past
    timestamp = time.time()
    timestamp -= 100
    r = requests.post(f"{config.url}/message/sendlater/v1", json = {'token': create_token("davidpeng"), 'channel_id': testing_data['CH1'], 'message': "Hello", 'time_sent': timestamp})
    data = r.json()

    assert data['code'] == 400

def test_message_sendlater_user_invalid(testing_data):
    # Testing sending a message as an unauth user
    timestamp = time.time()
    timestamp += 5
    r = requests.post(f"{config.url}/message/sendlater/v1", json = {'token': create_token("joelengelman"), 'channel_id': testing_data['CH1'], 'message': "Hello", 'time_sent': timestamp})
    data = r.json()

    assert data['code'] == 403

# Message sendlaterdm error testing

def test_message_sendlaterdm_invalid_dm(testing_data):
    # Testing sending to a nonexistant dm

    timestamp = time.time()
    timestamp += 5
    r = requests.post(f"{config.url}/message/sendlaterdm/v1", json = {'token': create_token("davidpeng"), 'dm_id': 10000, 'message': "Hello", 'time_sent': timestamp})
    data = r.json()

    assert data['code'] == 400

def test_message_sendlaterdm_message_long(testing_data):
    # Test sending a message that is too long
    text = "a"
    for i in range(0, 1100):
        text += "a"
        i += 1

    uids = [1]
    dmjson = requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids})
    dm = dmjson.json()
    dm_id = dm['dm_id']

    timestamp = time.time()
    timestamp += 5
    r = requests.post(f"{config.url}/message/sendlaterdm/v1", json = {'token': create_token("davidpeng"), 'dm_id': dm_id, 'message': text, 'time_sent': timestamp})
    data = r.json()

    assert data['code'] == 400

def test_message_sendlaterdm_time_past(testing_data):
    # Testing sending a message thats time is in the past
    uids = [1]
    dmjson = requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids})
    dm = dmjson.json()
    dm_id = dm['dm_id']

    timestamp = time.time()
    timestamp -= 100

    r = requests.post(f"{config.url}/message/sendlaterdm/v1", json = {'token': create_token("davidpeng"), 'dm_id': dm_id, 'message': "Hello", 'time_sent': timestamp})
    data = r.json()

    assert data['code'] == 400

def test_message_sendlaterdm_user_not_in_dm(testing_data):
    uids = [1]
    dmjson = requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids})
    dm = dmjson.json()
    dm_id = dm['dm_id']

    timestamp = time.time()
    timestamp += 5
    r = requests.post(f"{config.url}/message/sendlaterdm/v1", json = {'token': create_token("joelengelman"), 'dm_id': dm_id, 'message': "Hello", 'time_sent': timestamp})
    data = r.json()

    assert data['code'] == 403

# Test successful sendlater

def test_message_sendlater_1(testing_data):
    uids = [1]
    dmjson = requests.post(f"{config.url}/dm/create/v1", json = {"token": create_token("davidpeng"), "uids": uids})
    dm = dmjson.json()
    dm_id = dm['dm_id']

    timestamp = time.time()
    timestamp += 5
    start = time.time()
    requests.post(f"{config.url}/message/sendlaterdm/v1", json = {'token': create_token("davidpeng"), 'dm_id': dm_id, 'message': "Hello", 'time_sent': timestamp})
    end = time.time()
    assert int(end-start) == 5