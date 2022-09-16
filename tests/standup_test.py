'''
standup_test.py

Tests for the following functions:
standup_start_v1
standup_active_v1
standup_send_v1
'''

import pytest
from src.standup import standup_start_v1, \
                        standup_active_v1, \
                        standup_send_v1
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.channel import channel_join_v1, channel_messages_v1
from src.error import AccessError, InputError
from src.helper import create_token, get_user
from src.other import clear_v1
from time import sleep

@pytest.fixture
def register_users_channels():
    clear_v1()

    owner = auth_register_v2('user1@gmail.com', 'password1', 'Hayden', 'Smith')
    channel1= channels_create_v2(owner['token'], 'Channel1', True)
    channel2= channels_create_v2(owner['token'], 'Channel2', True)

    member = auth_register_v2('user2@gmail.com', 'password2', 'Nadya', 'Ulibasa')
    channel_join_v1(member['auth_user_id'], channel2['channel_id'])

    return {
        'c_id1': channel1['channel_id'], 
        'c_id2': channel2['channel_id'],
        'owner': owner, 
        'member': member, 
    }

################################ STANDUP_START TESTS ####################################
'''def test_standup_start_invalid_token(register_users_channels):
    token = create_token('invalid_token')
    channel_id = register_users_channels['c_id2']
    length = 1
    with pytest.raises(AccessError):
        standup_start_v1(token, channel_id, length)'''

def test_standup_start_invalid_channel(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = 3 
    length = 1
    with pytest.raises(InputError):
        standup_start_v1(token, channel_id, length)

def test_standup_start_invalid_activestandup(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']
    length = 1

    # Start standup
    time_finish = standup_start_v1(token, channel_id, length)['time_finish']
    result = standup_active_v1(token, channel_id)
    assert result['is_active']
    assert result['time_finish'] == time_finish

    # Ensure that another standup cannot be started
    with pytest.raises(InputError):
       standup_start_v1(token, channel_id, length) 
    
    sleep(length)

def test_standup_start_valid_owner(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']
    length = 1
    standup_start_v1(token, channel_id, length)

    standup = standup_active_v1(token, channel_id)
    assert standup['is_active']

    sleep(length)

def test_standup_start_valid_member(register_users_channels):
    token = register_users_channels['member']['token']
    channel_id = register_users_channels['c_id2']
    length = 1
    standup_start_v1(token, channel_id, length)

    standup = standup_active_v1(token, channel_id)
    assert standup['is_active']

    sleep(length)


############################### STANDUP_ACTIVE TESTS ####################################
'''def test_standup_active_invalid_token(register_users_channels):
    token = create_token('invalid')
    channel_id = register_users_channels['c_id2']
    with pytest.raises(AccessError):
        standup_active_v1(token, channel_id)'''

def test_standup_active_invalid_channel(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = 3 
    with pytest.raises(InputError):
        standup_active_v1(token, channel_id)

def test_standup_active_valid_active(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']
    length = 1

    # Start standup
    time_finish = standup_start_v1(token, channel_id, length)['time_finish']
    result = standup_active_v1(token, channel_id)
    assert result['is_active'] == True
    assert result['time_finish'] == time_finish
    
    sleep(length)

def test_standup_active_valid_inactive(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']
    
    # No standup started
    result = standup_active_v1(token, channel_id)
    assert result['is_active'] == False
    assert result['time_finish'] == None

'''
def test_standup_active_valid_double(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']
    length = 1

    # Start first standup
    time_finish = standup_start_v1(token, channel_id, length)['time_finish']
    result = standup_active_v1(token, channel_id)
    assert result['is_active'] == True
    assert result['time_finish'] == time_finish

    # Ensure first standup has finished
    sleep(length)
    result = standup_active_v1(token, channel_id)
    assert result['is_active'] == False
    assert result['time_finish'] == None

    # Start second standup
    time_finish = standup_start_v1(token, channel_id, length)['time_finish']
    result = standup_active_v1(token, channel_id)
    assert result['is_active'] == True
    assert result['time_finish'] == time_finish
    
    # Ensure second standup has finished
    sleep(length)
    result = standup_active_v1(token, channel_id)
    assert result['is_active'] == False
    assert result['time_finish'] == None
'''


################################ STANDUP_SEND TESTS #####################################
'''def test_standup_send_invalid_token(register_users_channels):
    token = create_token('invalid')
    channel_id = register_users_channels['c_id2']
    message = 'invalid token'
    with pytest.raises(AccessError):
        standup_send_v1(token, channel_id, message)'''

def test_standup_send_invalid_user(register_users_channels):
    token = register_users_channels['member']['token']
    channel_id = register_users_channels['c_id1']
    message = 'invalid not a member of channel'
    with pytest.raises(AccessError):
        standup_send_v1(token, channel_id, message)

def test_standup_send_invalid_channel(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = 3
    message = 'invalid channel id'
    with pytest.raises(InputError):
        standup_send_v1(token, channel_id, message)

def test_standup_send_invalid_message(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']
    message = 100 * 'invalid message is too long'
    with pytest.raises(InputError):
        standup_send_v1(token, channel_id, message)

def test_standup_send_invalid_activestandup(register_users_channels):
    token = register_users_channels['owner']['token']
    channel_id = register_users_channels['c_id2']
    message = 'invalid there is no active standup'

    assert standup_active_v1(token, channel_id)['is_active'] == False

    with pytest.raises(InputError):
       standup_send_v1(token, channel_id, message)

def test_standup_send_valid(register_users_channels):
    token = register_users_channels['owner']['token']
    # u_id = register_users_channels['owner']['auth_user_id']
    channel_id = register_users_channels['c_id2']
    length = 2

    # Start standup
    time_finish = standup_start_v1(token, channel_id, length)['time_finish']
    result = standup_active_v1(token, channel_id)
    assert result['is_active']
    assert result['time_finish'] == time_finish

    # Send messages
    standup_send_v1(token, channel_id, 'Test Message 1')
    standup_send_v1(token, channel_id, 'Test Message 2')

    # Wait until standup finishes
    sleep(length)

    '''channel_messages = channel_messages_v1(u_id, channel_id, 0)['messages']
    messages = channel_messages[0]
    handle_str = get_user(u_id)['handle_str']
    standup_messages = f"{handle_str}: Test Message 1\n" + f"{handle_str}: Test Message 2\n"

    assert messages['message'] == standup_messages'''
