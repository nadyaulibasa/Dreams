'''
user_test.py
Tests for user.py
'''

import pytest
from src.user import    user_profile_v1, \
                        user_profile_setname_v1, \
                        user_profile_setemail_v1, \
                        user_profile_sethandle_v1, \
                        user_stats_v1, \
                        users_stats_v1
from src.auth import auth_login_v2, auth_register_v2
from src.helper import create_token
from src.other import clear_v1
from src.error import AccessError, InputError
from src.channels import channels_create_v2
from src.channel import channel_invite_v1
from src.dm import dm_create_v1
from src.message import message_send_v1, message_senddm_v1

@pytest.fixture
def register_login():
    '''
    < Fixture registers a user and then logs them in >
    Returns dictionary containing their u_id and tokens
    '''
    clear_v1()

    # Create users:
    auth_register_v2("email1@gmail.com", "password1", "Hayden", "Smith")
    user1 = auth_login_v2("email1@gmail.com", "password1")

    auth_register_v2("email2@gmail.com", "password2", "Nadya", "Ulibasa")
    user2 = auth_login_v2("email2@gmail.com", "password2")

    return {
        "ID1"   : user1["auth_user_id"],
        "Token1": user1["token"],
        "ID2"   : user2["auth_user_id"],
        "Token2": user2["token"],
        "Email2": "email2@gmail.com",
        "Handle2": "nadyaulibasa"
    }

##########################################################################################
# user_profile tests

def test_user_profile_valid(register_login):
    # Set up valid token and u_id to be passed to user_profile
    u_id = register_login["ID1"]
    token = register_login["Token1"]

    # Since all inputs are valid, should return the users data
    assert user_profile_v1(token, u_id) == {
        'user': {
        	'u_id': 0,
        	'email': 'email1@gmail.com',
        	'name_first': 'Hayden',
        	'name_last': 'Smith',
        	'handle_str': 'haydensmith',
        },
    }

def test_user_profile_invalid_uid(register_login):
    # Set up valid token but invalid u_id to be passed to user_profile
    u_id = "invalid_uid"
    token = register_login["Token1"]

    # Invalid u_id, function should raise InputError
    with pytest.raises(InputError):
        assert user_profile_v1(token, u_id)

'''def test_user_profile_invalid_token(register_login):
    # Set up valid u_id but invalid token to be passed to user_profile
    u_id = register_login["ID1"]
    token = create_token("invalid")

    # Invalid token, function should raise InputError
    with pytest.raises(AccessError):
        assert user_profile_v1(token, u_id)'''


##########################################################################################
# user_profile_setname tests

def test_user_profile_setname_valid(register_login):
    # Set up valid u_id, token, first name and last name
    # to be passed to user_profile_setname
    u_id = register_login["ID1"]
    token = register_login["Token1"]
    name_first = "Sayden"
    name_last = "Hmith"

    # Call function
    user_profile_setname_v1(token, name_first, name_last)
    changed_user = user_profile_v1(token, u_id)

    assert  ([changed_user['user']['name_first'], changed_user['user']['name_last']] ==
            [name_first, name_last])

'''def test_user_profile_setname_invalid_token(register_login):
    # Set up data but invalid token
    u_id = register_login["ID1"]
    token = create_token("invalid")
    name_first = "Sayden"
    name_last = "Hmith"

    # Call function, AccessError
    with pytest.raises(AccessError):
        user_profile_setname_v1(token, name_first, name_last)'''

def test_user_profile_setname_invalid_firstnameshort(register_login):
    # Set up data but first name is too short
    token = register_login["Token1"]
    name_first = ""
    name_last = "Hmith"

    # Call function, InputError
    with pytest.raises(InputError):
        user_profile_setname_v1(token, name_first, name_last)

def test_user_profile_setname_invalid_firstnamelong(register_login):
    # Set up data but first name is too long
    token = register_login["Token1"]
    name_first = "Abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz"
    name_last = "Hmith"

    # Call function, InputError
    with pytest.raises(InputError):
        user_profile_setname_v1(token, name_first, name_last)

