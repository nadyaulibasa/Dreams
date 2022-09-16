from src.error import AccessError, InputError
import src.data as d
from src.helper import is_member, token_decode, get_channel, get_message, remove_message, get_dm, get_user, save_data, load_data, check_is_pinned, valid_message, channel_exists, dm_exists
import time
import threading
import queue

def message_send_v1(u_id, channel_id, message):
    '''
    This function takes an authorised user which is a part of the channel specified
    and sends a new message with the text 'message'

    Arguments:
    u_id (Integer)    - User who is part of the channel specified
    channel_id (Integer)    - Channel whose details need to be accessed
    message (String)  - Text that is to be included in the message
    
    Exceptions:
        InputError  - Occurs when 
                        1. The message is over 1000 characters long
        AccessError - Occurs when 
                        1. the user associated with u_id is not a member of the channel specified

    Return Value:
        Returns {
            "message_id" : message_id
        } upon valid input
    '''
    d.data = load_data()
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")

    if not is_member(u_id, channel_id):
        raise AccessError("User is not apart of channel")

    if len(d.data["messages"]) == 0:
        message_id = 0
    else:
        message_id = d.data["messages"][-1]["message_id"] + 1

    new_message= {
        "message_id": message_id,
        "u_id": u_id,
        "message": message,
        "time_created": time.time(),
        "channel_id": channel_id,
        "removed": False,
        "reacts" : [],
        "is_pinned": False

    }
    d.data["messages"].append(new_message)
    
    for channel in d.data["channels"]:
        if channel_id == channel["channel_id"]:
            channel["messages"].append(message_id)
    save_data()
    return {
        "message_id": message_id
    }

def message_remove_v1(u_id, message_id):
    '''
    This function takes an authorised user and a message id

    Arguments:
    u_id (Integer)    - Id of the user trying to remove the message
    message_id (Integer)    - Id of a message 
    
    Exceptions:
        InputError  - Occurs when 
                        1. Message does not exist or has been deleted
        AccessError - Occurs when 
                        1. If the user is not the original sender of the message OR
                        2. If the user is not the owner of the channel the message was sent to

    Return Value:
        Returns {
        } upon valid input
    '''
    d.data = load_data()
    message = get_message(message_id)

    if message == False or message["removed"] == True:
        raise InputError("Message no longer exists")
    
    if "channel_id" in message:

        channel = get_channel(message["channel_id"])

        if u_id != message["u_id"] and u_id not in channel["owner_members"] and u_id != d.data["users"][0]:
            raise AccessError("User is not authorised to delete message")
    elif "dm_id" in message:

        dm = get_dm(message["dm_id"])

        if u_id != message["u_id"] and u_id not in dm["creator"] and u_id != d.data["users"][0]:
            raise AccessError("User is not authorised to delete message")    
    
    remove_message(message_id)
    save_data()
    return {
    }

def message_edit_v1(u_id, message_id, message):
    '''
    This function takes an authorised user, a message_id and text to 
    edit the message with. If the message is an empty string, the message
    is deleted

    Arguments:
    u_id (Integer)    - User who is trying to edit the message
    message_id (Integer)    - Id of the message to be edited
    message (String)  - Text to replace the existing text within the original message
    
    Exceptions:
        InputError  - Occurs when 
                        1. Length of the message is over 1000 characters
                        2. Message does not exist or has been deleted
        AccessError - Occurs when 
                        1. If the user is not the original sender of the message OR
                        2. If the user is not the owner of the channel the message was sent to

    Return Value:
        Returns {
        } upon valid input
    '''
    d.data = load_data()
    if len(message) > 1000:
        raise InputError("Message is too long")
    
    actual_message = get_message(message_id)

    if actual_message == False or actual_message["removed"] == True:
        raise InputError("Message no longer exists")
    
    if "channel_id" in actual_message:

        channel = get_channel(actual_message["channel_id"])

        if u_id != actual_message["u_id"] and get_user(u_id) not in channel["owner_members"] and u_id != d.data["users"][0]:
            raise AccessError("User is not authorised to edit message")

    elif "dm_id" in actual_message:

        dm = get_dm(actual_message["dm_id"])

        if u_id != actual_message["u_id"] and u_id not in dm["creator"] and u_id != d.data["users"][0]:
            raise AccessError("User is not authorised to edit message")

    if len(message) == 0:
        remove_message(message_id)

    else:
        for temp_message in d.data["messages"]:
            if message_id == temp_message["message_id"]:
                temp_message["message"] = message
    save_data()
    return {
    }

