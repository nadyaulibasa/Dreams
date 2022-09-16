import src.data as d
import pytest
from src.helper import get_user, user_exists, dm_exists, get_dm, get_message, load_data, save_data, gen_dms_list, dm_name_gen, get_handles, add_dm_to_data, dm_remove_invalid_messages, refresh_reacts
from src.error import AccessError, InputError

def dm_create_v1(auth_u_id, uids):
    '''
    This function creates a dm with the auth_u_id as creator and uids as members

    Arguments:
    auth_u_id (Integer)    - u_id of the Creator/Owner of the dm
    uids (List[int])       - List of u_ids to be added to the dm

    Return Value:
        Returns {
            "dm_id": Integer,
            "dm_name": String
        } 
    '''
    handles = get_handles(auth_u_id, uids)
    dm_id = len(d.data['dms'])
    dm_name = dm_name_gen(handles)
    add_dm_to_data(auth_u_id, [get_user(user) for user in uids], dm_id, dm_name)
    return { 
     'dm_id': dm_id,
     'dm_name': dm_name
    }

def dm_invite_v1(auth_u_id, dm_id, u_id):
    '''
    This invites someone to a dm that the authorized user is a part of

    Arguments:
    auth_u_id (Integer)    - u_id of the inviter
    u_id (Integer)         - u_id of the invitee
    dm_id (Integer)        - dm_id of the dm the inviter is inviting the invitee

    Exceptions:
        InputError - Occurs when
            1. dm_id does not correspond with a valid dm
            2. dm_id corresponds to a deleted dm
            3. auth_u_id does not correspond to a valid user
            4. u_id does not correspond to a valid user
        AccessError - Occurs when
            1. auth_u_id is not a member of the dm specified

    Return Value:
        Returns { } 
    '''
    if user_exists(auth_u_id) == False or user_exists(u_id) == False:
        raise InputError
    if dm_exists(dm_id) == False:
        raise InputError
    dm = get_dm(dm_id)
    if dm['active'] == False:
        raise InputError
    if get_user(auth_u_id) not in dm['members']:
        raise AccessError

    invitee = get_user(u_id)

    dm['members'].append(invitee)
    save_data()
    return {}

def dm_details_v1(auth_u_id, dm_id):
    '''
    This function returns the details of a dm given the dm_id and a member of that dm

    Arguments:
    auth_u_id (Integer)    - authorized user
    dm_id (Integer)        - dm_id of the dm the user is requesting

    Exceptions:
        InputError - Occurs when
            1. dm_id does not correspond with a valid dm
            2. dm_id corresponds to a deleted dm
            3. auth_u_id does not correspond to a valid user
        AccessError - Occurs when
            1. auth_u_id is not a member of the dm specified

    Return Value:
        Returns {
            "dm_name": String,
            "members": [List of users that are members of the dm],
        } 
    '''
    if dm_exists(dm_id) == False:
        raise InputError("DM Does not Exist")
    dm = get_dm(dm_id)
    if dm['active'] == False:
        raise InputError("DM has been removed")
    if get_user(auth_u_id) not in dm['members']:
        raise AccessError("User is not member of DM")
    return {
        "name": dm["name"],
        "members": dm["members"]
    }

def dm_list_v1(auth_u_id):
    '''
    This function gets a list that the authorized user is part of

    Arguments:
    auth_u_id (Integer)    - u_id of the user whos list of dms is being shown

    Exceptions:
        InputError - Occurs when
            1. auth_u_id does not correspond to a valid user

    Return Value:
        Returns {
            "dms": [List of dms]
        }
    '''
    if user_exists(auth_u_id) == False:
        raise InputError

    dms = gen_dms_list(auth_u_id)
    return { 'dms': dms}

def dm_leave_v1(auth_u_id, dm_id):
    '''
    This function takes a user that is part of a dm and makes that user leave
    the dm

    Arguments:
    auth_u_id (Integer)    - u_id of the person who wants to leave
    dm_id (Integer)        - dm_id of the dm the user wants to leave

    Exceptions:
        InputError - Occurs when
            1. dm_id does not correspond with a valid dm
            2. dm_id corresponds to a deleted dm
        AccessError - Occurs when
            1. auth_u_id is not a member of the dm specified

    Return Value:
        Returns { } 
    '''
    if dm_exists(dm_id) == False:
        raise InputError
    dm = get_dm(dm_id)
    if dm['active'] == False:
        raise InputError
    if get_user(auth_u_id) not in dm['members']:
        raise AccessError

    dm['members'].remove(get_user(auth_u_id))
    save_data()
    return {}

def dm_remove_v1(auth_u_id, dm_id):
    '''
    This function deletes a dm if the creator is the authorized user

    Arguments:
    auth_u_id (Integer)    - u_id of the creator
    dm_id (Integer)        - dm_id of the dm to be removed

    Exceptions:
        InputError - Occurs when
            1. dm_id does not correspond with a valid dm
            2. dm_id corresponds to a deleted dm
        AccessError - Occurs when
            1. auth_u_id is not the creator of the dm

    Return Value:
        Returns { } 
    '''
    if dm_exists(dm_id) == False:
        raise InputError
    dm = get_dm(dm_id)
    if dm['active'] == False:
        raise InputError
    if get_user(auth_u_id) not in dm['members']:
        raise AccessError
    if auth_u_id != dm['creator']:
        raise AccessError

    dm.update({'active': False})
    save_data()
    return{}

def dm_messages_v1(auth_u_id, dm_id, start):
    '''
    This function takes an authorised user which is a part of the dm specified
    and lists returns a list of message_ids from the start value to the
    start value + 50

    Arguments:
    auth_user_id (Integer)    - User who is already part of the dm specified
    dm (Integer)    - dm which the messages are to be returned from
    start (Integer)    - The index of the starting message to be sent
    
    Exceptions:
        InputError  - Occurs when 
                        1. dm is not a valid channel
                        2. start is out of bounds of the list
        AccessError - Occurs when 
                        1. the user associated with auth_user_id is not a member of the dm specified

    Return Value:
        Returns {
            'messages' :dmMessages[start:end],
            'start': start,
            'end': end,
        }
    '''

    # Removing all of the invalid messages from the list
    dm_remove_invalid_messages(dm_id)
    save_data()
    # Update all the reacts for the current session user
    refresh_reacts(auth_u_id)

    if dm_exists(dm_id) is False:
        raise InputError
    dm = get_dm(dm_id)
    if dm['active'] == False:
        raise InputError
    if get_user(auth_u_id) not in dm['members']:
        raise AccessError

    dmMessageIDs = dm["messages"]
    dmMessageIDs.reverse()
    
    numOfMessages = len(dm["messages"])


    if start > numOfMessages:
        raise InputError("Start is out of bounds of list")


    formal_end = start + 50
    if formal_end >= numOfMessages:
        formal_end = -1

    end = formal_end


    dmMessages = []
    for message in range(start, start + 50):
        if end == -1 and message == numOfMessages:
            break
        msg = get_message(dmMessageIDs[message])
        if msg["removed"] and end != -1:
            end += 1
            if end >= numOfMessages:
                end = -1
            continue
        dmMessages.append(msg)
    
    return {
        'messages' :dmMessages,
        'start': start,
        'end': formal_end,
    }