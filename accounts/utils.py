import requests
import coffee.settings as st


def register_user():
    pass

def get_auth_token(email, password):
    url = 'http://localhost:8000/o/token/'
    auth = (st.CLIENT_ID, st.CLIENT_SECRET)
    payload = {
        'grant_type': 'password',
        'username': email,
        'password': password
    }
    return requests.post(url, data=payload, auth=auth)
