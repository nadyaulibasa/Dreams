import pytest
from src.error import AccessError, InputError
from src.other import clear_v1
from src.helper import get_user, get_dm, get_message
from src.auth import auth_register_v2 as auth_register_v1
from src.message import message_senddm_v1, message_remove_v1
from src.dm import dm_create_v1, dm_details_v1, dm_invite_v1, dm_list_v1, dm_messages_v1, dm_remove_v1, dm_leave_v1
'''
Tests for:
    dm_create_v1(ID, u_ids) => { dm_id, dm_name }
    dm_invite_v1(ID, dm_id, u_id) => {}
    dm_details_v1(ID, dm_id) => { name, members }
    dm_list_v1(ID) => { dms }
    dm_remove_v1(ID, dm_id) => {}
    dm_messages_v1(ID, dm_id, start) => { messages, start, end }
    dm_leave_v1(ID, dm_id)

'''
def get_dm_listformat(dm_id):
    dm = get_dm(dm_id)
    return {
        'dm_id': dm['dm_id'],
        'name': dm['name']
    }


@pytest.fixture
def Case1():
    clear_v1()
    User1 = auth_register_v1("email2@gmail.com", "password2", "David", "Peng")
    User2 = auth_register_v1("email3@gmail.com", "password3", "Krishnan", "Winter")
    User3 = auth_register_v1("email4@gmail.com", "password4", "Joel", "Engelman")
    User4 = auth_register_v1("email@gmail.com", "password1", "David", "Peng")
    return {"ID1": User1["auth_user_id"], "ID2": User2["auth_user_id"], "ID3": User3["auth_user_id"], "ID4": User4['auth_user_id']}

@pytest.fixture
def Case1ext(Case1):
    dm1 = dm_create_v1(Case1["ID1"], [Case1["ID2"], Case1["ID3"]])
    dm2 = dm_create_v1(Case1["ID1"], [Case1["ID2"]])
    dm3 = dm_create_v1(Case1["ID2"], [Case1["ID3"]])
    dm4 = dm_create_v1(Case1["ID1"], [Case1["ID2"], Case1["ID3"], Case1["ID4"]])
    return {
        "ID1": Case1["ID1"], 
        "ID2": Case1["ID2"], 
        "ID3": Case1["ID3"], 
        "ID4": Case1["ID4"], 
        "DMID1": dm1['dm_id'],
        "DMID2": dm2['dm_id'],
        "DMID3": dm3['dm_id'],
        "DMID4": dm4['dm_id'],
    }

def test_dm_create_no_uid(Case1):
    with pytest.raises(InputError):
        assert dm_create_v1(Case1['ID1'], [5, 6])

def test_dm_create_duplicate_uid(Case1): #need assumption
    with pytest.raises(InputError):
        assert dm_create_v1(Case1['ID1'], [5, 6])

def test_dm_create_valid_1(Case1):
    dm = dm_create_v1(Case1['ID1'], [Case1["ID2"]])
    assert dm['dm_id'] == 0
    assert dm['dm_name'] == 'davidpeng, krishnanwinter'

def test_dm_create_valid_2(Case1):
    dm = dm_create_v1(Case1['ID1'], [Case1["ID2"], Case1["ID3"]])
    assert dm['dm_id'] == 0
    assert dm['dm_name'] == 'davidpeng, joelengelman, krishnanwinter'

def test_dm_create_valid_3(Case1): #need assumption, handle start at 0, index of dm_id start at 0
    dm = dm_create_v1(Case1['ID1'], [Case1["ID2"], Case1["ID3"], Case1["ID4"]])
    assert dm['dm_id'] == 0
    assert dm['dm_name'] == 'davidpeng, davidpeng0, joelengelman, krishnanwinter'

def test_dm_create_invalid_1_wrong(Case1):
    with pytest.raises(InputError):
        assert dm_create_v1(Case1['ID1'], [Case1["ID2"], Case1["ID3"], Case1["ID4"], 5])

def test_dm_invite_nodm(Case1ext):
    with pytest.raises(InputError):
        assert dm_invite_v1(Case1ext['ID1'], 5, Case1ext["ID1"])

def test_dm_invite_noid2(Case1ext):
    with pytest.raises(InputError):
        assert dm_invite_v1(Case1ext['ID1'], Case1ext['DMID1'], 50)

