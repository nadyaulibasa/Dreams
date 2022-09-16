'''
channels.py
'''

import src.data as d
from src.error import InputError, AccessError
from src.helper import user_exists, get_user, token_decode, load_data, save_data

def channels_list_v2(token):
    '''
    < Provide a list of all the channels that the authorised user is a member of >
    Arguments:
        <token>        (string)

    Exceptions:
        AccessError  - Occurs when the token is invalid

    Return Value:
        Returns { channels }, a list of all the channels the user is a member of

    '''

    '''# Check if token is valid
    if is_valid_token(token) is False:
        raise AccessError(description="Error: Invalid token")'''

    # Retrieve user id from token
    u_id = token_decode(token)

    # Create a new dictionary of the channel that the user is a member of
    # and add to the list of channel dictionaries
    channels_list = []

    for channel in d.data['channels']:
        user_channel = {}
        if get_user(u_id) in channel['all_members']:
            user_channel.update({"channel_id": channel["channel_id"]})
            user_channel.update({"name": channel["name"]})
            channels_list.append(user_channel)

    return {
        'channels': channels_list
    }

def channels_listall_v2(token):
    '''
    < Provide a list of all channels (and their associated details) >
    Arguments:
        <token>        (string)

    Exceptions:
        AccessError  - Occurs when the token is invalid

    Return Value:
        Returns { channels }, a list of all the channels in data

    '''
    # Create a new dictionary for every channel and add to the list of 
    # channel dictionaries
    all_channels_list = []

    for channel in d.data['channels']:
        channels = {}
        channels.update({"channel_id": channel["channel_id"]})
        channels.update({"name": channel['name']})
        all_channels_list.append(channels)

    return {
        'channels': all_channels_list
    }

def channels_create_v2(token, name, is_public):
    '''
    < Creates a new channel with that name that is either a public or private channel >
    Arguments:
        <token>        (string)
        <name>         (string)     - Name of channel 
        <is_public>    (boolean)    - True if channel is public, false if channel is private

    Exceptions:
        InputError  - Occurs when the channel name is invalid, longer than 20 characters
        AccessError - Occurs when the token is invalid

    Return Value:
        Returns { channel_id }, the channel id of the newly created channel

    '''

    # Check if channel name is valid, no more than 20 characters long
    if (len(name) > 20):
        raise InputError("Invalid channel name")

    # Retrieve user id from token
    u_id = token_decode(token)

    # Create a new channel dictionary, add details, and then store to the data file
    channel = {}

    # Channel name
    channel.update({"name": name})  

    # Channel public/private                    
                           
    channel.update({"is_public": is_public})
    
    # Channel owner id
    channel.update({"owner_members": []})
    channel['owner_members'].append(get_user(u_id))  
    
    # Channel user id
    channel.update({"all_members": []})
    channel['all_members'].append(get_user(u_id))

    # Adding part for messages
    channel.update({"messages": []})

    # Channel id
    try:                                        
        channel_id = d.data['channels'][-1]['channel_id'] + 1     # Adds onto the last channel
    except:
        channel_id = 1                                          # First channel
    channel.update({"channel_id": channel_id})          

    # Update the database
    d.data['channels'].append(channel)
    save_data()

    return {
        'channel_id': channel_id
    }
