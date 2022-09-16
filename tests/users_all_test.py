import pytest
from src.user import users_all_v1
from src.other import clear_v1
from src.auth import auth_register_v2
from src.helper import get_user, token_decode


@pytest.fixture
def setup():
    """ Provides the set up code for the test functions used by initalising users to list in the list all function
	
	Parameters: 
		none 

	Returns:
		{user1, user2, user3, user4} dictionary of the revent users tokens

    """
    clear_v1()
    user1 = auth_register_v2("someemail@gmail.com", "password", "john", "doe")
    user2 = auth_register_v2("someotheremail@gmail.com", "password123", "jane", "doe")
    user3 = auth_register_v2("random@gmail.com", "password!@#", "kevin", "smith")
    user4 = auth_register_v2("testmail@gmail.com", "password456", "alex", "fulton")
    return {'user1' : user1, 'user2' : user2, 'user3' : user3, 'user4' : user4}


def test_users_all(setup):
    users = users_all_v1(setup['user1']['token'])['users']
    assert get_user(setup['user2']["auth_user_id"]) in users
    assert get_user(setup['user3']["auth_user_id"]) in users
    assert get_user(setup['user4']["auth_user_id"]) in users
