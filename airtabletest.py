import requests

AIRTABLE_API_KEY = 'pat6GluiYk9LiwfUq.4da5f6525e5251a292371c725f0cab6a4e25e9a322c830b0f376470971fe81d1'  # Reemplaza con tu API key de Airtable
BASE_ID = 'app5yIUTSGAhAWec2'  # Reemplaza con el ID de tu base en Airtable
TABLE_NAME = 'weights'

url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
headers = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("Conexión exitosa. Datos:", response.json())
else:
    print(f"Error {response.status_code}: {response.text}")
