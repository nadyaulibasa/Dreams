'''
user.py
'''

import re
import src.data as d
from src.helper import user_exists, get_user, get_channel, get_dm, token_decode, load_data, save_data, get_message
from src.error import InputError, AccessError
from src.channels import channels_listall_v2, channels_list_v2
from src.dm import dm_list_v1
import time


def user_profile_v1(token, u_id):
    '''
    < For a valid user, returns information about their user_id, email, first name, 
      last name, and handle >

    Arguments:
        <token>        (string)
        <u_id>         (integer)    - Member's user id

    Exceptions:
        InputError      - Occurs when user with u_id is not a valid user
        AccessError     - Occurs when the token given is invalid

    Return Value:
        Returns { user }, a dictionary containing u_id, email, name_first, name_last, handle_str

    '''
    d.data = load_data()
    # Check for valid u_id
    if user_exists(u_id) is False:
        raise InputError("Invalid user ID")

    user = get_user(u_id)
    save_data()
    return {
        'user': {
            'u_id': user['u_id'],
            'email': user['email'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'handle_str': user['handle_str'],
        }
    }

def user_profile_setname_v1(token, name_first, name_last):
    '''
    < Update the authorised user's first and last name >
    Arguments:
        <token>         (string)
        <name_first>    (string)    - Member's first name
        <name_last>     (string)    = Member's last name

    Exceptions:
        InputError   - Occurs when
                        = name_first is not between 1 and 50 characters inclusively in length
                        = name_last is not between 1 and 50 characters inclusively in length
        AccessError     - Occurs when the token given is invalid

    Return Value:
        Returns { }

    '''
    d.data = load_data()
    # Retrieve user id from token
    u_id = token_decode(token)

    # Check if the length of name_first and name_last is within limits
    if ((len(name_first) < 1 or len(name_first) > 50) or
        (len(name_last) < 1 or len(name_last) > 50)):
        raise InputError("Invalid name: Name length not within limits")

    # Update the user's name
    for user in d.data['users']:
        if u_id == user['u_id']:
            user['name_first'] = name_first
            user['name_last'] = name_last
    save_data()
    return {}

def user_profile_setemail_v1(token, email):
    '''
    < Update the authorised user's email address >
    Arguments:
        <token>         (string)
        <email>         (string)    - Member's e-mail

    Exceptions:
        InputError      - Occurs when
                            = Email entered is not a valid email using the method provided
                            here (unless you feel you have a better method).
                            - Email address is already being used by another user
        AccessError     - Occurs when the token given is invalid

    Return Value:
        Returns { }

    '''
    d.data = load_data()
    # Retrieve user id from token
    u_id = token_decode(token)

    # Check if the email entered is valid
    regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'
    if not re.search(regex, email):
        raise InputError("Invalid email")

    # Check if the email entered is not already being used by another user
    for user in d.data['users']:
        if email == user['email']:
            raise InputError("Invalid email: email is already being used by another user")

    # Update the authorised user's email
    for user in d.data['users']:
        if u_id == user['u_id']:
            user['email'] = email
    save_data()
    return {}

def user_profile_sethandle_v1(token, handle_str):
    '''
    < Update the authorised user's handle (i.e. display name) >
    Arguments:
        <token>         (string)
        <handle_str>    (string)    - Member's new handle

    Exceptions:
        InputError      - Occurs when
                            - handle_str is not between 3 and 20 characters inclusive
                            - handle is already used by another user
        AccessError     - Occurs when the token given is invalid

    Return Value:
        Returns { }

    '''
    d.data = load_data()
    # Retrieve user id from token
    u_id = token_decode(token)

    # Check if the new handle length is valid
    if (len(handle_str) < 3 or len(handle_str) > 20):
        raise InputError("Invalid handle: Handle length not within limits")

    # Check if the handle entered is not already being used by another user
    for user in d.data['users']:
        if handle_str == user['handle_str']:
            raise InputError("Invalid email: Handle is already being used by another user")

    # Update the authorised user's email
    for user in d.data['users']:
        if u_id == user['u_id']:
            user.update({'handle_str': handle_str})
    save_data()
    return {}

def users_all_v1(token):
    '''
    < Gets a list of all the users on dreams >
    Arguments:
        <token>         (string)

    Exceptions:
        AccessError     - Occurs when the token given is invalid

    Return Value:
        Returns {users}

    '''
    d.data = load_data()

    """ ***ADD IN ACCESS ERROR RAISE***
    # Exception raise
    if token_active(active_tokens, token) == False:
        raise AccessError
    """

    # Retrieve user id from token
    u_id = token_decode(token)

    # Creates the empty list of users that will be returned
    users = []

    for user in d.data['users']:
        if u_id != user['u_id']:
            users.append({
                "u_id": user["u_id"],
                "name_first": user["name_first"],
                "name_last": user["name_last"],
                "handle_str": user["handle_str"],
                "email": user["email"],
                })

    return {'users': users}


def user_stats_v1(token):
    '''
    Fetches the required statistics about this user's use of UNSW Dreams
    
    Arguments:
        token         (string)

    Exceptions:
        AccessError     - Occurs when the token given is invalid

    Return Value:
        Returns { user_stats }
    '''

    """ ***ADD IN ACCESS ERROR RAISE***
    # Exception raise
    if token_active(active_tokens, token) == False:
        raise AccessError
    """

    stats = {}
    time_stamp = time.time()
    u_id = token_decode(token)

    # Creating channels_joined
    channels_joined = {}
    channels_joined["num_channels_joined"] = len(channels_list_v2(token)["channels"])
    channels_joined["time_stamp"] = time_stamp
    stats["channels_joined"] = channels_joined

    # Creating dms_joined
    dms_joined = {}
    dms_joined["num_dms_joined"] = len(dm_list_v1(u_id)["dms"])
    dms_joined["time_stamp"] = time_stamp
    stats["dms_joined"] = dms_joined

    # Creating messages_sent
    messages_sent = {}
    message_counter = 0

    # Counts channel messages
    for channel in channels_list_v2(token)["channels"]:
        expanded_channel = get_channel(channel["channel_id"])
        for message_id in expanded_channel["messages"]:
            message = get_message(message_id)
            if message["u_id"] == u_id:
                
                message_counter += 1

    # Counts dm messages
    for dm in dm_list_v1(u_id)["dms"]:
        expanded_dm = get_dm(dm["dm_id"])
        for message_id in expanded_dm["messages"]:
            message = get_message(message_id)
            if message["u_id"] == u_id:
                message_counter += 1
    
    # Puts together messages_sent
    messages_sent["num_messages_sent"] = message_counter
    messages_sent["time_stamp"] = time_stamp
    stats["messages_sent"] = messages_sent

    return stats


def users_stats_v1(token):
    '''
    Fetches the required statistics about the use of UNSW Dreams
    
    Arguments:
        token         (string)

    Exceptions:
        AccessError     - Occurs when the token given is invalid

    Return Value:
        Returns { dreams_stats }
    '''

    """ ***ADD IN ACCESS ERROR RAISE***
    # Exception raise
    if token_active(active_tokens, token) == False:
        raise AccessError
    """

    stats = {}
    time_stamp = time.time()

    # Creating channels_exist
    channels_exist = {}
    channels_exist["num_channels_exist"] = len(channels_listall_v2(token)["channels"])
    channels_exist["time_stamp"] = time_stamp
    stats["channels_exist"] = channels_exist

    # Creating messages_exist
    messages_exist = {}
    message_counter = 0

    # Creating and counting dms_exist
    dms_exist = {}

    dm_count = 0
    dm_ids_covered = []
    for user in users_all_v1(token)['users']:
        for dm in dm_list_v1(user["u_id"])["dms"]:
            if dm["dm_id"] not in dm_ids_covered:
                dm_count += 1
                # Counts messages in the dm
                expanded_dm = get_dm(dm["dm_id"])
                message_counter += len(expanded_dm["messages"])
                # Adds to the covered dm list
                dm_ids_covered.append(dm["dm_id"])

    dms_exist["num_dms_exist"] = dm_count
    dms_exist["time_stamp"] = time_stamp
    stats["dms_exist"] = dms_exist

    # Counts channel messages
    for channel in channels_listall_v2(token)["channels"]:
        expanded_channel = get_channel(channel["channel_id"])
        message_counter += len(expanded_channel["messages"])
        print(len(expanded_channel["messages"]))
    
    # Puts together messages_exist
    messages_exist["num_messages_exist"] = message_counter
    messages_exist["time_stamp"] = time_stamp
    stats["messages_exist"] = messages_exist

    return stats