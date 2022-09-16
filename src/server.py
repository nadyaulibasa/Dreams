'''
server.py
provides HTTP routes for all modules
'''
import re
import sys
import jwt
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError, AccessError
from src import config
from src.helper import token_decode, token_active, load_data, save_data, get_id_and_password, user_exists, get_user, dm_exists, get_dm, get_channel, channel_exists

# Import paths for implementation
import src.admin as ad
import src.channels as cs
import src.user as u
import src.dm as d
import src.auth as a
import src.channel as c
import src.message as m
import src.data as dt
import src.other as o
import src.standup as su

dt.data = load_data()
active_tokens = []

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

#################################################################################
# AUTH ROUTES
@APP.route("/auth/login/v2", methods=['POST'])
def auth_login_v1():
    dt.data = load_data()
    data = request.get_json()
    email = data['email']

    regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'

    if not re.search(regex, email):
        raise InputError("Invalid Email")

    details = get_id_and_password(email)
    if details == None:
        raise InputError("Email not Found")

    password = data['password']
    if password != details['password']:
        raise InputError("Incorrect Password")

    login_details = a.auth_login_v2(email, password)

    session_id = 0

    while login_details['token'] in active_tokens:
        session_id += 1
        login_details['token'] = jwt.encode({'handle': get_user(details['user_id'])['handle_str'], "session_id": session_id}, "", algorithm='HS256')

    active_tokens.append(login_details['token'])

    return dumps(
        login_details
    )

@APP.route("/auth/register/v2", methods=['POST'])
def auth_register_v1():
    dt.data = load_data()
    data = request.get_json()
    email = data['email']
    password = data['password']
    name_first = data['name_first']
    name_last = data['name_last']

    regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'

    if not re.search(regex, email):
        raise InputError("Invalid Email")

    for user in dt.data['users']:
        if user['email'] == email:
            raise InputError("Email already taken")

    if len(password) < 6:
        raise InputError("Password too short")

    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError("Name length not within limits")

    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError("Name length not within limits")    

    login_details = a.auth_register_v2(email, password, name_first, name_last)

    active_tokens.append(login_details['token'])

    return dumps(
        login_details
    )

@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout_server_v1():
    data = request.get_json()
    token = data['token']
    is_success = False
    if token_active(active_tokens, token):
        active_tokens.remove(token)
        is_success = True
    return dumps({"is_success": is_success})

@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def auth_passwordreset_request():
    data = request.get_json()
    return a.auth_passwordreset_request_v1(data['email'])

@APP.route("/auth/passwordreset/reset", methods=['POST'])
def auth_passwordreset_reset():
    data = request.get_json()
    return a.auth_passwordreset_reset_v1(data['reset_code'], data['new_password'])

#################################################################################
# ADMIN ROUTES

@APP.route('/admin/user/remove', methods=['DELETE'])
def admin_user_remove_flask():
    data = request.get_json()
    token = data['token']
    u_id = data['u_id']

    return dumps(
        ad.admin_user_remove_v1(token, u_id)
    )

@APP.route('/admin/userpermission/change', methods=['POST'])
def admin_userpermission_change_flask():
    data = request.get_json()
    token = data['token']
    u_id = data['u_id']
    permission_id = data['permission_id']

    return dumps(
        ad.admin_userpermission_change_v1(token, u_id, permission_id)
    )

################################################################################
# CHANNEL ROUTES

@APP.route('/channel/invite/v2', methods=['POST'])
def channel_invite():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    u_id = data['u_id']
    c_id = data['channel_id']

    return dumps(
        c.channel_invite_v1(auth_uid, c_id, u_id)
    )

@APP.route('/channel/details/v2', methods=['GET'])
def channel_details():
    d.data = load_data()
    token = request.args.get('token')
    auth_uid = token_decode(token)
    c_id = int(request.args.get('channel_id'))
    if channel_exists(c_id) == False:
        raise InputError
    if get_user(auth_uid) not in get_channel(c_id)['all_members']:
        raise AccessError
    return dumps(
        c.channel_details_v1(auth_uid, c_id)
    )

