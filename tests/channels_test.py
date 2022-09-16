import pytest
from src.auth import auth_register_v2
from src.channels import channels_list_v2, channels_listall_v2, channels_create_v2
from src.error import InputError, AccessError
from src.other import clear_v1
from src.helper import get_channel_listformat

@pytest.fixture
def setup ():
	""" Provides the set up code for the test functions used by initalising user ID's and creating channels with those ID's
	
	Parameters: 
		none 

	Returns:
		{user1, user2, channel1, channel2, channel3}: a dictionary of all the users and channels created

	"""
	clear_v1()
	user1 = auth_register_v2("someemail@gmail.com", "password", "john", "doe")
	user2 = auth_register_v2("someotheremail@gmail.com", "password123", "jane", "doe")
	channel1 = channels_create_v2(user1["token"], 'Channel 1', True)
	channel2 = channels_create_v2(user1["token"], 'Channel 2', False)
	channel3 = channels_create_v2(user2["token"], 'Channel 3', True)
	return {'user1' : user1["token"], 'user2' : user2["token"], 'channel1' : channel1["channel_id"], 'channel2' : channel2["channel_id"], 'channel3' : channel3["channel_id"]}


def test_channels_create():
	""" Tests that a channel can be created

	Returns:
		assertion: pass if channel is created successfully, fail if not

	"""
	clear_v1()
	token = auth_register_v2("someemail@gmail.com", "password", "john", "doe")['token']
	channel = channels_create_v2(token, 'Channel 1', True)['channel_id']
	assert get_channel_listformat(channel) in channels_list_v2(token)['channels']

def test_channels_create_exception(setup):
	""" Tests that a channel with a name over 20 characters cannot be created

	Parameters:
		setup (fixture): the setup fixture

	Returns:
		assertion: pass if input exception is thrown, fail if not

	"""
	user_token = setup['user1']
	name = 'A channel name that is too long'
	with pytest.raises(InputError):
		assert channels_create_v2(user_token, name, True)


def test_channels_list(setup):
	""" Tests that the channel_list_v2 function returns a list of channels only that the user is in

	Parameters:
		setup (fixture): the setup fixture

	Returns:
		assertion: pass if the channels that the user in is contained in the list, fail if any are missing

	"""
	channels = channels_list_v2(setup['user1'])["channels"]
	assert get_channel_listformat(setup["channel1"]) in channels
	assert get_channel_listformat(setup["channel2"]) in channels
	assert get_channel_listformat(setup["channel3"]) not in channels

def test_channels_list_all(setup):
	""" Tests that the channels_listall_v2 returns all channels that have been created

	Parameters:
		setup (fixture): the setup fixture

	Returns:
		assertion: pass if all channels are contained in the list, fail if any are missing

	"""
	channels = channels_listall_v2(setup['user1'])["channels"]
	assert get_channel_listformat(setup["channel1"]) in channels
	assert get_channel_listformat(setup["channel2"]) in channels
	assert get_channel_listformat(setup["channel3"]) in channels