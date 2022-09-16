import pytest
import requests
import json
from src import config
import jwt
from src.helper import create_token
from src.other import clear_v1
import re

clear_v1()

def test_register():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': 'Peng',
    }
    r = requests.post(f"{config.url}/auth/register/v2", json = user_data)
    data = json.loads(r.text)
    assert data['auth_user_id'] == 0


def test_register_two_users():
    clear_v1()
    user_data = {
        'email': 'someemail3@gmail.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': 'Peng',
    }
    r = requests.post(f"{config.url}/auth/register/v2", json = user_data)
    data = json.loads(r.text)
    assert data['auth_user_id'] == 0

    user_data.update({"email": "someemail24@gmail.com"})
    r = requests.post(f"{config.url}/auth/register/v2", json = user_data)
    data = json.loads(r.text)
    assert data['auth_user_id'] == 1

def test_register_email_taken():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': 'Peng',
    }
    r = requests.post(f"{config.url}/auth/register/v2", json = user_data)
    r = requests.post(f"{config.url}/auth/register/v2", json = user_data)
    data = json.loads(r.text)
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Email already taken</p>'}

def test_register_email_invalid():
    clear_v1()
    user_data = {
        'email': 'someemail@gmai@@gmail.coamsroagnsl.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': 'Peng',
    }
    r = requests.post(f"{config.url}/auth/register/v2", json = user_data)
    data = json.loads(r.text)
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Invalid Email</p>'}

def test_register_shortpass():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'pass',
        'name_first': 'David',
        'name_last': 'Peng',
    }
    r = requests.post(f"{config.url}/auth/register/v2", json = user_data)
    data = json.loads(r.text)
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Password too short</p>'}

def test_register_shortfirst():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': '',
        'name_last': 'Peng',
    }
    r = requests.post(f"{config.url}/auth/register/v2", json = user_data)
    data = json.loads(r.text)
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Name length not within limits</p>'}

def test_register_shortlast():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': '',
    }
    r = requests.post(f"{config.url}/auth/register/v2", json = user_data)
    data = json.loads(r.text)
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Name length not within limits</p>'}

def test_register_longfirst():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': 'Davidasdfasdfassrgasroignasrogniarsngoasnignoaisrnogiarsognaorisng',
        'name_last': 'Peng',
    }
    r = requests.post(f"{config.url}/auth/register/v2", json = user_data)
    data = json.loads(r.text)
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Name length not within limits</p>'}

def test_register_longlast():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': 'Pengasirbgoarsboasrbogiansriognrosaingoaisnroginasrioagniosrn',
    }
    r = requests.post(f"{config.url}/auth/register/v2", json = user_data)
    data = json.loads(r.text)
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Name length not within limits</p>'}


def test_login():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': 'Peng',
    }
    requests.post(f"{config.url}/auth/register/v2", json = user_data)
    r = requests.post(f"{config.url}/auth/login/v2", json = {"email": "someemail@gmail.com", "password": "password"})
    data = json.loads(r.text)
    assert data['auth_user_id'] == 0

def test_login_2times():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': 'Peng',
    }
    requests.post(f"{config.url}/auth/register/v2", json = user_data)
    r = requests.post(f"{config.url}/auth/login/v2", json = {"email": "someemail@gmail.com", "password": "password"})
    data = json.loads(r.text)
    assert data['auth_user_id'] == 0
    r = requests.post(f"{config.url}/auth/login/v2", json = {"email": "someemail@gmail.com", "password": "password"})
    data = json.loads(r.text)
    assert data['auth_user_id'] == 0

def test_login_invalid_email():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': 'Peng',
    }
    requests.post(f"{config.url}/auth/register/v2", json = user_data)
    r = requests.post(f"{config.url}/auth/login/v2", json = {"email": "someemail2@g@@oinasf..AEFmail.com", "password": "password"})
    data = json.loads(r.text)
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Invalid Email</p>'}

def test_login_no_email():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': 'Peng',
    }
    requests.post(f"{config.url}/auth/register/v2", json = user_data)
    r = requests.post(f"{config.url}/auth/login/v2", json = {"email": "someemail2@gmail.com", "password": "password"})
    data = json.loads(r.text)
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Email not Found</p>'}

def test_login_incorrect_pass():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': 'Peng',
    }
    requests.post(f"{config.url}/auth/register/v2", json = user_data)

    r = requests.post(f"{config.url}/auth/login/v2", json = {"email": "someemail@gmail.com", "password": "password2"})
    data = json.loads(r.text)
    assert data == {'code': 400, 'name': 'System Error', 'message': '<p>Incorrect Password</p>'}

def test_logout_valid():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': 'Peng',
    }
    requests.post(f"{config.url}/auth/register/v2", json = user_data)

    user_data = {"token": create_token("davidpeng")}
    r = requests.post(f"{config.url}/auth/logout/v1", json = user_data)

    data = json.loads(r.text)
    assert data == {'is_success': True}


def test_logout_invalid():
    clear_v1()
    user_data = {
        'email': 'someemail@gmail.com',
        'password': 'password',
        'name_first': 'David',
        'name_last': 'Peng',
    }
    requests.post(f"{config.url}/auth/register/v2", json = user_data)

    user_data = {"token": create_token("davidpengas")}
    r = requests.post(f"{config.url}/auth/logout/v1", json = user_data)

    data = json.loads(r.text)
    assert data == {'is_success': False}