@APP.route('/channel/messages/v2', methods=['GET'])
def channel_messages():
    token = request.args.get('token')
    auth_uid = token_decode(token)
    c_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))

    return dumps(
        c.channel_messages_v1(auth_uid, c_id, start)
    )

@APP.route('/channel/join/v2', methods=['POST'])
def channel_join():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    c_id = data['channel_id']

    return dumps(
        c.channel_join_v1(auth_uid, c_id)
    )

@APP.route('/channel/addowner/v1', methods=['POST'])
def channel_addowner():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    c_id = data['channel_id']
    u_id = data['u_id']

    return dumps(
        c.channel_addowner_v1(auth_uid, c_id, u_id)
    )

@APP.route('/channel/removeowner/v1', methods=['POST'])
def channel_removeowner():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    c_id = data['channel_id']
    u_id = data['u_id']

    return dumps(
        c.channel_addowner_v1(auth_uid, c_id, u_id)
    )

@APP.route('/channel/leave/v1', methods=['POST'])
def channel_leave():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    c_id = data['channel_id']

    return dumps(
        c.channel_leave_v1(auth_uid, c_id)
    )

#################################################################################
# CHANNELS ROUTES

@APP.route('/channels/list/v2', methods=['GET'])
def channels_list_flask():
    token = request.args.get('token')
    if token_active(active_tokens, token) == False:
        raise AccessError
    
    return dumps(
        cs.channels_list_v2(token)
    )

@APP.route('/channels/listall/v2', methods=['GET'])
def channels_listall_flask():
    token = request.args.get('token')
    if token_active(active_tokens, token) == False:
        raise AccessError

    return dumps(
        cs.channels_listall_v2(token)
    )

@APP.route('/channels/create/v2', methods=['POST'])
def channels_create_flask(): 
    data = request.get_json()
    token = data['token']
    if token_active(active_tokens, token) == False:
        raise AccessError
    name = data['name']
    is_public = data['is_public']

    return dumps(
        cs.channels_create_v2(token, name, is_public)
    )

#################################################################################
# USER ROUTES

@APP.route('/user/profile/v2', methods=['GET'])
def user_profile_flask():
    token = request.args.get('token')
    if token_active(active_tokens, token) == False:
        raise AccessError
    u_id = int(request.args.get('u_id'))
    if user_exists(u_id) == False:
        raise InputError

    return dumps(
        u.user_profile_v1(token, u_id)
    )

@APP.route('/user/profile/setname/v2', methods=['POST'])
def user_profile_setname_flask():
    data = request.get_json()
    if token_active(active_tokens, data['token']) == False:
        raise AccessError
    token = data['token']
    name_first = data['name_first']
    if len(name_first) > 50 or len(name_first) < 1:
        raise InputError
    name_last = data['name_last']
    if len(name_last) > 50 or len(name_last) < 1:
        raise InputError

    return dumps(
        u.user_profile_setname_v1(token, name_first, name_last)
    )

@APP.route('/user/profile/setemail/v2', methods=['POST'])
def user_profile_setemail_flask():
    data = request.get_json()
    if token_active(active_tokens, data['token']) == False:
        raise AccessError
    token = data['token']
    email = data['email']
    regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'

    if not re.search(regex, email):
        raise InputError("Invalid Email")

    if get_id_and_password(email) != None:
        raise InputError("Email already in use")

    return dumps(
        u.user_profile_setemail_v1(token, email)
    )

@APP.route('/user/profile/sethandle/v1', methods=['POST'])
def user_profile_sethandle_flask():
    dt.data = load_data()
    data = request.get_json()
    token = data['token']
    if token_active(active_tokens, data['token']) == False:
        raise AccessError
    handle_str = data['handle_str']
    if len(handle_str) > 20 or len(handle_str) < 3:
        raise InputError    
    for user in dt.data['users']:
        if user['handle_str'] == handle_str:
            raise InputError

    return dumps(
        u.user_profile_sethandle_v1(token, handle_str)
    )
    
@APP.route('/users/all/v1', methods=["GET"])
def users_all_flask():
    token = request.args.get('token')
    if token_active(active_tokens, token) == False:
        raise AccessError

    return dumps(
        u.users_all_v1(token)
    )

