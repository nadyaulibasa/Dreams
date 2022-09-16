import src.data as d
import jwt
from src.error import AccessError, InputError
import json

def load_data():
    with open("src/data.json") as f:
        data = json.load(f)
        return data

def save_data():
    with open("src/data.json", "w") as f:
        json.dump(d.data, f)

def get_user(u_id):
    '''
    gets the user associated with a u_id and returns the whole dictionary

    Arguments:
    u_id (Integer) - User dictionary to be located and returned
    
    Return Value:
        Returns user - Dictionary containing the user's data (first name, last name, user_id, handle, email)
    '''
    for user in d.data["users"]:
        if u_id == user["u_id"]:
            return {
                "u_id": user["u_id"],
                "name_first": user["name_first"],
                "name_last": user["name_last"],
                "handle_str": user["handle_str"],
                "email": user["email"],
            }

def get_user_wPerms(u_id):
    '''
    gets the user associated with a u_id and returns the whole dictionary

    Arguments:
    u_id (Integer) - User dictionary to be located and returned
    
    Return Value:
        Returns user - Dictionary containing the user's data (first name, last name, user_id, handle, email)
    '''
    for user in d.data["users"]:
        if u_id == user["u_id"]:
            return {
                "u_id": user["u_id"],
                "name_first": user["name_first"],
                "name_last": user["name_last"],
                "handle_str": user["handle_str"],
                "email": user["email"],
                "permission": user['permission']
            }
    
def get_channel(channel_id):
    '''
    gets the channel associated with a channel_id and returns the whole dictionary

    Arguments:
    channel_id (Integer) - Channel dictionary to be located and returned
    
    Return Value:
        Returns channel - Dictionary containing the channel's data including name, 
                          channel_id, owner_members, all_members, privacy status etc
    '''
    for channel in d.data["channels"]:
        if int(channel_id) == channel["channel_id"]:
            return channel

def channel_exists(channel_id):
    '''
    Checks if a channel exists

    Arguments:
    channel_id (Integer) - channel to be located
    
    Return Value:
        Returns True - if the channel exists in the data
                False - if the channel does not exist
    '''
    d.data = load_data()
    for channel in d.data["channels"]:
        if channel_id == channel["channel_id"]:
            return True
    return False

def user_exists(u_id):
    '''
    Checks if a user exists

    Arguments:
    user_id (Integer) - user to be located
    
    Return Value:
        Returns True - if the user exists in the data
                False - if the user does not exist
    '''
    for user in d.data["users"]:
        if u_id == user["u_id"]:
            return True
    return False

def is_member(u_id, channel_id):
    '''
    Checks if a user is a member of a channel

    Arguments:
    u_id (Integer) - the user to check if they are a member of a channel
    channel_id (Integer) - the channel to check if the user is part of it

    Return Value:
        Returns True - if the user is part of the channel
                False - if user is not part of the channel
    '''
    for channel in d.data["channels"]:
        if channel_id == channel["channel_id"]:
            if get_user(u_id) in channel["all_members"]:
                return True
    return False

def reset_data():
    '''
    Resets the data in the data file
    '''

    d.data.update({"users": []})
    d.data.update({"channels": []})
    d.data.update({"messages": []})
    d.data.update({"dms": []})
    save_data()

def get_channel_listformat(channel_id):
    '''
    Gets the channel data utilised for the channels_list functions

    Arguments:
    channel_id (Integer) - the channel to get details from

    Return Value:
        Returns {
            "channel_id": channel_id,
            "name": name
        }
    '''
    for channel in d.data["channels"]:
        if int(channel_id) == channel["channel_id"]:
            return {"channel_id": channel["channel_id"], "name": channel["name"]}

def get_id_and_password(email):
    for user in d.data['users']:
        if user['email'] == email:
            pw = jwt.decode(user['password'], "", algorithms=["HS256"])

            return {'user_id': user['u_id'], 'password': pw['password']}

def create_token(handle):
    # Login, Register
    return jwt.encode({'handle': handle}, "", algorithm='HS256')


'''def is_valid_token(token):
    is_success = False
    if token in tokens:
        is_success = True
    return {
        is_success
    }'''


def token_decode(token):
    '''
    Finds a u_id from the token

    Arguments:
    token - The token that we want to get u_id from

    Return Value:
        Returns u_id
    '''
    SECRET = ""
    handle = jwt.decode(token, SECRET, algorithms=["HS256"])

    u_id = ''

    for user in d.data["users"]:
        if user["handle_str"] == handle['handle']:
            u_id = user["u_id"]

    return int(u_id)

def dm_exists(dm_id):
    '''
    Checks to see if a dm exists given its dm_id

    Arguments:
    dm_id (Integer) - the id of the dm to see if it exists
    
    Return Value: dm_exists ? True : False
    '''
    for dm in d.data['dms']:
        if dm['dm_id'] == dm_id:
            return True
    return False

def get_dm(dm_id):
    '''
    Gets the detail of a dm given its dm_id

    Arguments:
    dm_id (Integer) - the id of the dm to get the details from
    
    Return Value: {
        "dm_id": Integer,
        "name": String,
        "members": [List of users that make up the members],
        "messages": [List of message IDs],
        "creator": Integer (u_id of creator),
        "active": Boolean
    }
    '''
    for dm in d.data['dms']:
        if dm['dm_id'] == dm_id:
            return dm

