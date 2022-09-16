'''
standup.py

standup_start_v1
standup_active_v1
standup_send_v1
'''
import threading
import src.data as d
from src.helper import  token_decode, \
                        get_user, user_exists, \
                        get_channel, channel_exists, is_member
from src.error import AccessError, InputError
from src.message import message_send_v1
from datetime import datetime
import time

SU_TIME     = {}
SU_MESSAGES = {} 
SU_ACTIVE   = {}

def standup_start_v1(token, channel_id, length):
    '''
    < For a given channel, start the standup period whereby for the next "length" 
    seconds if someone calls "standup_send" with a message, it is buffered 
    during the X second window then at the end of the X second window a message 
    will be added to the message queue in the channel from the user who started 
    the standup. X is an integer that denotes the number of seconds that the 
    standup occurs for. >

    Arguments:
        <token>         (string)
        <channel_id>    (integer)
        <length>        (integer)

    Exceptions:
        AccessError - Occurs when the token is invalid
        InputError  - Occurs when
                        1. Channel ID is not a valid channel
                        2. An active standup is currently running in this channel

    Return Value:
        { time_finish }
    '''

    '''# Check if token is valid
    if is_valid_token is False:
        raise AccessError(description="Error: Invalid token")'''

    # Check if channel_id is valid
    if channel_exists(channel_id) is False:
        raise InputError(description="Error: Channel does not exist")

    # Check if a standup is currently running in this channel
    is_active = standup_active_v1(token, channel_id)['is_active']
    if is_active is True:
        raise InputError(description='''Error: An active standup is
                            currently running in this channel''')
    
    # Check if length is valid
    if (length < 1):
        raise InputError(description="Error: Standup must be at least 1 second")
    
    '''now = datetime.now()
    time_start = int(now.replace().timestamp())
    time_finish = time_start + length'''
    time_finish = int(time.time()) + length

    global SU_TIME, SU_ACTIVE, SU_MESSAGES
    SU_TIME[channel_id] = time_finish
    SU_ACTIVE[channel_id] = True
    SU_MESSAGES[channel_id] = []

    timer = threading.Timer(length, standup_message, kwargs={'token': token, 'channel_id': channel_id})
    timer.start()

    return {
        'time_finish': time_finish
    }

def standup_active_v1(token, channel_id):
    '''
    < For a given channel, return whether a standup is active in it, and what 
    time the standup finishes. If no standup is active, then time_finish 
    returns None. >

    Arguments:
        <token>         (string)
        <channel_id>    (integer)

    Exceptions:
        AccessError - Occurs when the token is invalid
        InputError  - Occurs when Channel ID is not a valid channel

    Return Value:
        { is_active, time_finish }
        <is_active>     returns True if standup is active, 
                        returns False if inactive
        <time_finish>   returns the time the standup finishes if active,
                        returns None if inactive
    '''
    '''# Check if token is valid
    if is_valid_token is False:
        raise AccessError(description="Error: Invalid token")'''

    # Check if channel_id is valid
    if channel_exists(channel_id) is False:
        raise InputError(description="Error: Channel does not exist")

    # Check if there is an active standup
    global SU_ACTIVE, SU_TIME
    is_active = SU_ACTIVE.get(channel_id, False)
    time_finish = SU_TIME.get(channel_id, None)

    return {
        'is_active': is_active,
        'time_finish': time_finish
    }

def standup_send_v1(token, channel_id, message):
    '''
    < Sending a message to get buffered in the standup queue, assuming a standup 
    is currently active. >

    Arguments:
        <token>         (string)
        <channel_id>    (integer)
        <message>       (string)

    Exceptions:
        AccessError  - Occurs when 
                        1. The token is invalid
                        2. The authorised user is not a member of the channel 
                            that the message is within
        InputError  - Occurs when
                        1. Channel ID is not a valid channel
                        2. Message is more than 1000 characters (not including 
                            the username and colon)
                        3. An active standup is not currently running in 
                            this channel

    Return Value:
        {}
    '''
    '''# Check if token is valid
    if is_valid_token is False:
        raise AccessError(description="Error: Invalid token")'''
    # Check if channel_id is valid
    if channel_exists(channel_id) is False:
        raise InputError(description="Error: Channel does not exist")

    # Check if the authorised user is a member of the channel
    u_id = token_decode(token)
    if user_exists(u_id) is False or is_member(u_id, channel_id) is False:
        raise AccessError(description="Error: User is not a member of the channel")

    # Check if message length is valid
    if len(message) >= 1000:
        raise InputError(description="Error: Message is too long! Message should \
            be shorter than 1000 characters")

    # Check if a standup is currently running in this channel
    is_active = standup_active_v1(token, channel_id)['is_active']
    if is_active is False:
        raise InputError(description="Error: An active standup is not currently \
            running in this channel")

    # Send message
    global SU_MESSAGES
    u_handle = get_user(u_id)['handle_str']
    msg_data = f"{u_handle}: {message}"
    for c_id in SU_MESSAGES:
        if channel_id == c_id: 
            SU_MESSAGES[channel_id].append(msg_data)

################################# HELPER FUNCTIONS ###################################

def standup_message(token, channel_id):
    '''
    < To send the buffered message from standup as a single message, and update
        standup to inactive >
    '''

    global SU_ACTIVE, SU_TIME, SU_MESSAGES
    
    # Concatinate the message into a one single string 
    str_send = ""
    for string in SU_MESSAGES[channel_id]:
        str_send += string 
        str_send += '\n'

    SU_MESSAGES[channel_id] = []
    SU_ACTIVE[channel_id] = False
    SU_TIME[channel_id] = None

    u_id = token_decode(token)
    message_send_v1(u_id, channel_id, str(str_send))
