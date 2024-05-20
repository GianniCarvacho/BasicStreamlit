import json
import streamlit as st
import hmac
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

# utils.py

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
