'''
This file includes different tests for auth_login_v2.
These tests include having an invalid email, the email not matching,
Having an incorrect password, valid email & password as well as multiple valid users.
'''

from src.auth import auth_login_v2, auth_register_v2
from src.error import AccessError, InputError
from src.helper import reset_data, create_token, get_id_and_password
import pytest

@pytest.fixture
def fix_setup():
    '''
    Setting up the fixture
    '''
    reset_data()
    user1 = auth_register_v2("someemail@gmail.com", "password", "Joel", "Engelman")
    user2 = auth_register_v2("someemail2@gmail.com", "password2", "John", "Smith")
    return {'user1' : user1['token'], 'user2' : user2['token']}

#invalid email test
def test_auth_login_invalid_email():
    '''
    Tests for invalid email.
    '''

    email = "@gmail.com"
    password = "password"
    with pytest.raises(InputError):
        assert auth_login_v2(email, password)

#email does not match
def test_auth_login_email_not_match(fix_setup):
    '''
    Tests for email not matching.
    '''

    email = "123abc@gmail.com"
    password = "password"
    with pytest.raises(InputError):
        assert auth_login_v2(email, password)

#incorrect password
def test_auth_login_incorrect_password(fix_setup):
    '''
    Tests for incorrect password.
    '''

    email = "abc123@gmail.com"
    password = "incorrect"
    with pytest.raises(InputError):
        assert auth_login_v2(email, password)

#test correct output
def test_auth_login_output(fix_setup):
    '''
    Tests for correct login output.
    '''

    email = "someemail@gmail.com"
    password = "password"
    assert auth_login_v2(email, password) == {'token' : fix_setup['user1'], 'auth_user_id' : 0}

#test correct output with multiple users
def test_auth_login_output_multiple_users(fix_setup):
    '''
    Tests for correct login output with multiple users.
    '''

    email = "someemail@gmail.com"
    password = "password"
    assert auth_login_v2(email, password) == {'token' : fix_setup['user1'], 'auth_user_id' : 0}

    email_2 = "someemail2@gmail.com"
    password_2 = "password2"
    assert auth_login_v2(email_2, password_2) == {'token' : fix_setup['user2'], 'auth_user_id' : 1}
    reset_data()
