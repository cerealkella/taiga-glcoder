from requests import get, post
from os import path
from local_settings import *


def authenticate():
    resp = post(SERVER_NAME + 'api/v1/auth', json=CREDS)
    print(resp.json())
    if resp.status_code != 200:
        # Failed to Authenticate!
        return None
    my_token = (format(resp.json()['auth_token']))
    with open('.api_token.txt', 'w') as f:
        f.write(my_token)
    return my_token


def get_header():
    try:
        with open('.api_token.txt', 'r') as f:
            my_token = f.readline()
        myUrl = SERVER_NAME + 'api/v1/application-tokens'
        head = {'Authorization': 'Bearer {}'.format(my_token),
                'x-disable-pagination': 'True'}
        try:
            response = get(myUrl, headers=head)
            if response.status_code != 200:
                my_token = authenticate()
        except ValueError:
            print("token expired!")
            my_token = authenticate()
    except FileNotFoundError:
        # print("No Token!")
        my_token = authenticate()
    # Ensure token is up to date
    head = {'Authorization': 'Bearer {}'.format(my_token),
            'x-disable-pagination': 'True'}
    return head
