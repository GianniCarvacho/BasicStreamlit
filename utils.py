import json
import streamlit as st
import hmac
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

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

def check_password():
    def login_form():
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)
    
    def password_entered():
        if st.session_state["username"] in st.secrets["passwords"] and \
           hmac.compare_digest(st.session_state["password"], st.secrets.passwords[st.session_state["username"]]):
            st.session_state["password_correct"] = True
            st.session_state["current_user"] = st.session_state["username"]
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False
    
    if st.session_state.get("password_correct", False):
        return True
    
    login_form()
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("User not known or password incorrect")
    return False

def get_table_style():
    return """
    <style>
    .dataframe {
        width: 80%;
        border-collapse: collapse;
    }
    .dataframe th, .dataframe td {
        padding: 2px;
        text-align: center;
        border: 1px solid #ddd;
    }
    .dataframe th {
        background-color: #444;  /* Color de fondo oscuro */
        color: white;  /* Color del texto blanco */
    }
    </style>
    """
def formateo_pd_visualizaPeso(df):
        
        
       # Convertir la columna de fechas a objetos datetime y ajustar la zona horaria
        df['fechahora'] = pd.to_datetime(df['fechahora'])
        df['fechahora'] = df['fechahora'].dt.tz_convert('America/Santiago') # Cambia esto a tu zona horaria deseada

        # Ordenar la tabla de forma descendente por la columna fechahora
        df = df.sort_values(by='fechahora', ascending=False)
        df_graficos = df.sort_values(by='fechahora', ascending=True)
        df_sinfiltro = df.sort_values(by='fechahora', ascending=True)

        # Convertir la fecha al formato deseado
        df['fechahora'] = df['fechahora'].dt.strftime('%d-%m-%Y %H:%M')
        df_graficos['fechahora'] = df_graficos['fechahora'].dt.strftime('%d-%m-%Y %H:%M')
        df_sinfiltro['fechahora'] = df_sinfiltro['fechahora'].dt.strftime('%d-%m-%Y %H:%M')

        # Agregar nueva columna "peso en kilos"
        df['peso en kilos'] = (df['peso_rm'] / 2.205).round().astype(int)  # Ejemplo de conversión, ajustar según sea necesario
        
        # Reordenar las columnas y eliminar la columna 'id'
        df = df[['ejercicio', 'peso_rm', 'peso en kilos', 'fechahora']]

            # Renombrar las columnas
        df = df.rename(columns={
            'ejercicio': 'Ejercicio',
            'peso_rm': 'RM Libras',
            'peso en kilos': 'RM Kilos',
            'fechahora': 'Fecha'
        })

        df_graficos = df_graficos.rename(columns={
            'ejercicio': 'Ejercicio',
            'peso_rm': 'RM Libras',
            'fechahora': 'Fecha'
        })

        df_sinfiltro = df_sinfiltro.rename(columns={
            'ejercicio': 'Ejercicio',
            'peso_rm': 'RM Libras',
            'fechahora': 'Fecha'
        })


        # df = df.head(50)  # Limitar a los 50 registros más recientes
        return df,df_graficos,df_sinfiltro



def check_password():
    session_timeout = timedelta(minutes=90)  # Ajusta el tiempo de sesión según tus necesidades
    if "login_time" in st.session_state:
        if datetime.now() - st.session_state["login_time"] > session_timeout:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        st.session_state["login_time"] = datetime.now()
        return True

    login_form()
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("User not known or password incorrect")
    return False


def login_form():
    with st.form("Credentials"):
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.form_submit_button("Log in", on_click=password_entered)


def password_entered():
    if st.session_state["username"] in st.secrets["passwords"] and \
       hmac.compare_digest(st.session_state["password"], st.secrets.passwords[st.session_state["username"]]):
        st.session_state["password_correct"] = True
        st.session_state["current_user"] = st.session_state["username"]
        st.session_state["login_time"] = datetime.now()
        del st.session_state["password"]
        del st.session_state["username"]
    else:
        st.session_state["password_correct"] = False