@APP.route('/user/stats/v1', methods=['GET'])
def user_stats_flask():
    token = request.args.get('token')
    return dumps(
        u.user_stats_v1(token)
    )

@APP.route('/users/stats/v1', methods=['GET'])
def users_stats_flask():
    token = request.args.get('token')
    return dumps (
        u.users_stats_v1(token)
    )
#################################################################################
# MESSAGE ROUTES

@APP.route('/message/send/v2', methods=['POST'])
def message_send():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    c_id = data['channel_id']
    msg = data['message']

    return dumps(
        m.message_send_v1(auth_uid, c_id, msg)
    )

@APP.route('/message/edit/v2', methods=['PUT'])
def message_edit():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    m_id = data['message_id']
    msg = data['message']

    return dumps(
        m.message_edit_v1(auth_uid, m_id, msg)
    )

@APP.route('/message/remove/v1', methods=['DELETE'])
def message_remove():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    m_id = data['message_id']

    return dumps(
        m.message_remove_v1(auth_uid, m_id)
    )

@APP.route('/message/share/v1', methods=['POST'])
def message_share():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    om_id = data['og_message_id']
    msg = data['message']
    c_id = data['channel_id']
    dm_id = data['dm_id']

    return dumps(
        m.message_share_v1(auth_uid, om_id, msg, c_id, dm_id)
    )

@APP.route('/message/senddm/v1', methods=['POST'])
def message_senddm():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    msg = data['message']
    dm_id = data['dm_id']

    return dumps(
        m.message_senddm_v1(auth_uid, dm_id, msg)
    )

@APP.route('/message/sendlater/v1', methods=['POST'])
def message_sendlater():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    c_id = data['channel_id']
    msg = data['message']
    time = data['time_sent']

    return dumps(
        m.message_sendlater_v1(auth_uid, c_id, msg, time)
    )

@APP.route('/message/sendlaterdm/v1', methods=['POST'])
def message_sendlaterdm():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    dm_id = data['dm_id']
    msg = data['message']
    time = data['time_sent']

    return dumps(
        m.message_sendlaterdm_v1(auth_uid, dm_id, msg, time)
    )

@APP.route('/message/react/v1', methods=['POST'])
def message_react():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    m_id = data['message_id']
    r_id = data['react_id']

    return dumps(
        m.message_react_v1(auth_uid, m_id, r_id)
    )

@APP.route('/message/unreact/v1', methods=['POST'])
def message_unreact():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    m_id = data['message_id']
    r_id = data['react_id']

    return dumps(
        m.message_unreact_v1(auth_uid, m_id, r_id)
    )

@APP.route('/message/pin/v1', methods=['POST'])
def message_pin():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    m_id = data['message_id']

    return dumps(
        m.message_pin_v1(auth_uid, m_id)
    )

@APP.route('/message/unpin/v1', methods=['POST'])
def message_unpin():
    data = request.get_json()
    auth_uid = token_decode(data['token'])
    m_id = data['message_id']

    return dumps(
        m.message_unpin_v1(auth_uid, m_id)
    )


#################################################################################
# DM ROUTES
@APP.route('/dm/details/v1', methods=['GET'])
def dm_details():
    token = request.args.get('token')
    if token_active(active_tokens, token) == False:
        raise AccessError
    dm_id = int(request.args.get('dm_id'))
    u_id = token_decode(token)

    if dm_exists(dm_id) == False:
        raise InputError
    if get_user(u_id) not in get_dm(dm_id)['members']:
        raise AccessError

    return dumps(
        d.dm_details_v1(u_id, dm_id)
    )

@APP.route('/dm/list/v1', methods=['GET'])
def dm_list():
    token = request.args.get('token')

    if token_active(active_tokens, token) == False:
        raise AccessError

    u_id = token_decode(token)
    if user_exists(u_id) == False:
        raise InputError

    return dumps(
        d.dm_list_v1(u_id)
    )

