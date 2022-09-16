'''
This file includes different tests for auth_register_v2.
These tests include registering with an invalid email, having a duplicate email,
Having a password that is too short,
Having a first name and last name that is both too long and too short (separate tests),
As well as a valid registration.
'''

from src.auth import auth_login_v2, auth_register_v2
from src.error import AccessError, InputError
from src.other import clear_v1
from src.helper import get_id_and_password, create_token
import pytest

#InputErrors:
#Email not valid
def test_auth_register_invalid_email():
    '''
    Test for email entered not being valid.
    '''
    with pytest.raises(InputError):
        assert auth_register_v2("@gmail.com", "password", "Joel", "Engelman")

def test_auth_register_duplicate_email():
    '''
    Test for email entered being a duplicate.
    '''
    clear_v1()
    auth_register_v2("someemail@gmail.com", "password", "Joel", "Engelman")
    with pytest.raises(InputError):
        assert auth_register_v2("someemail@gmail.com", "password2", "Joel", "Engelman")

def test_auth_register_short_password():
    '''
    Test for password entered being too short.
    '''
    with pytest.raises(InputError):
        assert auth_register_v2("someemail@gmail.com", "pass", "Joel", "Engelman")

def test_auth_register_name_first_length_too_short():
    '''
    Test for first name entered being too short.
    '''
    with pytest.raises(InputError):
        assert auth_register_v2("someemail@gmail.com", "password", "", "Engelman")

def test_auth_register_name_first_length_too_long():
    '''
    Test for first name entered being too long.
    '''
    with pytest.raises(InputError):
        assert auth_register_v2("someemail@gmail.com", "pass123",
        "MohammedMohammedMohammedMohammedMohammedMohammed123", "Smith")

def test_auth_register_name_last_length_too_short():
    '''
    Test for last name entered being too short.
    '''
    with pytest.raises(InputError):
        assert auth_register_v2("someemail@gmail.com", "password", "Joel", "")

def test_auth_register_name_last_length_too_long():
    '''
    Test for last name entered being too long.
    '''
    with pytest.raises(InputError):
        assert auth_register_v2("someemail@gmail.com", "password", "Joel",
        "MohammedMohammedMohammedMohammedMohammedMohammed123")

#test to create auth user id
def test_auth_register():
    '''
    Test for correct auth registration.
    '''
    clear_v1()
    token = create_token('joelengelman')
    user_identification = auth_register_v2("someemail@gmail.com", "password", "Joel", "Engelman")
    assert user_identification['token'] == token
    assert user_identification['auth_user_id'] == 0
    assert auth_login_v2("someemail@gmail.com", "password") == user_identification
