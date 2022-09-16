import src.data as d
from src.error import InputError, AccessError
from src.helper import get_user, is_member, user_exists, channel_exists, get_channel, valid_message, remove_invalid_messages, save_data, load_data, get_message, refresh_reacts


def channel_invite_v1(auth_user_id, channel_id, u_id):
    '''
    This function takes an authorised user which is a part of the channel specified
    invites another user to become a member of the channel. The user is automatically
    added to the channel and becomes a member of the channel under the "all_members" list

    Arguments:
    auth_user_id (Integer)    - User who is already part of the channel specified
    channel_id (Integer)    - Channel which a new user is to be added
    u_id (Integer)    - User who is going to be added to the Channel
    
    Exceptions:
        InputError  - Occurs when 
                        1. channel_id is not a valid channel
                        2. the invited user (u_id) is not valid
                        3. the invited user (u_id) is already a member of the channel
        AccessError - Occurs when 
                        1. the user associated with auth_user_id is not a member of the channel specified

    Return Value:
        Returns {}
    '''
    d.data = load_data()
    if not channel_exists(channel_id):
        raise InputError("Channel Specified does not exist")
    if not user_exists(u_id):
        raise InputError("User to be Invited does not exist")
    if is_member(u_id, channel_id):
        raise InputError("User to be Invited is already a member")
    if not is_member(auth_user_id, channel_id) and auth_user_id != 0:
        #Also covers if the authorised user given is invalid
        raise AccessError("Auth User is not a member of Channel")

    #Adding the u_id to the channel
    channel = get_channel(channel_id)
    channel["all_members"].append(get_user(u_id))
    save_data()
    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    '''
    This function takes an authorised user which is a part of the channel specified
    and prints out the details of the channel, including the name, the owner members
    all normal members

    Arguments:
    auth_user_id (Integer)    - User who is part of the channel specified
    channel_id (Integer)    - Channel whose details need to be accessed
    
    Exceptions:
        InputError  - Occurs when 
                        1. channel_id is not a valid channel
        AccessError - Occurs when 
                        1. the user associated with auth_user_id is not a member of the channel specified

    Return Value:
        Returns {
            "name": channel_name,
            "owner_members": [list of owner members],
            "all_members": [list of all members]
        } upon valid input
    '''
    if not channel_exists(channel_id):
        raise InputError("Channel Specified does not exist")
    if not is_member(auth_user_id, channel_id) and auth_user_id != 0:
        raise AccessError("Auth User is not a member of Channel")
    
    #Getting the channel which is associated with the channel_id
    channel = get_channel(channel_id)

    return {
        'name': channel["name"],
        'owner_members': channel["owner_members"],
        'all_members': channel["all_members"],
    }

# Given a channel_id, that auth_user_id is apart of, returns 50 of the most 
# recent messages starting with message index 'start'. If start + 50 is 
# out of bounds for the message list, it will return from start to index -1.
# Function returns the sliced message list, as well as the start and end
# indexes.
def channel_messages_v1(auth_user_id, channel_id, start):
    '''
    This function takes an authorised user which is a part of the channel specified
    and lists returns a list of message dictionaries from the start value to the
    start value + 50

    Arguments:
    auth_user_id (Integer)    - User who is already part of the channel specified
    channel_id (Integer)    - Channel which a new user is to be added
    start (Integer)    - The index of the starting message to be sent
    
    Exceptions:
        InputError  - Occurs when 
                        1. channel_id is not a valid channel
                        2. start is out of bounds of the list
        AccessError - Occurs when 
                        1. the user associated with auth_user_id is not a member of the channel specified

    Return Value:
        Returns {
            'messages' :channelMessages[start:end],
            'start': start,
            'end': end,
        }
    '''
    # Check if the channel exists, if not InputError
    if channel_exists(channel_id) is False:
        raise InputError("Channel does not exist")

    # Removing all of the invalid messages from the list
    remove_invalid_messages(channel_id)
    save_data()
    # Update all the reacts for the current session user
    refresh_reacts(auth_user_id)

    channel = get_channel(channel_id)

    # Reversing the list so the start of the list is the latest message
    channelMessagesId = channel["messages"]
    channelMessagesId.reverse()
    
    # Checking how many messages are in the messages list
    numOfMessages = len(channel["messages"])

    # Checking that start is within the bound of messages
    if start > numOfMessages:
        raise InputError("Start is out of bounds of list")

    # Assuming that all members in channel can invite
    # Checking if the auth_user_id is apart of channel
    if not is_member(auth_user_id,channel_id) and auth_user_id != 0:
        raise AccessError("Auth user is not apart of channel")

    # Creating the end index
    end = start + 50

    # Checking that end is not out of bounds
    # if out of bounds assign end = -1
    if end >= numOfMessages:
        end = -1


    channelMessages = []
    for message in range(start, start + 50):
        if end == -1 and message == numOfMessages:
            break
        msg = get_message(channelMessagesId[message])
        if msg["removed"] and end != -1:
            end += 1
            if end >= numOfMessages:
                end = -1
            continue
        channelMessages.append(msg)
    # Returning the channel messages 
    # and the start and end index
    return {
        'messages': channelMessages,
        'start': start,
        'end': end,
    }

