import pytest
import requests
import json
from src import config
from src.helper import create_token, token_decode, load_data

def test_clear():
    '''
    Tests the clear function. Creates two users, one channel, sends a message to the channel and
    creates a dm between the users. All should be removed once the clear function has been called
    by the server.
    '''
    requests.post(f"{config.url}/auth/register/v2", json={
        "email" : "email@gmail.com",
        "password" : "password",
        "name_first" : "Alex",
        "name_last" : "Fulton"})
    requests.post(f"{config.url}/auth/register/v2", json={
        "email" : "email2@gmail.com",
        "password" : "password123",
        "name_first" : "Nadya",
        "name_last" : "Ulibasa"})
    requests.post(f"{config.url}/channels/create/v2", json={
        "token": create_token("alexfulton"),
        "name" : "Channel1",
        "is_public" : True,
    })
    requests.post(f"{config.url}/massage/send/v2", json={
        "token" : create_token("alexfulton"),
        "channel_id" : 1,
        "message" : "test message",
    })
    requests.post(f"{config.url}/dm/create/v1", json={
        "token" : create_token("alexfulton"),
        "uids" : [1],
    })

    requests.delete(f"{config.url}/clear/v1")
    data = load_data()
    assert data == {
        "users" : [],
        "channels" : [],
        "messages" : [],
        "dms" : [],
    }
    

    