@APP.route('/dm/create/v1', methods=['POST'])
def dm_create():
    data = request.get_json()
    uids = data['uids']
    if token_active(active_tokens, data['token']) == False:
        raise AccessError
    u_id = token_decode(data['token'])
    if user_exists(u_id) == False:
        raise InputError
    for user in uids:
        if user_exists(user) == False:
            raise InputError
    return dumps(
        d.dm_create_v1(u_id, uids)
    )

@APP.route('/dm/remove/v1', methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    dm_id = data['dm_id']
    if token_active(active_tokens, data['token']) == False:
        raise AccessError
    u_id = token_decode(data['token'])
    if dm_exists(dm_id) == False:
        raise InputError
    dm = get_dm(dm_id)
    if dm['active'] == False:
        raise InputError
    if get_user(u_id) not in dm['members']:
        raise AccessError
    if u_id != dm['creator']:
        raise AccessError
    return dumps(
        d.dm_remove_v1(u_id, dm_id)
    )

@APP.route('/dm/invite/v1', methods=['POST'])
def dm_invite():
    data = request.get_json()
    if token_active(active_tokens, data['token']) == False:
        raise AccessError
    a_u_id = token_decode(data['token'])
    u_id = data['u_id']
    dm_id = data['dm_id']
    if user_exists(a_u_id) == False or user_exists(u_id) == False:
        raise InputError
    if dm_exists(dm_id) == False:
        raise InputError
    dm = get_dm(dm_id)
    if dm['active'] == False:
        raise InputError
    if get_user(a_u_id) not in dm['members']:
        raise AccessError
    return dumps(
        d.dm_invite_v1(a_u_id, dm_id, u_id)
    )

@APP.route('/dm/leave/v1', methods=['POST'])
def dm_leave():
    data = request.get_json()
    if token_active(active_tokens, data['token']) == False:
        raise AccessError
    a_u_id = token_decode(data['token'])
    dm_id = data['dm_id']
    if dm_exists(dm_id) == False:
        raise InputError
    dm = get_dm(dm_id)
    if dm['active'] == False:
        raise InputError
    if get_user(a_u_id) not in dm['members']:
        raise AccessError
    return dumps(
        d.dm_leave_v1(a_u_id, dm_id)
    )


@APP.route('/dm/messages/v1', methods=['GET'])
def dm_messages():
    token = request.args.get('token')
    if token_active(active_tokens, token) == False:
        raise AccessError
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))
    u_id = token_decode(token)
    if dm_exists(dm_id) is False:
        raise InputError
    dm = get_dm(dm_id)
    if dm['active'] == False:
        raise InputError
    if get_user(u_id) not in dm['members']:
        raise AccessError
    if start > len(dm['messages']):
        raise InputError
    return dumps(
        d.dm_messages_v1(u_id, dm_id, start)
    )
    
#############################################################
# Notifications

@APP.route('/notifications/get/v1', methods=['GET'])
def notifications_flask():
    # a dummy notification as to stop errors on front end
    return dumps({
        "notifications": ["none"]
    })


#############################################################
# OTHER ROUTES
@APP.route('/clear/v1', methods=['DELETE'])
def clear_data():
    o.clear_v1()
    return { }


@APP.route('/search/v2', methods=['GET'])
def search_messages():
    token = request.args.get('token')
    if token_active(active_tokens, token) == False:
        raise AccessError
    u_id = token_decode(token)
    str_query = request.args.get('query_str')

    if len(str_query) > 1000:
        raise InputError

    return dumps(
        o.search_v1(u_id, str_query)
    )

#################################################################################
# STANDUP ROUTES

@APP.route('/standup/start/v1', methods=['POST'])
def standup_start():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    length = data['length']
    return dumps(
        su.standup_start_v1(token, channel_id, length)
    )

@APP.route('/standup/active/v1', methods=['GET'])
def standup_active():
    payload = request.get_json()
    token = payload['token']
    channel_id = payload['channel_id']
    return dumps(
        su.standup_active_v1(token, channel_id)
    )

@APP.route('/standup/send/v1', methods=['POST'])
def standup_send():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    message = data['message']
    return dumps(
        su.standup_send_v1(token, channel_id, message)
    )

if __name__ == "__main__":
    APP.debug = True
    APP.run(port=config.port) # Do not edit this port
