import json
from pathlib import Path

def load_exercises_Json():
    FileJson = Path('Archivos/Ejercicios.json') 
    with open(FileJson, 'r') as file:
        data = json.load(file)
    return data['ejercicios']



# Función para calcular el RM utilizando la fórmula de Epley
def calcular_rm(peso, repes):
    if repes == 1:
        rm = peso
    else:
        rm = peso * (1 + repes / 30)
    rm_kg = rm * 0.453592  # Convertir de libras a kilogramos
    rm = round(rm)
    rm_kg = round(rm_kg)
    return rm, rm_kg