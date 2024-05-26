import pandas as pd
from pyairtable import Table
from pyairtable.api import Api
import pytz
import streamlit as st



AIRTABLE_API_KEY = st.secrets["Keys"]["airtable_key"]  # Reemplaza con tu API key de Airtable
BASE_ID = st.secrets["Keys"]["airtable_baseid"]  # Reemplaza con el ID de tu base en Airtable

TABLE_NAME = 'weights'
USERS_TABLE_NAME = 'usuarios'
TABLE_PROFILE = 'perfil'

api = Api(AIRTABLE_API_KEY)
table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
users_table = Table(AIRTABLE_API_KEY, BASE_ID, USERS_TABLE_NAME)
profile_table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_PROFILE)

# Definir tu zona horaria local para Chile
local_tz = pytz.timezone('America/Santiago')  # Ajusta según tu zona horaria

def insert_weight(exercise, weight,user):
    # Obtener la hora actual en UTC y convertir a la zona horaria local
    now_utc = pd.Timestamp.now(tz='UTC')
    now_local = now_utc.tz_convert(local_tz)
    
    # Crear el registro con la hora local en formato ISO 8601
    record = {
        "ejercicio": exercise,
        "peso_rm": weight,
        "fechahora": now_local.isoformat(),
        "usuario": user

    }
    table.create(record)

def fetch_all_weights(usuario):
    records = table.all()
    data = [record['fields'] for record in records if record['fields']['usuario'] == usuario]
    df = pd.DataFrame(data)
    return df

def load_data_from_db(usuario):
    """
    Load data from the database for a given user.

    Parameters:
    usuario (str): The username of the user.

    Returns:
    list: A list of weights for the user.
    """
    return fetch_all_weights(usuario)

def fetch_weights_by_user(username):
    records = table.all()
    weights = [{'fechahora': record['fields'].get('fechahora'), 'peso_rm': record['fields'].get('peso_rm'), 'ejercicio': record['fields'].get('ejercicio')} for record in records if record['fields'].get('username') == username]
    return pd.DataFrame(weights)


# Inicio Perfil de usuario ------------------------

#Inserta perfil de usuario
def insert_user_profile(usuario, nombre, edad, sexo, dias_entrenamiento):
    # Obtener la hora actual en UTC y convertir a la zona horaria local
    # now_utc = pd.Timestamp.now(tz='UTC')
    # now_local = now_utc.tz_convert(local_tz)
    
    # Crear el registro con la hora local en formato ISO 8601
    record = {
        "usuario": usuario,
        "nombre": nombre,
        "edad": edad,
        "sexo": sexo,
        "total_entren": dias_entrenamiento,
    }

    profile_table.create(record)



def get_user_profile(user):
    records = profile_table.all()
    for record in records:
        if record['fields'].get('usuario') == user:
            return record  # Devuelve el primer registro que coincida
    return None  # Devuelve None si no se encontraron coincidencias

def insert_or_update_user_profile(user, nombre, edad, sexo, dias_entrenamiento, accion):
    profile = get_user_profile(user)
    if accion == 'insert':
        insert_user_profile(user, nombre, edad, sexo, dias_entrenamiento)
    elif accion == 'update':
       fields = {
            'usuario': user,
            'nombre': nombre,
            'edad': edad,
            'sexo': sexo,
            'total_entren': dias_entrenamiento,
        }
    profile_table.update(profile['id'], fields)
