import pytest
from src.auth import auth_register_v2 as auth_register_v1, auth_login_v2 as auth_login_v1
from src.channels import channels_create_v2 as channels_create_v1, channels_listall_v2 as channels_listall_v1
from src.message import message_send_v1
from src.error import AccessError, InputError
from src.other import clear_v1, search_v1
from src.helper import create_token

@pytest.fixture
def Case1():
    clear_v1()
    User1 = auth_register_v1("email@gmail.com", "password1", "david", "peng")
    User2 = auth_register_v1("email2@gmail.com", "password2", "david", "peng")
    User3 = auth_register_v1("email3@gmail.com", "password3", "david", "peng")
    Channel1 = channels_create_v1(create_token("davidpeng"), "example channel", True)
    Channel2 = channels_create_v1(create_token("davidpeng"), "example channel 2", False)
    return {"ID1": User1["auth_user_id"], "ID2": User2["auth_user_id"], "ID3": User3["auth_user_id"], "CH1": Channel1["channel_id"], "CH2": Channel2["channel_id"]}

def test_clear_users(Case1):
    clear_v1()
    with pytest.raises(InputError):
        assert auth_login_v1("email@gmail.com", "password1")

def test_clear_channels(Case1):
    clear_v1()
    assert len(channels_listall_v1(Case1["ID1"])['channels']) == 0

def test_search(Case1):
    for _ in range(50):
        message_send_v1(Case1['ID1'], Case1['CH1'], "Hello World")
    for _ in range(10):
        message_send_v1(Case1['ID1'], Case1['CH1'], "Hello World22")

    assert len(search_v1(Case1['ID1'], "Hello World")['messages']) == 50
    