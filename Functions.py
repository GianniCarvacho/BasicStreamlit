import streamlit as st
from database import insert_weight, create_db, fetch_all_weights, load_data_from_db
from pathlib import Path
import pandas as pd
import plotly.express as px
import json


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


def register_weights():
    st.title('Registro de Pesos Levantados')
    EjerciciosJson = load_exercises_Json()
    
    exercise = st.selectbox('Elegir ejercicio', (EjerciciosJson))
    st.radio('Barra', ['45 Lbs.'])
    valorBarra = int(45) 

    discos = st.number_input('Total Discos (lbs)', min_value=0)
    weight = discos + valorBarra
    repes = st.number_input('Número de Repeticiones', min_value=1, max_value=10)

    # Calcular el RM en tiempo real
    rm, rm_kg = calcular_rm(weight, repes)

    # Mostrar el cálculo del RM
    st.markdown(f'**RM estimado:** {rm} lbs ({rm_kg} kg)')
    
    with st.form(key='weight_form'):
        submit_button = st.form_submit_button(label='Guardar')
        
        if submit_button:
            insert_weight(exercise, rm)
            st.success(f'Registrado {rm} lbs para {exercise}')

def TablaFull2():
    st.title('Tabla Completa')
    filepath =  Path('Archivos/TablaPesos.xlsx')
    Tabla = pd.read_excel(filepath, engine='openpyxl')
    
    # Seleccionar las columnas deseadas, ejemplo de columnas
    columnas_deseadas =['Libras por Lado','Libras Totales','Kilos Totales']
    Tabla_filtrada = Tabla[columnas_deseadas]

    # Resetear el índice para no mostrar la columna del índice en el DataFrame
    Tabla_filtrada = Tabla_filtrada.reset_index(drop=True)

    # Convertir el DataFrame a HTML y ocultar el índice
    html = Tabla_filtrada.to_html(index=False)
    st.markdown(html, unsafe_allow_html=True)

def display_charts():
    st.title('Visualización de Pesos')
    
    JsonEjercicios = load_exercises_Json()

    # Cargar datos desde la base de datos
    df = load_data_from_db()

    selected_exercise = st.selectbox('Selecciona Ejercicio', JsonEjercicios)

    # Filtrar datos por el ejercicio seleccionado
    filtered_data = df[df['exercise'] == selected_exercise]

     # Crear el gráfico de líneas 1
    fig = px.line(filtered_data, x='datetime', y='weight_lbs', title=f'Peso registrado en el tiempo para {selected_exercise}')
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

     # Crear el gráfico de líneas 2
    # Asegurarse de que 'datatime' es de tipo datetime si no lo es
     
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Crear el gráfico de líneas múltiples
    fig = px.line(df, x='datetime', y='weight_lbs', color='exercise',
                  title='Peso por Tipo de Ejercicio a lo Largo del Tiempo')

    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def about_page():

    st.title('Acerca de')
    st.write("Esta es una aplicación para registrar y visualizar pesos levantados en diferentes ejercicios.")

def load_exercises_Json():
    FileJson = Path('Archivos/Ejercicios.json') 
    with open(FileJson, 'r') as file:
        data = json.load(file)
    return data['ejercicios']