def message_share_v1(u_id, og_message_id, message, channel_id, dm_id):
    '''
    This function takes an authorised user, the message_id of the message to send, 
    potential additional message to accompany the share, channel id of the channel
    to share to, or the dm to share to. Dm is set to -1 when sharing to a channel,
    and channel is set to -1 when sharing to a dm

    Arguments:
    u_id (Integer)    - User who is sharing
    og_message_id (Integer)    - Id of the message to be shared
    message (String)  - Text to add to the original text
    channel_id (Integer)   - The id of the channel to be shared to
    dm_id (Integer)   - The id of the dm to be shared to
    
    Exceptions:
        AccessError - Occurs when 
                        1. If the user has not joined the channel or dm they are trying to share to

    Return Value:
        Returns {
            "shared_message_id": shared_message_id
        } upon valid input
    '''
    d.data = load_data()
    
    if dm_id == -1:
        if not is_member(u_id, channel_id):
            raise AccessError("User is not apart of channel")
    elif channel_id == -1:
        dm_data = get_dm(dm_id)
        if get_user(u_id) not in dm_data["members"]:
            raise AccessError("User is not apart of DM")

    og_message = get_message(og_message_id)
    og_text = og_message["message"]

    newline = '\n'

    if len(message) != 0:
        new_text = f"{og_text}{newline}{message}"
    else:
        new_text = og_message["message"]

    if og_message == False or og_message["removed"] == True:
        raise InputError("Message no longer exists")


    if dm_id == -1:
        shared_message_id = message_send_v1(u_id, channel_id, new_text)
    elif channel_id == -1:
        shared_message_id = message_senddm_v1(u_id, dm_id, new_text)
    save_data()
    return {
        "shared_message_id": shared_message_id["message_id"]
    }


def message_senddm_v1(u_id, dm_id, message):
    '''
    This function takes an authorised user, the id of the dm to send the message to,
    and the text to be sent

    Arguments:
    u_id (Integer)    - User who is sharing
    dm_id (Integer)   - The id of the dm to be sent to
    message (String)  - Text to send in the message

    Exceptions:
        InputError  - Occurs when 
                        1. Length of the message is over 1000 characters
        AccessError - Occurs when 
                        1. If the user is not apart of the Dm they are trying to send to

    Return Value:
        Returns {
            "message_id": message_id
        } upon valid input
    '''
    d.data = load_data()
    if len(message) > 1000:
        raise InputError("Message is more than 1000 characters")

    dm = get_dm(dm_id)

    if get_user(u_id) not in dm["members"]:
        raise AccessError("User is not apart of the dm")
    
    #turn this into a helper function

    if len(d.data["messages"]) == 0:
        message_id = 0
    else:
        message_id = d.data["messages"][-1]["message_id"] + 1   

    new_message= {
        "message_id": message_id,
        "u_id": u_id,
        "message": message,
        "time_created": time.time(),
        "dm_id": dm_id,
        "removed": False,
        "reacts" : [],
        "is_pinned": False
    }

    d.data["messages"].append(new_message)

    for dm in d.data["dms"]:
        if dm_id == dm["dm_id"]:
            dm["messages"].append(message_id)
    save_data()
    return {
        "message_id": message_id
    }

def message_react_v1(u_id, message_id, react_id):
    '''
    This function takes an authorised user, the id of a message and a react_id
    and marks the u_id as reacted

    Arguments:
    u_id (Integer)    - User who is reacting
    message_id (Integer)   - The id of message to react to
    react_id (String)  - The react_id of the react of the message

    Exceptions:
        InputError  - Occurs when 
                        1. Message_id is not a valid message
                        2. React_id is not a valid react
                        3. User has already reacted to the message
        AccessError - Occurs when 
                        1. If the user is not apart of the channel or dm they are trying to react

    Return Value:
        Returns {
        }
    '''
    d.data = load_data()

    # Checking if the message is valid
    if valid_message(message_id) is False:
        raise InputError("Message_id is not a valid message")
    
    if react_id != 1:
        raise InputError("Invalid react id")
    
    message = get_message(message_id)
    
    temp_reacts = message['reacts']

    for react in temp_reacts:
        if react['react_id'] == react_id and u_id in react['u_ids']:
            raise InputError("User has already reacted with react: react_id")
    
    if 'channel_id' in message:
        if is_member(u_id, message['channel_id']) is False:
            raise AccessError("User is not apart of the channel the message is in")
    elif 'dm_id' in message:
        dm = get_dm(message['dm_id'])
        if get_user(u_id) not in dm['members']:
            raise AccessError("User is not apart of the DM the message is in")
    
    # If a dictionary react exists, append user_id to the list, and update the seen value
    for react in temp_reacts:
        if react['react_id'] == react_id:
            react['u_ids'].append(u_id)
            react['is_this_user_reacted'] = True
            save_data()
            return
    
    # If we have not found a react of react_id in the message, we create a new react
    # dictionary

    new_react = {
        'react_id': react_id,
        'u_ids': [u_id],
        'is_this_user_reacted': True
    }

    message['reacts'].append(new_react)
    
    save_data()

    return {

    }


