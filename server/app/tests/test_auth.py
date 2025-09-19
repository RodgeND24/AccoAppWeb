import requests, json
from getpass import getpass
data = {
    "username": 'Admin',
    "password": '1234512345'
}


# user_id = 4
# result = requests.get(f'http://localhost:8000/users/id/{user_id}')
# print(result.content.decode())

# json_data = json.dumps(data)
# result = requests.post('http://localhost:8000/api/auth/login', params=data)
# print(result.content.decode())

json_data = {'username': 'Dima',
             'password': '1234512345'}
result = requests.post('http://localhost:8000/api/auth/login', headers={'Content-Type': 'application/json'}, json=json_data)
print(result.content.decode())