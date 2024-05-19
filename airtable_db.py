import pandas as pd
from pyairtable import Table
from pyairtable.api import Api
import pytz

AIRTABLE_API_KEY = 'pat6GluiYk9LiwfUq.4da5f6525e5251a292371c725f0cab6a4e25e9a322c830b0f376470971fe81d1'  # Reemplaza con tu API key de Airtable
BASE_ID = 'app5yIUTSGAhAWec2'  # Reemplaza con el ID de tu base en Airtable
TABLE_NAME = 'weights'
USERS_TABLE_NAME = 'usuarios'

api = Api(AIRTABLE_API_KEY)
table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
users_table = Table(AIRTABLE_API_KEY, BASE_ID, USERS_TABLE_NAME)

# Definir tu zona horaria local para Chile
local_tz = pytz.timezone('America/Santiago')  # Ajusta según tu zona horaria

def insert_weight(exercise, weight):
    # Obtener la hora actual en UTC y convertir a la zona horaria local
    now_utc = pd.Timestamp.now(tz='UTC')
    now_local = now_utc.tz_convert(local_tz)
    
    # Crear el registro con la hora local en formato ISO 8601
    record = {
        "ejercicio": exercise,
        "peso_rm": weight,
        "fechahora": now_local.isoformat()

    }
    table.create(record)

def fetch_all_weights(usuario):
    records = table.all()
    data = [record['fields'] for record in records if record['fields']['usuario'] == usuario]
    df = pd.DataFrame(data)
    return df

def load_data_from_db(usuario):
    return fetch_all_weights(usuario)


def fetch_weights_by_user(username):
    records = table.all()
    weights = [{'fechahora': record['fields'].get('fechahora'), 'peso_rm': record['fields'].get('peso_rm'), 'ejercicio': record['fields'].get('ejercicio')} for record in records if record['fields'].get('username') == username]
    return pd.DataFrame(weights)
