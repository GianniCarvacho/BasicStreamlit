import yaml
import pandas as pd
from pyairtable import Table
import streamlit_authenticator as stauth
from airtable_db import fetch_all_users

def generate_config():
    users = fetch_all_users()
    usernames = {user['username']: {
                    'email': user['email'],
                    'name': user['name'],
                    'password': user['password']} for user in users}
    plain_passwords = [user['password'] for user in users]
    hashed_passwords = stauth.Hasher(plain_passwords).generate()

    print("Plain Passwords: ", plain_passwords)
    print("Hashed Passwords: ", hashed_passwords)
    
    # Asignar contraseñas hasheadas
    for i, user in enumerate(users):
        usernames[user['username']]['password'] = hashed_passwords[i]

    config = {
        'credentials': {
            'usernames': usernames
        },
        'cookie': {
            'expiry_days': 30,
            'key': 'random_signature_key',
            'name': 'random_cookie_name'
        },
        'preauthorized': {
            'emails': []
        }
    }

    # Guardar configuración en config.yaml
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file)

    print("Datos cargados desde Airtable:")
    print(pd.DataFrame(users))
    print("Plain Passwords: ", plain_passwords)
    print("Hashed Passwords: ", hashed_passwords)
    print("Configuración generada:")
    print(config)

# Generar el archivo config.yaml
generate_config()