def test_dm_invite_noid(Case1ext):
    with pytest.raises(InputError):
        assert dm_invite_v1(50, Case1ext['DMID1'], Case1ext["ID4"])

def test_dm_invite_notMember(Case1ext):
    with pytest.raises(AccessError):
        assert dm_invite_v1(Case1ext['ID1'], Case1ext["DMID3"], Case1ext["ID4"])

def test_dm_invite_valid(Case1ext):
    dm_invite_v1(Case1ext['ID1'], Case1ext["DMID1"], Case1ext["ID4"])
    assert get_user(Case1ext["ID4"]) in dm_details_v1(Case1ext['ID1'], Case1ext['DMID1'])['members']

def test_dm_invite_valid2(Case1ext):
    dm_invite_v1(Case1ext['ID1'], Case1ext["DMID1"], Case1ext["ID4"])
    dm_invite_v1(Case1ext['ID1'], Case1ext["DMID1"], Case1ext["ID3"])
    assert get_user(Case1ext["ID4"]) in dm_details_v1(Case1ext['ID1'], Case1ext['DMID1'])['members']
    assert get_user(Case1ext["ID3"]) in dm_details_v1(Case1ext['ID1'], Case1ext['DMID1'])['members']

def test_dm_details_nodm(Case1ext):
    with pytest.raises(InputError):
        assert dm_details_v1(Case1ext['ID1'], 5)

def test_dm_details_noid(Case1ext):
    with pytest.raises(AccessError):
        assert dm_details_v1(Case1ext['ID1'], Case1ext['DMID3'])

def test_dm_details_valid(Case1ext):
    dm = dm_details_v1(Case1ext['ID1'], Case1ext['DMID1'])
    assert dm['name'] == 'davidpeng, joelengelman, krishnanwinter'
    assert get_user(Case1ext["ID1"]) in dm['members']
    assert get_user(Case1ext["ID2"]) in dm['members']
    assert get_user(Case1ext["ID3"]) in dm['members']

def test_dm_details_valid2(Case1ext):
    dm = dm_details_v1(Case1ext['ID1'], Case1ext['DMID4'])
    assert dm['name'] == 'davidpeng, davidpeng0, joelengelman, krishnanwinter'
    assert get_user(Case1ext["ID1"]) in dm['members']
    assert get_user(Case1ext["ID2"]) in dm['members']
    assert get_user(Case1ext["ID3"]) in dm['members']
    assert get_user(Case1ext["ID4"]) in dm['members']

def test_dm_list_noID(Case1ext):
    with pytest.raises(InputError):
        assert dm_list_v1(5000)

def test_dm_list_valid(Case1ext):
    assert len(dm_list_v1(0)['dms']) == 3

def test_dm_list_Case1ext(Case1ext): 
    assert get_dm_listformat(Case1ext['DMID1']) in dm_list_v1(Case1ext['ID1'])['dms']
    assert get_dm_listformat(Case1ext['DMID2']) in dm_list_v1(Case1ext['ID1'])['dms']
    assert get_dm_listformat(Case1ext['DMID4']) in dm_list_v1(Case1ext['ID1'])['dms']
    assert get_dm_listformat(Case1ext['DMID1']) in dm_list_v1(Case1ext['ID2'])['dms']
    assert get_dm_listformat(Case1ext['DMID2']) in dm_list_v1(Case1ext['ID2'])['dms']
    assert get_dm_listformat(Case1ext['DMID3']) in dm_list_v1(Case1ext['ID2'])['dms']
    assert get_dm_listformat(Case1ext['DMID4']) in dm_list_v1(Case1ext['ID2'])['dms']


def test_dm_remove_noDm(Case1ext):
    with pytest.raises(InputError):
        assert dm_remove_v1(Case1ext['ID1'], 5)

def test_dm_remove_notCreator(Case1ext):
    with pytest.raises(AccessError):
        assert dm_remove_v1(Case1ext['ID2'], Case1ext['DMID1'])

def test_dm_remove_notMember(Case1ext):
    with pytest.raises(AccessError):
        assert dm_remove_v1(123412341, Case1ext['DMID1'])
    
