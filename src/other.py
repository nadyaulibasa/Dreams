from src.helper import reset_data, load_data, get_channel, get_dm, get_user, channel_exists, dm_exists
import src.data as d

def clear_v1():
    '''
    Clears all the data in the data file
    '''
    reset_data()

def search_v1(auth_user_id, query_str):
    d.data = load_data()

    user = get_user(auth_user_id)
    msgs = []

    for message in d.data['messages']:
        if message['message'] == query_str:
            if user in get_channel(message["channel_id"])['all_members'] or user in get_dm(message['dm_id'])['members']:
                msgs.append(message)
    return {
        'messages': msgs
    }

def notification_v1(auth_user_id):
    d.data = load_data()
    activities = []
    for activity in d.data['activity']:
        if activity['invitee'] == auth_user_id:
            activities.append(activity)
    activities.reverse()

    messages = []
    for message in d.data['messages']:
        if message['u_id'] != auth_user_id:
            if channel_exists(message['channel_id']) and get_user(auth_user_id) in get_channel(message['channel_id'])['all_members']:
                messages.append(message)
            if dm_exists(message['dm_id']) and get_user(auth_user_id) in get_dm(message['dm_id'])['members']:
                messages.append(message)
 
    notifications = []
    while len(notifications) < 20:
        if len(messages) > 0 and len(activities) > 0:
            if messages[0]['time_created'] < activities[0]['time']:
                message = messages[0]
                sender = get_user(message['u_id'])
                if message['channel_id'] > message['dm_id']:
                    name = get_channel(message['channel_id'])['name']
                else:
                    name = get_dm(message['dm_id'])['name']
                if len(message['message']) > 20:
                    messagestr = message['message'][:20]
                else:
                    messagestr = message['message']
                print(message)
                notifications.append({
                    'channel_id': message['channel_id'],
                    'dm_id': message['dm_id'],
                    'notification_message': f"{sender['handle_str']} tagged you in {name}: {messagestr}"
                })
                messages.remove(message)
            elif len(activities) > 0:
                activity = activities[0]
                print(activity)
                notifications.append({
                    'channel_id': activity['channel_id'],
                    'dm_id': activity['dm_id'],
                    'notification_message': f"{activity['handle_str']} added you to {activity['name']}"
                })
                activities.remove(activity)
        else:
            if len(messages) > 0:
                message = messages[0]
                sender = get_user(message['u_id'])
                if message['channel_id'] > message['dm_id']:
                    name = get_channel(message['channel_id'])['name']
                else:
                    name = get_dm(message['dm_id'])['name']
                if len(message['message']) > 20:
                    messagestr = message['message'][:20]
                else:
                    messagestr = message['message']
                print(message)
                notifications.append({
                    'channel_id': message['channel_id'],
                    'dm_id': message['dm_id'],
                    'notification_message': f"{sender['handle_str']} tagged you in {name}: {messagestr}"
                })
                messages.remove(message)
            if len(activities) > 0:
                activity = activities[0]
                print(activity)
                notifications.append({
                    'channel_id': activity['channel_id'],
                    'dm_id': activity['dm_id'],
                    'notification_message': f"{activity['handle_str']} added you to {activity['name']}"
                })
                activities.remove(activity)
        if len(messages) == 0 and len(activities) == 0:
            break
    notifications.reverse()
    return {'notifications': notifications}
