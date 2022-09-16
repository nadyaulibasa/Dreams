'''
This file includes different tests for both auth_passwordreset
functions.
'''
from src.auth import auth_passwordreset_request_v1, auth_passwordreset_reset_v1, auth_register_v2, auth_login_v2
from src.error import InputError
from src.other import clear_v1
from src.helper import get_id_and_password, create_token
import src.data as d
import pytest

def test_auth_passwordreset_request_and_reset():
    '''
    Tests that the user is able to request for a password reset and then login using the new password
    '''

    clear_v1()
    email = "someemail@gmail.com"
    auth_register_v2(email, "password", "Joel", "Engelman")
    with pytest.raises(InputError):
        assert auth_passwordreset_request_v1("emailnotused@gmail.com")
    auth_passwordreset_request_v1(email)

    code = None
    for user in d.data['users']:
        if email == user['email']:
            code = user['code']
    
    assert code is not None

    auth_passwordreset_reset_v1(code, "password2")
    with pytest.raises(InputError):
        assert auth_login_v2(email, "password2")

def test_auth_passwordreset_invalid_code_and_password():
    clear_v1()
    email = "someemail@gmail.com"
    auth_register_v2(email, "password", "Joel", "Engelman")
    auth_passwordreset_request_v1(email)

    code = None
    for user in d.data['users']:
        if email == user['email']:
            code = user['code']
    
    assert code is not None

    #invalid password test
    with pytest.raises(InputError):
        assert auth_passwordreset_reset_v1(code, "")
    
    #invalid code test
    with pytest.raises(InputError):
       assert auth_passwordreset_reset_v1("invalidcode", "password2")
