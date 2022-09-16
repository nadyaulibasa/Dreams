'''
admin_test.py
Tests for admin.py
'''

import pytest
from src.admin import   admin_user_remove_v1, \
                        admin_userpermission_change_v1
from src.auth import auth_login_v2, auth_register_v2
from src.user import user_profile_v1
from src.channels import channels_create_v2
from src.channel import channel_join_v1
from src.message import message_send_v1
from src.helper import get_user_wPerms, create_token, load_data, save_data, get_channel
from src.other import clear_v1
from src.error import AccessError, InputError
import src.data as d

@pytest.fixture
def register_login():
    '''
    < Fixture registers a user and then logs them in >
    Returns dictionary containing their u_id and tokens
    '''
    clear_v1()
    d.data = load_data()
    # Create users:
    user1 = auth_register_v2("email1@gmail.com", "password1", "Hayden", "Smith")

    user2 = auth_register_v2("email2@gmail.com", "password2", "Nadya", "Ulibasa")

    user3 = auth_register_v2("email3@gmail.com", "password3", "Alex", "Fulton")
    
    return {
        "ID1"   : user1["auth_user_id"],
        "Token1": user1["token"],
        "ID2"   : user2["auth_user_id"],
        "Token2": user2["token"],
        "ID3"   : user3["auth_user_id"],
        "Token3": user3["token"]
    }

##########################################################################################
# admin_user_remove tests

def test_admin_user_remove_valid(register_login):
    '''
    Valid test: An owner user (1) removing a member user (2)
    '''
    token1 = register_login['Token1']
    u_id2 = register_login['ID2']

    channels_create_v2(token1, 'channel1', True)
    channel_join_v1(u_id2, 1)
    print(u_id2)
    print(get_channel(1))
    message_send_v1(u_id2, 1, 'test')
    admin_user_remove_v1(token1, u_id2)

    profile = user_profile_v1(token1, u_id2)
    assert profile['user']['name_first'] == 'Removed user'
    assert profile['user']['name_last'] == 'Removed user'

def test_admin_user_remove_valid_first_owner(register_login):
    ''' 
    Valid test: An owner user (2) removing another owner user (1)
    '''
    token1 = register_login['Token1']
    token2 = register_login['Token2']
    u_id1 = register_login['ID1']
    u_id2 = register_login['ID2']

    admin_userpermission_change_v1(token1, u_id2, 1)
    admin_user_remove_v1(token2, u_id1)

    profile = user_profile_v1(token2, u_id1)
    assert profile['user']['name_first'] == 'Removed user'
    assert profile['user']['name_last'] == 'Removed user'

def test_admin_user_remove_valid_themselves(register_login):
    ''' 
    Valid test: An owner user (2) removing themselves
    '''
    token1 = register_login['Token1']
    token2 = register_login['Token2']
    u_id2 = register_login['ID2']

    admin_userpermission_change_v1(token1, u_id2, 1)
    admin_user_remove_v1(token2, u_id2)

    profile = user_profile_v1(token2, u_id2)
    assert profile['user']['name_first'] == 'Removed user'
    assert profile['user']['name_last'] == 'Removed user'

'''def test_admin_user_remove_invalid_token(register_login):
    u_id = register_login['ID1']
    token = 'invalid_token'

    with pytest.raises(AccessError):
        assert admin_user_remove_v1(token, u_id)'''

def test_admin_user_remove_invalid_uid(register_login):
    ''' 
    Invalid u_id: InputError
    '''
    u_id = 'invalid_uid'
    token = register_login['Token1']

    with pytest.raises(InputError):
        assert admin_user_remove_v1(token, u_id)

def test_admin_user_remove_invalid_only_owner(register_login):
    ''' 
    Invalid: user is the only owner in Dreams, InputError
    '''
    u_id = register_login['ID1']
    token = register_login['Token1']

    with pytest.raises(InputError):
        assert admin_user_remove_v1(token, u_id)

def test_admin_user_remove_invalid_not_owner(register_login):
    ''' 
    Invalid: authorised user is not an owner, AccessError
    '''
    u_id = register_login['ID3']
    token = register_login['Token3']

    with pytest.raises(AccessError):
        assert admin_user_remove_v1(token, u_id)


##########################################################################################
# admin_userpermission_change tests
 
def test_admin_userpermission_change_valid(register_login):
    '''
    Valid test: An owner user changing a member user to an owner
    '''
    token1 = register_login['Token1']
    u_id2 = register_login['ID2']
    permission_id = 1

    admin_userpermission_change_v1(token1, u_id2, permission_id)

    user = get_user_wPerms(u_id2)
    assert user['permission'] == permission_id

def test_admin_userpermission_change_valid_themselves(register_login):
    '''
    Valid test: An owner user changing their own permission to a member
    '''
    # User 1 and 2 are both owners
    token1 = register_login['Token1']
    u_id2 = register_login['ID2']
    permission_id = 1
    admin_userpermission_change_v1(token1, u_id2, permission_id)

    # User 1 changed to owner
    u_id1 = register_login['ID1']
    permission_id = 2
    admin_userpermission_change_v1(token1, u_id1, permission_id)

    user = get_user_wPerms(u_id1)
    assert user['permission'] == permission_id

def test_admin_userpermission_change_valid_same_permission(register_login):
    '''
    Valid test: An owner user changing a permission with the same permission
                as before
    '''
    token1 = register_login['Token1']
    u_id2 = register_login['ID2']
    permission_id = 2

    admin_userpermission_change_v1(token1, u_id2, permission_id)

    user = get_user_wPerms(u_id2)
    print(user)
    assert user['permission'] == permission_id

'''def test_admin_userpermission_change_invalid_token(register_login):
    u_id = register_login['ID1']
    token = 'invalid_token'
    permission_id = 1

    with pytest.raises("AccessError"):
        assert admin_userpermission_change_v1(token, u_id, permission_id)'''

def test_admin_userpermission_change_invalid_uid(register_login):
    ''' 
    Invalid u_id: InputError
    '''
    u_id = 'invalid_uid'
    token = register_login['Token1']
    permission_id = 1

    with pytest.raises(InputError):
        assert admin_userpermission_change_v1(token, u_id, permission_id)

def test_admin_userpermission_change_invalid_permission(register_login):
    ''' 
    Invalid permission_id: InputError
    '''
    u_id = register_login['ID1']
    token = register_login['Token1']
    permission_id = 99

    with pytest.raises(InputError):
        assert admin_userpermission_change_v1(token, u_id, permission_id)

def test_admin_userpermission_remove_invalid_not_owner(register_login):
    ''' 
    Invalid: authorised user is not an owner, AccessError
    '''
    u_id = register_login['ID1']
    token = register_login['Token2']
    permission_id = 1

    with pytest.raises(AccessError):
        assert admin_userpermission_change_v1(token, u_id, permission_id)
  