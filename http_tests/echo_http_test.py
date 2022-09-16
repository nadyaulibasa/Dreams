import pytest
import requests
import json
from src import config

def test_echo():
    
    resp = requests.get(config.url + 'echo', params={'data': 'hello'})
    assert json.loads(resp.text) == {'data': 'hello'}