def get_message(message_id):
    '''
    Gets a message from the message_id, if one cannot be found, return false

    Arguments:
    message_id (Integer) - The id of the message to find

    Return Value:
        Returns {
            message
        } OR
        Returns {
            False
        }
    '''
    for message in d.data["messages"]:
        if message_id == message["message_id"]:
            return message
    return False

def remove_message(message_id):
    '''
    Updates a message so that the removed field is True

    Arguments:
    message_id (Integer) - the message to remove

    Return Value:
        Returns {

        }
    '''
    for message in d.data["messages"]:
        if message_id == message["message_id"]:
            message["removed"] = True

def valid_message(message_id):
    '''
    Checks if a message has been deleted or not, returns true if it hasn't 
    and false if it has

    Arguments:
    message_id (Integer) - the message to check

    Return Value:
        Returns {
            True
        } OR
        Returns {
            False
        }
    '''
    for message in d.data["messages"]:
        if message_id == message["message_id"] and message["removed"] == False:
            return True
    return False

def remove_invalid_messages(channel_id):
    '''
    Removes all invalid messages from the list of messages in the channel_id

    Arguments:
    channel_id (Integer) - The channel to remove invalid messages from

    Return Value:
        Returns {

        }
    '''
    for channel in d.data["channels"]:
        if channel_id == channel["channel_id"]:
            for message in channel["messages"]:
                if not valid_message(message):
                    channel["messages"].remove(message)

def get_message_text(message_id):
    '''
    Gets the text of the message with message_id

    Arguments:
    message_id (Integer) - the message to get text from

    Return Value:
        Returns {
            message
        }
    '''
    for message in d.data["messages"]:
        if message_id == message["message_id"]:
            return message["message"]

def token_active(active_tokens, token):
    if token in active_tokens:
        return True
    return False

def gen_dms_list(auth_u_id):
    '''
    This function takes an authorised user and returns a list of dictionaries
    which the user is aprt of

    Arguments:
    auth_u_id (Integer)    - User who's dms are being returned

    Return Value:
        Returns dms : -> [{dm1}, {dm2} ...] 
    '''
    dms = []
    user = get_user(auth_u_id)
    for dm in d.data['dms']:
        if user in dm['members'] and dm['active'] == True:
            dm = {
                "dm_id": dm['dm_id'],
                "name": dm['name']
            }
            dms.append(dm)
    return dms

def dm_name_gen(handles):
    '''
    This function takes a list of handles and generates a dm name based on the handles

    Arguments:
    handles (List[str])    - a list of handles used to generate a dm_name

    Return Value:
        Returns dm_name
    '''
    handles.sort()
    dm_name = ""
    for handle in range(len(handles)):
        dm_name += handles[handle]
        if(handle != len(handles) - 1):
            dm_name += ', '
    return dm_name

def get_handles(auth_u_id, uids):
    '''
    This function takes an authorised user and a list of other user_ids
    and creates a list of handles taken from userdata

    Arguments:
    auth_u_id (Integer)    - Creator of dm
    uids (List[int])       - Members of dm

    Exceptions:
        InputError - When an invalid u_id is present inside of uids

    Return Value:
        Returns dm_name (List[str]) 
    '''
    handles = [get_user(auth_u_id)['handle_str']]

    for u_id in uids:
        if user_exists(u_id) == False:
            raise InputError("Invalid uid Found")
        user = get_user(u_id)
        handles.append(user['handle_str'])
    return handles

def add_dm_to_data(creator, members, dm_id, name):
    '''
    This function takes all the necessary information for a
    dm and adds this information to data.py

    Arguments:
    creator (Integer)    - User who's dms are being returned
    members (List(Int))  - List of members
    dm_id (Integer)      - ID of the dm
    name (String)        - The name of the dm

    Return Value: None 
    '''
    d.data = load_data()
    dm = {}
    members.append(get_user(creator))
    dm.update({'dm_id': dm_id})
    dm.update({"creator": creator})
    dm.update({"members": members})
    dm.update({"name": name})
    dm.update({"active": True})
    dm.update({"messages": []})
    d.data['dms'].append(dm)
    save_data()

def check_is_pinned(message_id):
    '''
    This function takes in a message_id and checks if it is marked as pinned

    Arguments:
    message_id (Integer)    - The message_id of the message to check

    Return Value: None
    '''
    for message in d.data['messages']:
        if message_id == message['message_id'] and message['is_pinned'] == True:
            return True
    return False

def refresh_reacts(u_id):
    '''
    This function takes in the u_id of the current session user, and checks 
    all uids in every message react, and if u_id is there, update the 
    is_this_user_reacted_value

    Arguments:
    u_id (Integer)    - The u_id of the current user

    Return Value: True if message exists and is pinned, 
                  False otherwise 
    '''
    d.data = load_data()

    for message in d.data['messages']:
        for react in message['reacts']:
            if u_id in react['u_ids']:
                react['is_this_user_reacted'] = True
            else:
                react['is_this_user_reacted'] = False

    save_data()

def dm_remove_invalid_messages(dm_id):
    '''
    Removes all invalid messages from the list of messages in the dm_id

    Arguments:
    dm_id (Integer) - The dm to remove invalid messages from

    Return Value:
        Returns {

        }
    '''
    dm = get_dm(dm_id)
    if dm is None:
        return
    for message in dm['messages']:
        if not valid_message(message):
            dm["messages"].remove(message)