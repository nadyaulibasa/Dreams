from src.channel import channel_invite_v1, \
                        channel_details_v1,\
                        channel_join_v1, \
                        channel_messages_v1, \
                        channel_removeowner_v1, \
                        channel_addowner_v1, \
                        channel_invite_v1, \
                        channel_leave_v1
from src.auth import auth_login_v2, auth_register_v2
from src.channels import channels_create_v2, channels_list_v2, channels_listall_v2
from src.error import AccessError, InputError
from src.helper import get_channel, get_user, create_token
from src.message import message_send_v1
from src.other import clear_v1
import pytest

@pytest.fixture
def Case1():
    clear_v1()
    User1 = auth_register_v2("email@gmail.com", "password1", "david", "peng")
    User2 = auth_register_v2("email2@gmail.com", "password2", "krishnan", "winter")
    User3 = auth_register_v2("email3@gmail.com", "password3", "joel", "engelman")
    Channel1 = channels_create_v2(create_token("davidpeng"), "example channel", True)
    Channel2 = channels_create_v2(create_token("krishnanwinter"), "example channel 2", False)
    Channel3 = channels_create_v2(create_token("davidpeng"), "example channel 3", False)
    return {"ID1": User1["auth_user_id"], "ID2": User2["auth_user_id"], "ID3": User3["auth_user_id"], "CH1": Channel1["channel_id"], "CH2": Channel2["channel_id"], "CH3": Channel3["channel_id"]}

# channel_invite_v1 tests
def test_channel_invite_no_user(Case1):
    #user does not exist
    with pytest.raises(InputError):
        assert channel_invite_v1(Case1["ID1"], Case1["CH1"], 4)

def test_channel_invite_no_channel(Case1):
    #channel does not exist
    with pytest.raises(InputError):
        assert channel_invite_v1(Case1["ID1"], 100, Case1["ID2"])

def test_channel_invite_already_member(Case1):
    #inviting a member who is already in the channel
    with pytest.raises(InputError):
        assert channel_invite_v1(Case1["ID1"], Case1["CH1"], Case1["ID1"])

def test_channel_invite_no_access(Case1):
    #auth user does not have access
    with pytest.raises(AccessError):
        assert channel_invite_v1(Case1["ID2"], Case1["CH1"], Case1["ID3"])

# Testing the expected output when the function succesfully runs
def test_channel_invite_output(Case1):
    channel_invite_v1(Case1["ID1"], Case1["CH1"], Case1["ID2"])
    assert get_user(Case1["ID1"]) in channel_details_v1(Case1["ID1"], Case1["CH1"])["all_members"]

# Testing the expected output when the function succesfully runs
def test_channel_invite_output2(Case1):
    channel_invite_v1(Case1["ID1"], Case1["CH3"], Case1["ID2"])
    assert get_user(Case1["ID2"]) in channel_details_v1(Case1["ID1"], Case1["CH3"])["all_members"]

# channel_details_v1 tests

def test_channel_details_no_channel(Case1):
    #Channel does not exist
    with pytest.raises(InputError):
        assert channel_details_v1(Case1["ID1"], 100)

def test_channel_details_no_access(Case1):
    #User is not a member of the Channel
    with pytest.raises(AccessError):
        assert channel_details_v1(Case1["ID3"], Case1["CH2"])

def test_channel_messages_past_start(Case1):
    #Start > total messages
    with pytest.raises(InputError):
        assert channel_messages_v1(Case1["ID1"], Case1["CH1"], 30)

def test_channel_messages_not_member(Case1):
    #Auth user not a member of Channel
    with pytest.raises(AccessError):
        assert channel_messages_v1(Case1["ID2"], Case1["CH1"], 0)

# Testing the expected output when the function succesfully runs
def test_channel_detail_output(Case1):
    details = channel_details_v1(Case1["ID1"], Case1["CH1"])
    channel = get_channel(Case1["CH1"])
    assert channel["name"] == details["name"]
    assert channel["owner_members"] == details["owner_members"]
    assert channel["all_members"] == details["all_members"]
    
def test_channel_messages_no_channel(Case1):
    #Channel does not exist
    with pytest.raises(InputError):
        assert channel_messages_v1(Case1["ID1"], 56, 0)

def test_channel_messages_start_invalid(Case1):
    # Testing if the start index is less than the size of the message list
    with pytest.raises(InputError):
        assert channel_messages_v1(Case1["ID1"], Case1["CH1"], 5)


def test_channel_messages_negative_end(Case1):
    # Has an iterative loop that will send out the designated amount of messages
    # utilisng the message_send_v1 function, however it has not been 
    # implemented yet
    # Creating 20 Messages in Channel 1
    i = 0
    for i in range(0,20):
        message_send_v1(Case1["ID1"], Case1["CH1"], f"{i}")
        i += 1
    message_return = channel_messages_v1(Case1["ID1"], Case1["CH1"], 0)

    assert len(message_return["messages"]) == i


