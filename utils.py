import json
from pathlib import Path

# Función para cargar ejercicios desde un archivo JSON
def load_exercises_Json():
    FileJson = Path('Archivos/Ejercicios.json')
    with open(FileJson, 'r') as file:
        data = json.load(file)
    return data['ejercicios']

# Función para calcular RM
def calcular_rm(peso, repes):
    if repes == 1:
        rm = peso
    else:
        rm = peso * (1 + repes / 30)
    rm_kg = rm * 0.453592  # Convertir de libras a kilogramos
    return round(rm), round(rm_kg)
