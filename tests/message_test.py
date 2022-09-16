'''
message_test.py
Tests for the following functions:
message_send_v1
message_remove_v1
message_edit_v1
message_share_v1
'''

import pytest
from src.message import message_send_v1,  message_remove_v1,  message_edit_v1,message_share_v1, message_senddm_v1, message_react_v1,  message_unreact_v1, message_pin_v1, message_unpin_v1, message_sendlater_v1, message_sendlaterdm_v1
from src.dm import dm_create_v1, dm_messages_v1
from src.channels import channels_create_v2
from src.channel import channel_invite_v1, channel_messages_v1
from src.auth import auth_login_v2, auth_register_v2
from src.other import clear_v1
from src.error import AccessError, InputError
from src.helper import is_member, valid_message, get_message_text, create_token, save_data
import time

@pytest.fixture
def testing_data():
    clear_v1()
    User1 = auth_register_v2("email@gmail.com", "password1", "david", "peng")
    User2 = auth_register_v2("email2@gmail.com", "password2", "krishnan", "winter")
    User3 = auth_register_v2("email3@gmail.com", "password3", "joel", "engelman")

    Channel1 = channels_create_v2(create_token("davidpeng"), "example channel", True)
    Channel2 = channels_create_v2(create_token("krishnanwinter"), "example channel 2", False)
    return {"ID1": User1["auth_user_id"], "ID2": User2["auth_user_id"], "ID3": User3["auth_user_id"], "CH1": Channel1["channel_id"], "CH2": Channel2["channel_id"]}

# message_send testing
def test_message_send_long(testing_data):
    # InputError if message is more than 1000 characters 
    message = "a"
    for i in range(0, 1100):
        message += "a"
        i += 1
    with pytest.raises(InputError):
        assert message_send_v1(testing_data["ID1"], testing_data["CH1"], message)

def test_message_send_unauth(testing_data):
    # AccessError if the supplied token doesn't correspond to an authorised user
    with pytest.raises(AccessError):
        assert message_send_v1(testing_data["ID2"], testing_data["CH1"], "new message")

def test_message_send_1(testing_data):
    #ensuring that the message_id is created properly
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "hello")

    channel_messages = channel_messages_v1(testing_data["ID1"], testing_data["CH1"], 0)

    assert len(channel_messages["messages"]) == 1

    assert get_message_text(new_message["message_id"]) == "hello"
    assert new_message["message_id"] == 0

def test_message_send_2(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "hello")
    new_message1 = message_send_v1(testing_data["ID1"], testing_data["CH1"], "hello there")

    assert get_message_text(new_message["message_id"]) == "hello"
    assert get_message_text(new_message1["message_id"]) == "hello there"

    channel_messages = channel_messages_v1(testing_data["ID1"], testing_data["CH1"], 0)
    assert len(channel_messages["messages"]) == 2

    assert new_message1["message_id"] == 1

######################################################################################################################

# message_remove testing
def test_message_remove_not_exist(testing_data):
    # Input Error if the message no longer exists
    with pytest.raises(InputError):
        assert message_remove_v1(testing_data["ID1"], 99999999999)

def test_message_remove_not_auth_user(testing_data):
    # Access Error if an unauthorised user attempts to remove message
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    with pytest.raises(AccessError):
        assert message_remove_v1(testing_data["ID2"], new_message["message_id"])

def test_removal(testing_data):
    # Ensuring that the message is not valid if it has been removed
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    message_remove_v1(testing_data["ID1"], new_message["message_id"])
    assert valid_message(new_message["message_id"]) == False

def test_removal_dm(testing_data):
    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID2"]])
    dm_id = dm["dm_id"]   

    message1 = message_senddm_v1(testing_data["ID1"], dm_id, "new message")  

    message_remove_v1(testing_data["ID1"], message1["message_id"])

    assert valid_message(message1["message_id"]) == False

######################################################################################################################

# message_edit testing
def test_message_edit_long(testing_data):
    # Input Error if a message is more than 1000 characters long
    message = "a"
    for _ in range(0, 1100):
        message += "a"
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    with pytest.raises(InputError):
        assert message_edit_v1(testing_data["ID1"], new_message["message_id"], message)