def test_channel_messages_normal_output(Case1):
    i = 0
    # Creating 50 Messages in Channel 1
    for i in range(0,50):
        message_send_v1(Case1["ID1"], Case1["CH1"], f"{i}")
        i += 1
    message_return = channel_messages_v1(Case1["ID1"], Case1["CH1"], 0)

    assert len(message_return["messages"]) == i


# channel_join_v1 tests

def test_channel_join_private(Case1):
    #Trying to join a private Channel
    with pytest.raises(AccessError):
        assert channel_join_v1(Case1["ID2"], Case1["CH3"])

def test_channel_join_no_channel(Case1):
    #Joining a Channel which does not exist
    with pytest.raises(InputError):
        assert channel_join_v1(Case1["ID1"], 18)

def test_channel_join_no_user(Case1):
    with pytest.raises(InputError):
        assert channel_join_v1(90000, Case1["CH2"])

def test_channel_join_already_member(Case1):
    with pytest.raises(InputError):
        assert channel_join_v1(Case1["ID1"], Case1["CH1"])

# Testing the expected output when the function succesfully runs
def test_channel_join_output(Case1):
    channel_join_v1(Case1["ID2"], Case1["CH1"])
    # If we get any valid return value, then member must now be apart of the 
    # channel
    assert get_user(Case1["ID2"]) in channel_details_v1(Case1["ID2"], Case1["CH1"])["all_members"]

def test_channel_join_global_owner(Case1):
    channel_join_v1(Case1["ID1"], Case1["CH2"])
    # If we get any valid return value, then member must now be apart of the 
    # channel
    assert get_user(Case1["ID1"]) in get_channel(Case1["CH2"])["all_members"]

# channel_addowner

def test_channel_addowner_no_channel(Case1):
    with pytest.raises(InputError):
        assert channel_addowner_v1(Case1["ID1"], 999999, Case1["ID2"])

def test_channel_addowner_user_already_owner(Case1):
    with pytest.raises(InputError):
        assert channel_addowner_v1(Case1["ID1"], Case1["CH1"], Case1["ID1"])

def test_channel_addowner_not_auth(Case1):
    channel_invite_v1(Case1["ID1"], Case1["CH1"], Case1["ID2"])
    with pytest.raises(AccessError):
        assert channel_addowner_v1(Case1["ID2"], Case1["CH1"], Case1["ID3"])

def test_channel_addowner_valid(Case1):
    channel_addowner_v1(Case1["ID1"], Case1["CH1"], Case1["ID2"])
    channel = get_channel(Case1["CH1"])
    assert get_user(Case1["ID2"]) in channel["owner_members"]

# channel_removeowner

def test_channel_removeowner_no_channel(Case1):
    with pytest.raises(InputError):
        assert channel_removeowner_v1(Case1["ID1"], 999999, Case1["ID2"])

def test_channel_removeowner_not_owner(Case1):
    with pytest.raises(InputError):
        assert channel_removeowner_v1(Case1["ID2"], Case1["CH2"], Case1["ID3"])

def test_channel_removeowner_single_owner(Case1):
    with pytest.raises(InputError):
        assert channel_removeowner_v1(Case1["ID1"], Case1["CH1"], Case1["ID1"])

def test_channel_removeowner_not_auth(Case1):
    channel_invite_v1(Case1["ID1"], Case1["CH1"], Case1["ID2"])
    channel_invite_v1(Case1["ID1"], Case1["CH1"], Case1["ID3"])
    channel_addowner_v1(Case1["ID1"], Case1["CH1"], Case1["ID2"])

    with pytest.raises(AccessError):
        assert channel_removeowner_v1(Case1["ID3"], Case1["CH1"], Case1["ID1"])

def test_channel_removeowner_valid(Case1):
    channel_invite_v1(Case1["ID1"], Case1["CH1"], Case1["ID2"])
    channel_invite_v1(Case1["ID1"], Case1["CH1"], Case1["ID3"])
    channel_addowner_v1(Case1["ID1"], Case1["CH1"], Case1["ID2"])

    channel_removeowner_v1(Case1["ID1"], Case1["CH1"], Case1["ID1"])

    channel = get_channel(Case1["CH1"])

    assert get_user(Case1["ID2"]) in channel["owner_members"]
    assert get_user(Case1["ID1"]) not in channel["owner_members"]

# channel_leave

def test_channel_leave_invalid_channel(Case1):
    with pytest.raises(InputError):
        assert channel_leave_v1(Case1["ID1"], 999999)

def test_channel_leave_not_member(Case1):
    with pytest.raises(AccessError):
        assert channel_leave_v1(Case1["ID2"], Case1["CH1"])
    
def test_channel_leave_valid(Case1):
    channel_invite_v1(Case1["ID1"], Case1["CH1"], Case1["ID2"])
    channel_leave_v1(Case1["ID2"], Case1["CH1"])

    channel = get_channel(Case1["CH1"])

    assert get_user(Case1["ID2"]) not in channel["all_members"]



