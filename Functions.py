import streamlit as st
from airtable_db import insert_weight, fetch_all_weights, load_data_from_db
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
import pytz
# Definir tu zona horaria local para Chile
local_tz = pytz.timezone('America/Santiago')  # Ajusta según tu zona horaria

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

def display_charts():
    st.title('Visualización de Pesos')
    
    # Cargar datos desde Airtable
    df = load_data_from_db()

    # Eliminar la columna 'id' si existe
    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    # Verificar y eliminar índices duplicados
    if df.index.duplicated().any():
        st.write("Índices duplicados detectados y eliminados.")
        df = df[~df.index.duplicated(keep='first')]

    # Verificar y eliminar columnas duplicadas antes de renombrar
    if df.columns.duplicated().any():
        st.write("Columnas duplicadas detectadas antes de renombrar y eliminadas.")
        df = df.loc[:, ~df.columns.duplicated()]


    # Convertir 'fechahora' a formato datetime y ajustar a la zona horaria local
    df['fechahora'] = pd.to_datetime(df['fechahora'], errors='coerce', utc=True).dt.tz_convert(local_tz)
    df['RM (Lbs)'] = pd.to_numeric(df['peso_rm'], errors='coerce')
    df['Ejercicio'] = df['ejercicio'].astype(str)

    # Verificar si hay fechas no válidas
    if df['fechahora'].isnull().any():
        st.error("Hay fechas no válidas en los datos. Verifica los registros.")
        st.write(df[df['fechahora'].isnull()])  # Mostrar registros con fechas no válidas para depuración


    # Ordenar datos por 'fechahora' de más reciente a más antiguo
    df = df.sort_values(by='fechahora', ascending=False)

    # Cambiar los títulos de las columnas
    df.rename(columns={
        'ejercicio': 'Ejercicio',
        'peso_rm': 'RM (Lbs)',
        'fechahora': 'Fecha'
    }, inplace=True)

    # Verificar y eliminar columnas duplicadas después de renombrar
    if df.columns.duplicated().any():
        df = df.loc[:, ~df.columns.duplicated()]

    # Convertir peso de libras a kilogramos y redondear a enteros
    df['RM (Kg)'] = (df['RM (Lbs)'] * 0.453592).round().astype(int)

    # Filtrar datos por el ejercicio seleccionado
    JsonEjercicios = load_exercises_Json()
    selected_exercise = st.selectbox('Selecciona Ejercicio', JsonEjercicios)
    filtered_data = df[df['Ejercicio'] == selected_exercise]

    # Limitar a los 50 registros más recientes
    filtered_data = filtered_data.head(50)

    # Seleccionar columnas y ajustar formato de la fecha
    filtered_data = filtered_data[['Ejercicio', 'RM (Lbs)', 'RM (Kg)', 'Fecha']]
    filtered_data['Fecha'] = filtered_data['Fecha'].dt.strftime('%Y-%m-%d %H:%M')


    # Reiniciar el índice del DataFrame para evitar duplicados
    filtered_data.reset_index(drop=True, inplace=True)

    # Verificar datos filtrados
    st.write("Historial:", filtered_data)

    # Ajustar el ancho de las columnas automáticamente en la tabla
    st.write("""
        <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border: 1px solid #ddd;
        }
        </style>
    """, unsafe_allow_html=True)

    # Crear el gráfico de líneas 1
    fig = px.line(filtered_data, x='Fecha', y='RM (Lbs)', title=f'Peso registrado en el tiempo para {selected_exercise}')
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

    # Crear el gráfico de líneas 2
    fig = px.line(df, x='Fecha', y='RM (Lbs)', color='Ejercicio',
                  title='Peso por Tipo de Ejercicio a lo Largo del Tiempo')

    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

def about_page():
    st.title('Acerca de')
    

def load_exercises_Json():
    FileJson = Path('Archivos/Ejercicios.json') 
    with open(FileJson, 'r') as file:
        data = json.load(file)
    return data['ejercicios']

def TablaFull2():
    st.title('Tabla Conversiones Lbs/Kg')
    filepath = Path('Archivos/TablaPesos.xlsx')
    Tabla = pd.read_excel(filepath, engine='openpyxl')
    
    # Seleccionar las columnas deseadas, ejemplo de columnas
    columnas_deseadas = ['Libras por Lado', 'Libras Totales', 'Kilos Totales']
    Tabla_filtrada = Tabla[columnas_deseadas]

    # Resetear el índice para no mostrar la columna del índice en el DataFrame
    Tabla_filtrada = Tabla_filtrada.reset_index(drop=True)

    # Convertir el DataFrame a HTML y ocultar el índice
    html = Tabla_filtrada.to_html(index=False)
    st.markdown(html, unsafe_allow_html=True)