def message_unreact_v1(u_id, message_id, react_id):
    '''
    This function takes an authorised user, the id of a message and a react_id
    and removes the u_id from the users that have reacted

    Arguments:
    u_id (Integer)    - User who is unreacting
    message_id (Integer)   - The id of message to unreact
    react_id (String)  - The react_id of the react of the message

    Exceptions:
        InputError  - Occurs when 
                        1. Message_id is not a valid message
                        2. React_id is not a valid react
                        3. User has not reacted to the message
        AccessError - Occurs when 
                        1. If the user is not apart of the channel or dm they are trying to unreact

    Return Value:
        Returns {
        }
    '''
    d.data = load_data()

    # Checking if the message is valid
    if valid_message(message_id) is False:
        raise InputError("Message_id is not a valid message")
    
    if react_id != 1:
        raise InputError("Invalid react id")
    
    message = get_message(message_id)
    
    temp_reacts = message['reacts']
    
    if 'channel_id' in message:
        if is_member(u_id, message['channel_id']) is False:
            raise AccessError("User is not apart of the channel the message is in")
    elif 'dm_id' in message:
        dm = get_dm(message['dm_id'])
        if get_user(u_id) not in dm['members']:
            raise AccessError("User is not apart of the DM the message is in")

    if len(temp_reacts) == 0:
        raise InputError("User has not reacted to message with react: react_id")

    for react in temp_reacts:
        if react['react_id'] == react_id and u_id not in react['u_ids']:
            raise InputError("User has not reacted to message with react: react_id")

    for react in temp_reacts:
        if react['react_id'] == react_id:
            react['u_ids'].remove(u_id)
            react['is_this_user_reacted'] = False

    save_data()

    return


def message_pin_v1(u_id, message_id):
    '''
    This function takes an authorised user, and a message_id and marks it as pinned

    Arguments:
    u_id (Integer)    - User who is pinning
    message_id (Integer)   - The id of message to pin

    Exceptions:
        InputError  - Occurs when 
                        1. Message_id is not a valid message
                        2. Message is already pinned
        AccessError - Occurs when 
                        1. If the user is not apart of the channel or dm they are trying to react
                        2. The user is not an owner of the channel or dm or they are not the global dreams owner

    Return Value:
        Returns {
        }
    '''
    d.data = load_data()

    # Checking if the message is valid
    if valid_message(message_id) is False:
        raise InputError("Message_id is not a valid message")

    # Checking if the message is already pinned
    if check_is_pinned(message_id) is True:
        raise InputError("Message is already pinned")
    # Checking if the user is not apart of the dm
    message = get_message(message_id)
    # If the user is the global owner, then skip access error checking
    if u_id == d.data['users'][0]: 
        pass
    elif 'channel_id' in message:
        channel = get_channel(message['channel_id'])

        if get_user(u_id) not in channel["owner_members"]:
            raise AccessError("User is not owner of the channel")
        
        elif is_member(u_id, message['channel_id']) is False:
            raise AccessError("User is not apart of the channel the message is in")
    elif 'dm_id' in message:
        dm = get_dm(message['dm_id'])
        if get_user(u_id) not in dm['members']:
            raise AccessError("User is not apart of the DM the message is in")

        if u_id != dm['creator']:
            raise AccessError("User is not the creator of the dm")
    
    for message in d.data["messages"]:
        if message_id == message['message_id']:
            message["is_pinned"] = True
            break

    save_data()

    return {

    }

def message_unpin_v1(u_id, message_id):
    '''
    This function takes an authorised user, and a message_id and unpins it

    Arguments:
    u_id (Integer)    - User who is unpinning
    message_id (Integer)   - The id of message to unpin

    Exceptions:
        InputError  - Occurs when 
                        1. Message_id is not a valid message
                        2. Message is already unpinned
        AccessError - Occurs when 
                        1. If the user is not apart of the channel or dm they are trying to react
                        2. The user is not an owner of the channel or dm or they are not the global dreams owner

    Return Value:
        Returns {
        }
    '''
    d.data = load_data()

    # Checking if the message is valid
    if valid_message(message_id) is False:
        raise InputError("Message_id is not a valid message")

    # Checking if the message is already pinned
    if check_is_pinned(message_id) is False:
        raise InputError("Message is already unpinned")

    # Checking if the user is not apart of the dm
    message = get_message(message_id)
    # If the user is the global owner, then skip access error checking
    if u_id == d.data['users'][0]: 
        pass
    elif 'channel_id' in message:
        channel = get_channel(message['channel_id'])

        if get_user(u_id) not in channel["owner_members"]:
            raise AccessError("User is not owner of the channel")
            

        if is_member(u_id, message['channel_id']) is False:
            raise AccessError("User is not apart of the channel the message is in")
    elif 'dm_id' in message:
        dm = get_dm(message['dm_id'])
        if get_user(u_id) not in dm['members']:
            raise AccessError("User is not apart of the DM the message is in")
        if u_id != dm['creator']:
            raise AccessError("User is not the creator of the dm")
    
    for message in d.data["messages"]:
        if message_id == message['message_id']:
            message["is_pinned"] = False
            break
            
    save_data()

    return {

    }

