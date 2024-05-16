import streamlit as st
import streamlit_authenticator as Stauth 
import pickle
from pathlib import Path


# usuario autenticacion
names = ["Gianni", "Fito"]
usernames = ["Ugianni", "Ufito"]

# --- Leer  PICKE -----

file_path = Path(__file__).parent / 'PW_Hashed.pkl'
with file_path.open('rb') as file:
    PW_Hashed = pickle.load(file)

authenticator = Stauth.Authenticate(names, usernames, PW_Hashed,"CookieGC","abcd")

name, authentications_status,username = authenticator.login("Login","sidebar")

if authentications_status == False:
    st.error("Usuario o contraseña incorrecta")
if authentications_status == None:
    st.error("Usuario no registrado")
if authentications_status == True:
    st.success("Usuario autenticado")


