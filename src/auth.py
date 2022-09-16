'''
Auth.py has two functions: auth_login_v2 and auth_register_v2.
These functions are what allow the user to register an account
As well as login with the account once it has been created.
'''

import re
from src.helper import user_exists, get_id_and_password, create_token, get_user, load_data, save_data
from src.error import InputError, AccessError
from src.config import port
import src.data as d
from src.other import clear_v1
import jwt
import random
import smtplib
import string



def auth_login_v2(email, password):
    '''
    Auth_login_v1 is given a registered users' email
    and password and returns their `auth_user_id` value

    Arguments:
    email (string) - The email that the user inputs when they are logging into their account
    password (string) - The password that the user inputs when they are logging into their account

    Exceptions:
    InputError - This occurs when the:
        Email entered is not a valid email
        Email entered does not belong to a user
        Password is not correct

    Return Value: The function returns the auth_user_id of the user
    '''
    d.data = load_data()
    regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'

    if not re.search(regex, email):
        raise InputError("Invalid Email")

    details = get_id_and_password(email)

    if details == None:
        raise InputError

    if password == details['password']:
        user_id = details['user_id']
        handle = get_user(user_id)['handle_str']
    else:
        raise InputError("Incorrect Password")

    token = create_token(handle)

    return {
        'token' : token,
        'auth_user_id': user_id,
    }

def auth_register_v2(email, password, name_first, name_last):
    '''
    Auth_register_v1 is given a user's first and last name, email address,
    and password and creates a new account for them and return a new `auth_user_id`.

    A handle is generated that is the concatenation of a
    lowercase-only first name and last name, being cutoff at 20 characters.

    If handle already taken, append the concatenated names with the smallest number (starting at 0)
    that forms a new handle that isn't already taken.

    Arguments:
    email (string) - The email that the user inputs when they are registering their account
    password (string) - The password that the user inputs when they are registering their account
    name_first (string) - This is the first name of the user that will be registered
    name_last (string) - This is the last name of the user that will be registered

    Exceptions:
    InputError - This occurs when the:
        Email entered is not a valid email
        Email address is already being used by another user
        Password entered is less than 6 characters long
        name_first is not between 1 and 50 characters inclusively in length
        name_last is not between 1 and 50 characters inclusively in length

    Return Value: The function returns the auth_user_id of the user
    '''
    d.data = load_data()
    regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'

    if re.search(regex, email):
        pass

    else:
        raise InputError("Invalid Email")

    for user in d.data['users']:
        if user['email'] == email:
            raise InputError("Email already taken")

    if len(password) < 6:
        raise InputError("Password too short")

    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError("Name length not within limits")

    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError("Name length not within limits")

    #name has to be all lowercase
    handle = name_first.lower() + name_last.lower()

    #not include whitespace or '@'
    handle = re.sub('[@\t]', '', handle)

    #no longer than 20 characters
    if len(handle) > 20:
        handle = handle[0:20]

    #If handle taken, start concatenating with smallest number (0...)
    #This can result in handle > 20 characters
    first_handle = handle
    handle_counter = 0
    for i in range(len(d.data['users'])):
        if d.data['users'][i]['handle_str'] == handle:
            handle = first_handle + str(handle_counter)
            handle_counter += 1

    token = create_token(handle)

    #create dict
    new_user = {}

    #searches for next available user id
    if len(d.data['users']) == 0:
        auth_user_id = 0
    else:
        auth_user_id = d.data['users'][-1]['u_id'] + 1
    
    password = jwt.encode({'password': password}, "", algorithm='HS256')

    if auth_user_id == 0:
        permission = 1
    else:
        permission = 2

    #add keys and values into dict
    new_user = {
        "email": email,
        "password" : password,
        "name_first" : name_first,
        "name_last" : name_last,
        "u_id" : auth_user_id,
        "handle_str" : handle,
        "permission": permission
    }

    #append that dictionary to the data["users"] list
    d.data['users'].append(new_user)
    save_data()
    return {
        'token' : token,
        'auth_user_id': auth_user_id,
    }

def auth_passwordreset_request_v1(email):
    '''
    Given an email address, if the user is a registered user,
    sends them an email containing a specific secret code, 
    that when entered in auth_passwordreset_reset, shows that
    the user trying to reset the password is the one who got
    sent this email.
    '''
    email_exists = False
    for user in d.data['users']:
        if email == user['email']:
            print(email)
            print(user['email'])
            email_exists = True
            name_first = user['name_first']
    
    if email_exists == False:
        raise InputError("Email does not exist")

    if email_exists is True:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo() #become identified as a connection
            smtp.starttls() #info becomes encrypted
            smtp.ehlo() #connection now encrypted

            #email and password for sending emails for password reset
            EMAIL_ADDRESS = "mysomeemail38@gmail.com"
            PASSWORD = "Pineapple1!"

            smtp.login(EMAIL_ADDRESS, PASSWORD)

            email_subject = "Forgotten passwrd?"
            name_first = f"Hello {name_first},"
            body = "In order to reset password, enter the code: "

            string1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            string2 = "1234567890"
            code = ''
            for _ in range(0, 8):
                code += random.choice(string1) + random.choice(string2)

            email_msg = f"{email_subject}\n\n{name_first}\n{body}\n\n{code}"
            smtp.sendmail(EMAIL_ADDRESS, email, email_msg)

            for user in d.data['users']:
                if email == user['email']:
                    user.update({'code': code})
    
    return {}

def auth_passwordreset_reset_v1(reset_code, new_password):
    """
    Given a reset code for a user, set that user's new
    password to the password provided
    """

    if len(new_password) < 6:
        raise InputError("Password too short")
    
    password = jwt.encode({'password': new_password}, "", algorithm = 'HS256')

    valid_reset_code = False
    for user in d.data['users']:
        if reset_code == user['code']:
            user.update({'password': password})
            valid_reset_code = True
            user.update({'code': None}) #code returned to None as it is a one-time code

    if valid_reset_code is False:
        raise InputError("Not a valid reset code")
    
    return {}