def test_user_profile_setname_invalid_lastnameshort(register_login):
    # Set up data but last name is too short
    token = register_login["Token1"]
    name_first = "Sayden"
    name_last = ""

    # Call function, InputError
    with pytest.raises(InputError):
        user_profile_setname_v1(token, name_first, name_last)

def test_user_profile_setname_invalid_lastnamelong(register_login):
    # Set up data but last name is too long
    token = register_login["Token1"]
    name_first = "S"
    name_last = "Abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz"

    # Call function, InputError
    with pytest.raises(InputError):
        user_profile_setname_v1(token, name_first, name_last)


##########################################################################################
# user_profile_setemail tests

def test_user_profile_setemail_valid(register_login):
    # Set up valid u_id, token, first name and last name
    # to be passed to user_profile_setemail
    u_id = register_login["ID1"]
    token = register_login["Token1"]
    email = "mynewemail@gmail.com"

    # Call function
    user_profile_setemail_v1(token, email)
    changed_user = user_profile_v1(token, u_id)

    assert changed_user['user']['email'] == email

'''def test_user_profile_setemail_invalid_token(register_login):
    # Set up data but invalid token
    u_id = register_login["ID1"]
    token = create_token("invalid")
    email = "mynewemail@gmail.com"

    # Call function, AccessError
    with pytest.raises(AccessError):
        user_profile_setemail_v1(token, email)'''

def test_user_profile_setemail_invalid_email_1(register_login):
    # Set up data but the new email is not in the valid format
    token = register_login["Token1"]
    email = "definitelynotavalidemail"

    # Call function, InputError
    with pytest.raises(InputError):
        user_profile_setemail_v1(token, email)

def test_user_profile_setemail_invalid_email_2(register_login):
    # Set up data but the new email is already in use of another user
    token = register_login["Token1"]
    email = register_login["Email2"]

    # Call function, InputError
    with pytest.raises(InputError):
        user_profile_setemail_v1(token, email)


##########################################################################################
# user_profile_sethandle tests

def test_user_profile_sethandle_valid(register_login):
    # Set up valid u_id, token, first name and last name
    # to be passed to user_profile_setemail
    u_id = register_login["ID1"]
    token = register_login["Token1"]
    handle = "mynewhandle"

    # Call function
    user_profile_sethandle_v1(token, handle)
    changed_user = user_profile_v1(token, u_id)

    assert changed_user['user']['handle_str'] == handle

'''def test_user_profile_sethandle_invalid_token(register_login):
    # Set up data but token is invalid
    u_id = register_login["ID1"]
    token = create_token("invalid")
    handle = "mynewhandle"

    # Call function, AccessError
    with pytest.raises(AccessError):
        user_profile_sethandle_v1(token, handle)'''

def test_user_profile_sethandle_invalid_handle_1(register_login):
    # Set up data but the new handle is too short
    token = register_login["Token1"]
    handle = ""

    # Call function, InputError
    with pytest.raises(InputError):
        user_profile_sethandle_v1(token, handle)

def test_user_profile_sethandle_invalid_handle_2(register_login):
    # Set up data but the new handle is too long
    token = register_login["Token1"]
    handle = "thishandleiswaytoolonglollongerthan20charextraforgoodmeasure"

    # Call function, InputError
    with pytest.raises(InputError):
        user_profile_sethandle_v1(token, handle)

def test_user_profile_sethandle_invalid_handle_3(register_login):
    # Set up data but the new handle is already used by another user
    token = register_login["Token1"]
    handle = register_login["Handle2"]

    # Call function, InputError
    with pytest.raises(InputError):
        user_profile_sethandle_v1(token, handle)

##########################################################################################
# user_stats tests

