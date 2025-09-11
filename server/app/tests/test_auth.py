import requests, json
from getpass import getpass
data = {
    "username": 'Dima',
    "password": '1234512345'
}


# user_id = 4
# result = requests.get(f'http://localhost:8000/users/id/{user_id}')
# print(result.content.decode())
json_data = json.dumps(data)
result = requests.post('http://localhost:8000/auth/login', data=data)
print(result.content.decode())
# print(result.headers)