def message_sendlater_v1(u_id, channel_id, message, time_sent):
    '''
    This function takes an authorised user, a channel_id, a message and a time 
    to send the message. The function then creates a thread that waits till that 
    time to execute sending the message

    Arguments:
    u_id (Integer)    - User who is sending
    channel_id (Integer) - The channel to send the message to
    message (String)   - The message to be sent
    time_sent (Integer) - The unix timestamp of when the message is to be sent

    Exceptions:
        InputError  - Occurs when 
                        1. Channel_id is not a valid channel
                        2. Message is more than 1000 characters
                        3. Time sent is in the past
        AccessError - Occurs when 
                        1. The user has not joined the channel they are trying to post to

    Return Value:
        Returns {
            'message_id': message_id
        }
    '''
    d.data = load_data()

    if channel_exists(channel_id) is False:
        raise InputError("Channel ID is not a valid channel")
    
    if len(message) > 1000:
        raise InputError("Message is over 1000 characters long")

    current_time = int(time.time())
    
    if (time_sent - current_time) < 0:
        raise InputError("Time is a time in the past")

    if is_member(u_id, channel_id) is False:
        raise AccessError("User is not apart of channel")
    
    wait = time_sent - current_time

    my_queue = queue.Queue()

    t = threading.Timer(wait, message_send_thread, [u_id, channel_id, message, my_queue])
    t.start()

    return_value = my_queue.get()

    save_data()

    return return_value

def message_sendlaterdm_v1(u_id, dm_id, message, time_sent):
    '''
    This function takes an authorised user, a channel_id, a message and a time 
    to send the message. The function then creates a thread that waits till that 
    time to execute sending the message

    Arguments:
    u_id (Integer)    - User who is sending
    dm_id (Integer) - The dm to send the message to
    message (String)   - The message to be sent
    time_sent (Integer) - The unix timestamp of when the message is to be sent

    Exceptions:
        InputError  - Occurs when 
                        1. Channel_id is not a valid channel
                        2. Message is more than 1000 characters
                        3. Time sent is in the past
        AccessError - Occurs when 
                        1. The user has not joined the dm they are trying to post to

    Return Value:
        Returns {
            'message_id': message_id
        }
    '''
    d.data = load_data()

    if dm_exists(dm_id) is False:
        raise InputError("DM is not a valid dm")

    if len(message) > 1000:
        raise InputError("Message is over 1000 characters long")

    current_time = int(time.time())
    
    if (time_sent - current_time) < 0:
        raise InputError("Time is a time in the past")

    dm = get_dm(dm_id)
    if get_user(u_id) not in dm['members']:
        raise AccessError("User is not apart of the DM the message is in")

    wait = time_sent - current_time

    my_queue = queue.Queue()

    t = threading.Timer(wait, message_senddm_thread, [u_id, dm_id, message, my_queue])
    t.start()

    return_value = my_queue.get()

    save_data()

    return return_value


def message_send_thread(u_id, channel_id, message, out_queue):
    '''
    This function is a wrapper function for message_send_v1, however, 
    it saves the return value of the function in the supplied queue, so 
    we can access it in a seperate thread

    Arguments:
    u_id (Integer)    - User who is sending
    channel_id (Integer) - The channel to send the message to
    message (String)   - The message to be sent
    out_queue (Queue)  - The queue where we will store the return of message_send

    return None
    '''
    return_value = message_send_v1(u_id, channel_id, message)
    out_queue.put(return_value)

def message_senddm_thread(u_id, dm_id, message, out_queue):
    '''
    This function is a wrapper function for message_senddm_v1, however, 
    it saves the return value of the function in the supplied queue, so 
    we can access it in a seperate thread

    Arguments:
    u_id (Integer)    - User who is sending
    dm_id (Integer) - The dm to send the message to
    message (String)   - The message to be sent
    out_queue (Queue)  - The queue where we will store the return of message_senddm

    return None
    '''
    return_value = message_senddm_v1(u_id, dm_id, message)
    out_queue.put(return_value)