def test_dm_remove_valid(Case1ext):
    dm_remove_v1(Case1ext['ID1'], Case1ext['DMID1'])
    with pytest.raises(InputError):
        dm_details_v1(Case1ext['ID1'], Case1ext['DMID1'])

def test_dm_remove_valid2(Case1ext):
    dm_remove_v1(Case1ext['ID2'], Case1ext['DMID3'])
    with pytest.raises(InputError):
        dm_details_v1(Case1ext['ID2'], Case1ext['DMID3'])

def test_dm_message_noDM(Case1ext):
    with pytest.raises(InputError):
        assert dm_messages_v1(Case1ext['ID1'], 5, 0)
    
def test_dm_message_bigStart(Case1ext):
    message_senddm_v1(Case1ext["ID1"], Case1ext["DMID1"], "Hello World")
    with pytest.raises(InputError):
        assert dm_messages_v1(Case1ext['ID1'], Case1ext["DMID1"], 3)

def test_dm_message_notMember(Case1ext):
    message_senddm_v1(Case1ext["ID1"], Case1ext["DMID1"], "Hello World")
    with pytest.raises(AccessError):
        assert dm_messages_v1(Case1ext['ID4'], Case1ext["DMID1"], 0)

def test_dm_message_valid(Case1ext):
    messageID = message_senddm_v1(Case1ext["ID1"], Case1ext["DMID1"], "Hello World")['message_id']
    assert dm_messages_v1(Case1ext['ID1'], Case1ext["DMID1"], 0) == {
        'messages': [get_message(messageID)],
        'start': 0,
        'end': -1
    }

def test_dm_message_valid2(Case1ext):
    messageID1 = message_senddm_v1(Case1ext["ID1"], Case1ext["DMID1"], "Hello World")['message_id']
    messageID2 = message_senddm_v1(Case1ext["ID2"], Case1ext["DMID1"], "Hello World")['message_id']
    print(dm_messages_v1(Case1ext['ID1'], Case1ext["DMID1"], 1))
    print("/////////")
    print({
        'messages': [get_message(messageID1), get_message(messageID2)],
        'start': 1,
        'end': -1
    })
    assert dm_messages_v1(Case1ext['ID1'], Case1ext["DMID1"], 1) == {
        'messages': [get_message(messageID2)],
        'start': 1,
        'end': -1
    }

def test_dm_message_valid100(Case1ext):
    messageIDs = []
    for _ in range(100):
        messageIDs.append(message_senddm_v1(Case1ext["ID1"], Case1ext["DMID1"], "Hello World")['message_id'])

    dms = dm_messages_v1(Case1ext['ID1'], Case1ext["DMID1"], 37)['messages']
    print(dms[0])
    assert get_message(messageIDs[13]) in dms
    assert get_message(messageIDs[38]) in dms
    assert get_message(messageIDs[56]) in dms
    assert get_message(messageIDs[58]) in dms
    assert get_message(messageIDs[86]) not in dms
    assert get_message(messageIDs[87]) not in dms
    assert get_message(messageIDs[88]) not in dms

def test_dm_message_validRemoval(Case1ext):
    messageIDs = []
    for _ in range(100):
        messageIDs.append(message_senddm_v1(Case1ext["ID1"], Case1ext["DMID1"], "Hello World")['message_id'])
        
    message_remove_v1(Case1ext["ID1"], messageIDs[58])

    assert get_message(messageIDs[58]) not in dm_messages_v1(Case1ext['ID1'], Case1ext["DMID1"], 37)['messages']


def test_dm_leave_noDM(Case1ext):
    with pytest.raises(InputError):
        assert dm_leave_v1(Case1ext["ID1"], 50000)

def test_dm_leave_inactive(Case1ext):
    dm_remove_v1(Case1ext["ID1"], Case1ext["DMID1"])
    with pytest.raises(InputError):
        assert dm_leave_v1(Case1ext["ID1"], Case1ext["DMID1"])
        
def test_dm_leave_notmember(Case1ext):
    with pytest.raises(AccessError):
        assert dm_leave_v1(500000, Case1ext["DMID1"])

def test_dm_leave_valid(Case1ext):
    dm_leave_v1(Case1ext["ID1"], Case1ext["DMID1"])
    assert get_user(Case1ext["ID1"]) not in get_dm(Case1ext["DMID1"])['members']