def test_user_stats(register_login):
    token1 = register_login["Token1"]
    id1 = register_login["ID1"]
    token2 = register_login["Token2"]
    id2 = register_login["ID2"]

    # Create some channels
    channel1 = channels_create_v2(token1, 'Channel 1', True)
    channel2 = channels_create_v2(token1, 'Channel 2', False)
    channel3 = channels_create_v2(token2, 'Channel 3', True)
    channel4 = channels_create_v2(token2, 'Channel 4', True)
    
    channel_invite_v1(id2, channel3["channel_id"], id1)
    channel_invite_v1(id1, channel1["channel_id"], id2)
    
    # Create and send some dm's (count 2 messages)
    dm1 = dm_create_v1(id1, [id2])
    message_senddm_v1(id1, dm1["dm_id"], "a test dm")
    message_senddm_v1(id2, dm1["dm_id"], "a test response")
    message_senddm_v1(id1, dm1["dm_id"], "a follow up message")

    # Send some messages into channels (count 3 messages)
    message_send_v1(id1, channel1["channel_id"], "hello channel 1")
    message_send_v1(id2, channel1["channel_id"], "hello back channel 1")
    message_send_v1(id1, channel2["channel_id"], "this is empty")
    message_send_v1(id1, channel3["channel_id"], "thanks for the invite")
    message_send_v1(id2, channel3["channel_id"], "no problem")
    message_send_v1(id2, channel4["channel_id"], "none is here")

    stats = user_stats_v1(token1)
    assert stats["channels_joined"]["num_channels_joined"] == 3
    assert stats["dms_joined"]["num_dms_joined"] == 1
    assert stats["messages_sent"]["num_messages_sent"] == 5

""" (To do when error handling is fixed)
def test_user_stats_exception(register_login):
    with pytest.raises(AccessError):
        assert user_stats_v1(999)
"""

##########################################################################################
# users_stats tests

def test_users_stats(register_login):
    token1 = register_login["Token1"]
    id1 = register_login["ID1"]
    token2 = register_login["Token2"]
    id2 = register_login["ID2"]

    # Create another user
    user3 = auth_register_v2("testmail@gmail.com", "password123", "Alex", "Fulton")
    id3 = user3["auth_user_id"]

    # Create some channels (4 channels)
    channel1 = channels_create_v2(token1, 'Channel 1', True)
    channel2 = channels_create_v2(token1, 'Channel 2', False)
    channel3 = channels_create_v2(token2, 'Channel 3', True)
    channel4 = channels_create_v2(token2, 'Channel 4', True)
    
    channel_invite_v1(id2, channel3["channel_id"], id1)
    channel_invite_v1(id1, channel1["channel_id"], id2)
    
    # Create some dm's (3 dm's)
    dm1 = dm_create_v1(id1, [id2])
    dm2 = dm_create_v1(id1, [id3])
    dm3 = dm_create_v1(id2, [id3])

    # Send some dm's (count 3 messages)
    message_senddm_v1(id1, dm1["dm_id"], "a test dm")
    message_senddm_v1(id1, dm2["dm_id"], "a test response")
    message_senddm_v1(id2, dm3["dm_id"], "a follow up message")

    # Send some messages into channels (count 6 messages)
    message_send_v1(id1, channel1["channel_id"], "hello channel 1")
    message_send_v1(id2, channel1["channel_id"], "hello back channel 1")
    message_send_v1(id1, channel2["channel_id"], "this is empty")
    message_send_v1(id1, channel3["channel_id"], "thanks for the invite")
    message_send_v1(id2, channel3["channel_id"], "no problem")
    message_send_v1(id2, channel4["channel_id"], "none is here")

    stats = users_stats_v1(token1)
    assert stats["channels_exist"]["num_channels_exist"] == 4
    assert stats["dms_exist"]["num_dms_exist"] == 3
    assert stats["messages_exist"]["num_messages_exist"] == 9

""" (To do when error handling is fixed)
def test_users_stats_exception(register_login):
    with pytest.raises(AccessError):
        assert users_stats_v1(999)
"""