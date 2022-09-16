'''
admin.py
'''

import src.data as d
from src.error import InputError, AccessError
from src.helper import token_decode, user_exists, load_data, save_data

def admin_user_remove_v1(token, u_id):
    '''
    < Given a User by their user ID, remove the user from the Dreams.
    Dreams owners can remove other **Dreams** owners (including the original first owner).
    Once users are removed from **Dreams**, the contents of the messages they sent will be
    replaced by 'Removed user'. Their profile must still be retrievable with user/profile/v2,
    with their name replaced by 'Removed user'. >

    Arguments:
        <token>     (string)
        <u_id>      (int)       Member's user id

    Exceptions:
        InputError      - Occurs when
                            - u_id does not refer to a valid user
                            - the user is currently the only owner
        AccessError     - Occurs when the authorised user is not an owner

    Return Value:
        { }

    '''
    d.data = load_data()
    # Check if the user is an owner 
    token_id = token_decode(token)
    for user in d.data['users']:
        if token_id == user['u_id']:
            if user['permission'] == 1:
                break
            elif user['permission'] == 2:
                raise AccessError(description="Error: User is not an owner")

    # Check for valid u_id
    if user_exists(u_id) is False:
        raise InputError(description="Error: Invalid user ID")
    
    # Check if the user is currently the only owner
    owner_flag = False
    for user in d.data['users']:
        if user['permission'] == 1 and user['u_id'] != u_id:
            owner_flag = True
            break
    
    if owner_flag is False:
        raise InputError(description="Error: User is currently the only owner\
                                        in dreams")

    # Removing user
    # Replace name with 'Removed user'
    for user in d.data['users']:
        if user['u_id'] == u_id:
            user['name_first'] = 'Removed user'
            user['name_last'] = 'Removed user'

    # Replace messages sent with 'Removed user' both in messages and dms
    for message in d.data['messages']:
        if message['u_id'] == u_id:
            message['message'] = 'Removed user'
    save_data()
    return {}


def admin_userpermission_change_v1(token, u_id, permission_id):
    '''
    < Given a User by their user ID, set their permissions to new permissions
        described by permission_id >

    Arguments:
        <token>         (string)
        <u_id>          (int)       Member's user id
        <permission_id> (int)       Permission id

    Exceptions:
        InputError      - Occurs when
                            - u_id does not refer to a valid user
                            - permission_id does not refer to a value permission
        AccessError     - Occurs when the authorised user is not an owner

    Return Value:
        { }

    '''
    d.data = load_data()
    # Check if the user is an owner
    token_id = token_decode(token)
    for user in d.data['users']:
        if token_id == user['u_id']:
            if user['permission'] == 1:
                break
            elif user['permission'] == 2:
                raise AccessError(description="Error: User is not an owner")

    # Check if u_id refers to a valid user
    if user_exists(u_id) is False:
        raise InputError(description="Error: Invalid user ID")
    
    # Check if permission_id is valid
    if permission_id != 1 and permission_id != 2:
        raise InputError(description="Error: permission_id does not refer to\
                                    a valid permission")

    # Change the user's permission
    for user in d.data['users']:
        if u_id == user['u_id']:
            user['permission'] = permission_id
    save_data()
    return {}