def test_message_edit_does_not_exist(testing_data):
    # Input Error if the message does not exist
    with pytest.raises(InputError):
        assert message_edit_v1(testing_data["ID1"], 9999999, "EDIT")

def test_message_edit_not_auth_user(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    with pytest.raises(AccessError):
        assert message_edit_v1(testing_data["ID2"], new_message["message_id"], "EDIT")
    
def test_message_edit_empty_string(testing_data):
    # If we pass message_edit an empty string, we remove the message
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    message_edit_v1(testing_data["ID1"], new_message["message_id"], "")
    assert valid_message(new_message["message_id"]) == False

def test_message_edit_normal(testing_data):
    # Passing an actual edit 
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")

    edit_text = "This is now an edited message"
    message_edit_v1(testing_data["ID1"], new_message["message_id"], edit_text)

    assert get_message_text(new_message["message_id"]) == edit_text

def test_message_edit_normal_dm(testing_data):
    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID2"]])
    dm_id = dm["dm_id"]   

    message1 = message_senddm_v1(testing_data["ID1"], dm_id, "new message")

    edit_text = "This is now an edited message"

    message_edit_v1(testing_data["ID1"], message1["message_id"], edit_text)

    assert get_message_text(message1["message_id"]) == edit_text


######################################################################################################################

# message_share testing

def test_message_share_not_auth(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    with pytest.raises(AccessError):
        assert message_share_v1(testing_data["ID1"], new_message["message_id"], "", testing_data["CH2"], -1)

def test_message_share_to_channel(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    channel_invite_v1(testing_data["ID2"], testing_data["CH2"], testing_data["ID1"])
    shared_message = message_share_v1(testing_data["ID1"], new_message["message_id"], "", testing_data["CH2"], -1)

    assert get_message_text(shared_message["shared_message_id"]) == get_message_text(new_message["message_id"])

def test_message_share_to_dm(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")

    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID2"]])
    dm_id = dm["dm_id"]   

    shared_message = message_share_v1(testing_data["ID1"], new_message["message_id"], "", -1, dm_id)

    assert get_message_text(shared_message["shared_message_id"]) == get_message_text(new_message["message_id"])
    
    dm_messages = dm_messages_v1(testing_data["ID1"], dm_id, 0)

    assert len(dm_messages["messages"]) == 1

######################################################################################################################

# message_senddm testing

def test_message_senddm_long(testing_data):
    message = "a"
    for i in range(0, 1100):
        message += "a"
        i += 1
    with pytest.raises(InputError):
        assert message_senddm_v1(testing_data["ID1"], 0, message)

def test_message_senddm_not_auth(testing_data):
    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID3"]])
    dm_id = dm["dm_id"]
    with pytest.raises(AccessError):
        assert message_senddm_v1(testing_data["ID2"], dm_id, "new message")

def test_message_senddm_1(testing_data):
    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID2"]])
    dm_id = dm["dm_id"]   

    message1 = message_senddm_v1(testing_data["ID1"], dm_id, "new message")

    assert get_message_text(message1['message_id']) == "new message"
    
    dm_messages = dm_messages_v1(testing_data["ID1"], dm_id, 0)

    assert len(dm_messages["messages"]) == 1

    assert message1['message_id'] == 0

def test_message_senddm_2(testing_data):
    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID2"]])
    dm_id = dm["dm_id"]   

    message1 = message_senddm_v1(testing_data["ID1"], dm_id, "new message")
    message2 = message_senddm_v1(testing_data["ID1"], dm_id, "another new message")

    assert get_message_text(message1['message_id']) == "new message"
    assert get_message_text(message2['message_id']) == "another new message"

    dm_messages = dm_messages_v1(testing_data["ID1"], dm_id, 0)

    assert len(dm_messages["messages"]) == 2

    assert message1['message_id'] == 0
    assert message2['message_id'] == 1

######################################################################################################################

#message react testing
def test_message_react_1(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")    
    message_react_v1(testing_data["ID1"], new_message["message_id"], 1)
    messages = channel_messages_v1(testing_data['ID1'], testing_data['CH1'], 0)
    message = messages['messages'][0]
    assert testing_data['ID1'] in message['reacts'][0]['u_ids']

def test_message_react_2(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")    
    channel_invite_v1(testing_data["ID1"], testing_data["CH1"], testing_data["ID2"])

    message_react_v1(testing_data["ID1"], new_message["message_id"], 1)
    message_react_v1(testing_data["ID2"], new_message["message_id"], 1)

    messages = channel_messages_v1(testing_data['ID1'], testing_data['CH1'], 0)
    message = messages['messages'][0]
    reacts = message['reacts']
    for react in reacts:
        if react['react_id'] == 1:
            test_react = react
    assert testing_data['ID1'] in test_react['u_ids']
    assert testing_data['ID2'] in test_react['u_ids']

def test_message_react_is_this_user_reacted(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")    
    channel_invite_v1(testing_data["ID1"], testing_data["CH1"], testing_data["ID2"])

    message_react_v1(testing_data["ID2"], new_message["message_id"], 1)

    messages = channel_messages_v1(testing_data['ID1'], testing_data['CH1'], 0)
    message = messages['messages'][0]
    reacts = message['reacts']
    for react in reacts:
        if react['react_id'] == 1:
            test_react = react
    assert testing_data['ID2'] in test_react['u_ids']
    assert test_react['is_this_user_reacted'] == False

def test_message_react_invalid_message(testing_data):
    #message_id is not a valid message within a channel or DM that the authorised user has joined
    with pytest.raises(InputError):
        assert message_react_v1(testing_data["ID1"], 99999999, 1)

def test_message_react_invalid_react_id(testing_data):
    #react_id is not a valid React ID. The only valid react ID the frontend has is 1
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")    
    with pytest.raises(InputError):
        assert message_react_v1(testing_data["ID1"], new_message['message_id'], 5)

def test_message_react_id_exists(testing_data):
    #Message with ID message_id already contains an active React with ID react_id from the authorised user
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")    
    message_react_v1(testing_data["ID1"], new_message["message_id"], 1)
    with pytest.raises(InputError):
        assert message_react_v1(testing_data["ID1"], new_message['message_id'], 1)

def test_message_react_unauthorised_user(testing_data):
    #The authorised user is not a member of the channel or DM that the message is within
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    with pytest.raises(AccessError):
        assert message_react_v1(testing_data["ID3"], new_message['message_id'], 1)

def test_message_react_user_not_in_dm(testing_data):
    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID3"]])
    new_message = message_senddm_v1(testing_data['ID1'], dm['dm_id'], "Hello")
    with pytest.raises(AccessError):
        assert message_react_v1(testing_data["ID2"], new_message['message_id'], 1)

######################################################################################################################

# message un-react testing
def test_message_unreact_user_not_in_dm(testing_data):
    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID3"]])
    new_message = message_senddm_v1(testing_data['ID1'], dm['dm_id'], "Hello")
    message_react_v1(testing_data["ID1"], new_message['message_id'], 1)
    with pytest.raises(AccessError):
        assert message_unreact_v1(testing_data["ID2"], new_message['message_id'], 1)

def test_message_unreact_invalid_message(testing_data):
    #message_id is not a valid message within a channel or DM that the authorised user has joined
    with pytest.raises(InputError):
        assert message_unreact_v1(testing_data["ID1"], 99999999, 1)

def test_message_unreact_invalid_react_id(testing_data):
    #react_id is not a valid React ID. The only valid react ID the frontend has is 1
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")    
    with pytest.raises(InputError):
        assert message_unreact_v1(testing_data["ID1"], new_message['message_id'], 5)

def test_message_unreact_not_reacted(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")    
    with pytest.raises(InputError):
        assert message_unreact_v1(testing_data["ID1"], new_message['message_id'], 1)

def test_message_unreact_invalid_user(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    with pytest.raises(AccessError):
        assert message_unreact_v1(testing_data["ID3"], new_message['message_id'], 1)

def test_message_unreact_1(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")    
    channel_invite_v1(testing_data["ID1"], testing_data["CH1"], testing_data["ID2"])

    message_react_v1(testing_data["ID1"], new_message["message_id"], 1)

    messages = channel_messages_v1(testing_data['ID1'], testing_data['CH1'], 0)
    message = messages['messages'][0]
    reacts = message['reacts']
    for react in reacts:
        if react['react_id'] == 1:
            test_react = react
    assert testing_data['ID1'] in test_react['u_ids']

    message_unreact_v1(testing_data["ID1"], new_message["message_id"], 1)

    messages = channel_messages_v1(testing_data['ID1'], testing_data['CH1'], 0)
    message = messages['messages'][0]
    reacts = message['reacts']
    for react in reacts:
        if react['react_id'] == 1:
            test_react = react
    assert testing_data['ID1'] not in test_react['u_ids']
    assert test_react['is_this_user_reacted'] == False
######################################################################################################################

# message pin testing
def test_message_pin_not_valid(testing_data):
    # Testing when a message id is not valid
    with pytest.raises(InputError):
        assert message_pin_v1(testing_data["ID1"], 9999999999999)

def test_message_pin_already_pinned(testing_data):
    # Testing trying to pin a message that is already pinned
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    message_pin_v1(testing_data["ID1"], new_message['message_id'])
    with pytest.raises(InputError):
        assert message_pin_v1(testing_data['ID1'], new_message['message_id'])

def test_message_pin_user_not_auth(testing_data):
    # Testing when a user is not authorised to pin a message
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    with pytest.raises(AccessError):
        assert message_pin_v1(testing_data["ID3"], new_message['message_id'])

def test_message_pin_not_in_dm(testing_data):
    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID3"]])
    new_message = message_senddm_v1(testing_data['ID1'], dm['dm_id'], "Hello")
    with pytest.raises(AccessError):
        assert message_pin_v1(testing_data["ID2"], new_message['message_id'])

def test_message_pin_1(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    message_pin_v1(testing_data['ID1'], new_message['message_id'])
   
    messages = channel_messages_v1(testing_data['ID1'], testing_data['CH1'], 0)
    message = messages['messages'][0]

    assert message['is_pinned'] == True

def test_message_pin_2(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    message_pin_v1(testing_data['ID1'], new_message['message_id'])

    new_message2 = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    message_pin_v1(testing_data['ID1'], new_message2['message_id'])

    messages = channel_messages_v1(testing_data['ID1'], testing_data['CH1'], 0)
    message1 = messages['messages'][0]
    message2 = messages['messages'][1]

    assert message1['is_pinned'] == True
    assert message2['is_pinned'] == True

def test_message_pin_1_2_messages(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    message_pin_v1(testing_data['ID1'], new_message['message_id'])

    message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")

    messages = channel_messages_v1(testing_data['ID1'], testing_data['CH1'], 0)
    message1 = messages['messages'][0]
    message2 = messages['messages'][1]

    assert message1['is_pinned'] == False
    assert message2['is_pinned'] == True

######################################################################################################################

# message unpin testing
def test_message_unpin_not_valid(testing_data):
    # Testing when a message id is not valid
    with pytest.raises(InputError):
        assert message_unpin_v1(testing_data["ID1"], 9999999999999)

def test_message_unpin_already_unpinned(testing_data):
    # Testing when a message is already unpinned
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    with pytest.raises(InputError):
        assert message_unpin_v1(testing_data["ID1"], new_message['message_id'])

def test_message_unpin_not_auth(testing_data):
    # Testing when an unauthorised user attempts to unpin a message
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    message_pin_v1(testing_data["ID1"], new_message['message_id'])
    with pytest.raises(AccessError):
        assert message_unpin_v1(testing_data['ID3'], new_message['message_id'])

def test_message_unpin_not_in_dm(testing_data):
    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID3"]])
    new_message = message_senddm_v1(testing_data['ID1'], dm['dm_id'], "Hello")
    message_pin_v1(testing_data["ID1"], new_message['message_id'])

    with pytest.raises(AccessError):
        assert message_unpin_v1(testing_data['ID2'], new_message['message_id'])


def test_message_unpin_1(testing_data):
    new_message = message_send_v1(testing_data["ID1"], testing_data["CH1"], "This is a new message")
    message_pin_v1(testing_data['ID1'], new_message['message_id'])
   
    messages = channel_messages_v1(testing_data['ID1'], testing_data['CH1'], 0)
    message = messages['messages'][0]

    assert message['is_pinned'] == True

    message_unpin_v1(testing_data['ID1'], new_message['message_id'])

    messages = channel_messages_v1(testing_data['ID1'], testing_data['CH1'], 0)
    message = messages['messages'][0]

    assert message['is_pinned'] == False


######################################################################################################################

# message sendlater testing
def test_message_sendlater_channel_invalid(testing_data):
    # Testing if the channel does not exist
    with pytest.raises(InputError):
        assert message_sendlater_v1(testing_data['ID1'], 99999999, "hello", 1621312012)

def test_message_sendlater_message_long(testing_data):
    # Testing when the message is too long
    message = "a"
    for i in range(0, 1100):
        message += "a"
        i += 1
    timestamp = time.time()
    timestamp = timestamp + (2 * 60 * 60)
    with pytest.raises(InputError):
        assert message_sendlater_v1(testing_data['ID1'], testing_data['CH1'], message, timestamp)

def test_message_sendlater_time_past(testing_data):
    # Testing if the inputted time occured in the past 
    with pytest.raises(InputError):
        assert message_sendlater_v1(testing_data['ID1'], testing_data['CH1'], "Hello", 1616038012)

def test_message_sendlater_user_invalud(testing_data):
    # Testing when the user is not apart of the channel
    timestamp = time.time()
    timestamp = timestamp + (2 * 60 * 60)
    with pytest.raises(AccessError):
        assert message_sendlater_v1(testing_data['ID3'], testing_data['CH1'], "Hello", timestamp)

def test_message_sendlater_5_seconds(testing_data):
    timestamp = time.time()
    timestamp = timestamp + 5
    start = time.time()
    message = message_sendlater_v1(testing_data['ID1'], testing_data['CH1'], "Hello", timestamp)
    end = time.time()

    assert int(end - start) == 5
    messages = channel_messages_v1(testing_data['ID1'], testing_data['CH1'], 0)
    message = messages['messages'][0]
    
    assert message['message'] == 'Hello'

######################################################################################################################

# message sendlaterdm testing
def test_message_sendlaterdm_invalid_dm(testing_data):
    # Testing if the user is apart of the dm
    timestamp = time.time()
    timestamp = timestamp + (2 * 60 * 60)
    with pytest.raises(InputError):
        assert message_sendlaterdm_v1(testing_data['ID2'], 999999999, "hello", timestamp)

def test_message_sendlaterdm_message_long(testing_data):
    # Testing sending a message that is over 1000 characters
    message = "a"
    for i in range(0, 1100):
        message += "a"
        i += 1
    timestamp = time.time()
    timestamp = timestamp + (2 * 60 * 60)
    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID3"]])
    dm_id = dm["dm_id"]
    with pytest.raises(InputError):
        assert message_sendlaterdm_v1(testing_data['ID1'], dm_id, message, timestamp)

def test_message_sendlaterdm_time_past(testing_data):
    # Testing if the inputted time is in the past
    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID3"]])
    dm_id = dm["dm_id"]
    with pytest.raises(InputError):
        assert message_sendlaterdm_v1(testing_data['ID1'], dm_id, "Hello", 1616038012)

def test_message_sendlaterdm_user_not_in_dm(testing_data):
    # Testing if the user is not apart of the DM
    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID3"]])
    dm_id = dm["dm_id"]
    timestamp = time.time()
    timestamp = timestamp + (2 * 60 * 60)
    with pytest.raises(AccessError):
        assert message_sendlaterdm_v1(testing_data['ID2'], dm_id, "hello", timestamp)

def test_message_sendlaterdm_5_seconds(testing_data):
    dm = dm_create_v1(testing_data["ID1"], [testing_data["ID3"]])
    dm_id = dm["dm_id"]
    timestamp = time.time()
    timestamp = timestamp + 5
    start = time.time()
    message_sendlaterdm_v1(testing_data['ID1'], dm_id, "hello", timestamp)
    end = time.time()

    assert int(end - start) == 5