#Not required for Iteration 1
def channel_leave_v1(auth_user_id, channel_id):
    '''
    This function takes an authorised user which is a member of a channel, 
    and removes them as a member

    Arguments:
    auth_user_id (Integer)    - User who is a member of the channel specified
    channel_id (Integer)    - Channel whose details need to be accessed
    
    Exceptions:
        InputError  - Occurs when 
                        1. channel_id is not a valid channel
        AccessError - Occurs when 
                        1. When then auth_user is not a member of the channel
    Return Value:
        Returns {}
    '''
    d.data = load_data()
    if channel_exists(channel_id) == False:
        raise InputError
    ch = get_channel(channel_id)
    user = get_user(auth_user_id)
    if user in ch["owner_members"] and len(ch["owner_members"] == 1):
        raise InputError
    if user not in ch["all_members"]:
        raise AccessError

    if user in ch["owner_members"]:
        ch["owner_members"].remove(user)
    ch["all_members"].remove(user)
    save_data()
    return {
    }

# Given a channel_id, the auth_user_id is added to the channel if they are 
# authorised to do so. If the channel is private or does not exist, an error
# will occur. 
# Function has no return value
def channel_join_v1(auth_user_id, channel_id):
    '''
    This function takes an authorised user which is not a part of the channel specified
    and adds the user into the channel if the channel is public

    Arguments:
    auth_user_id (Integer)    - User who is part of the channel specified
    channel_id (Integer)    - Channel whose details need to be accessed
    
    Exceptions:
        InputError  - Occurs when 
                        1. channel_id is not a valid channel
                        2. the uses is already a member of the specified channel
        AccessError - Occurs when 
                        1. The channel is private
    Return Value:
        Returns {}
    '''
    d.data = load_data()
    # Check if the channel exists, if not InputError
    if channel_exists(channel_id) is False:
        raise InputError("Channel does not exist")

    #if the user is already a member
    if is_member(auth_user_id, channel_id):
        raise InputError("User is already a member of the channel")

    #if the user does not exist
    if not user_exists(auth_user_id):
        raise InputError("User does not exist")

    channel = get_channel(channel_id)

    #if the user is the global_owner add to both the normal members and the owner members
    if auth_user_id == d.data["users"][0]["u_id"]:
        channel["all_members"].append(get_user(auth_user_id))
        return {
        }

    # Checking that the channel is public, if not 
    # AccessError
    if channel["is_public"] is False:
        raise AccessError("Channel is private")

    # Adding the user as a member
    channel["all_members"].append(get_user(auth_user_id))
    save_data()
    return {
    }

#Not required for Iteration 1
def channel_addowner_v1(auth_user_id, channel_id, u_id):
    '''
    This function takes an authorised user which is the owner of a channel, 
    and adds another u_id as the owner of the channel

    Arguments:
    auth_user_id (Integer)    - User who is owner of the channel specified
    channel_id (Integer)    - Channel whose details need to be accessed
    u_id (Integer)          - User who is to be added as owner
    
    Exceptions:
        InputError  - Occurs when 
                        1. channel_id is not a valid channel
                        2. the uses is already an owner of the specified channel
        AccessError - Occurs when 
                        1. When then auth_user is not owner of the channel
                        or owner of dreams
    Return Value:
        Returns {}
    '''
    d.data = load_data()
    if channel_exists(channel_id) == False:
        raise InputError
    ch = get_channel(channel_id)
    if get_user(u_id) in ch["owner_members"]:
        raise InputError
    if get_user(auth_user_id) not in ch["owner_members"]:
        raise AccessError
    if auth_user_id != 0:
        raise AccessError

    ch["owner_members"].append(get_user(u_id))
    save_data()
    return {
    }

#Not required for Iteration 1
def channel_removeowner_v1(auth_user_id, channel_id, u_id):
    '''
    This function takes an authorised user which is the owner of a channel, 
    and removes another u_id as owner of the channel

    Arguments:
    auth_user_id (Integer)    - User who is owner of the channel specified
    channel_id (Integer)    - Channel whose details need to be accessed
    u_id (Integer)          - User who is to be removed as owner
    
    Exceptions:
        InputError  - Occurs when 
                        1. channel_id is not a valid channel
                        2. the auth_user is not an owner of the specified channel
                        3. the u_id is the only owner
        AccessError - Occurs when 
                        1. When then auth_user is not owner of the channel
                        or owner of dreams
    Return Value:
        Returns {}
    '''
    d.data = load_data()
    if channel_exists(channel_id) == False:
        raise InputError
    ch = get_channel(channel_id)
    if get_user(u_id) not in ch["owner_members"]:
        raise InputError
    if len(ch["owner_members"]) == 1:
        raise InputError
    if auth_user_id != 0:
        raise AccessError
    if get_user(auth_user_id) not in ch["owner_members"]:
        raise AccessError

    ch["owner_members"].remove(get_user(u_id))
    save_data()
    return {
    }
