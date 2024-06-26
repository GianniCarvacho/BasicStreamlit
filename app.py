import streamlit as st
import hmac
import os
import base64
from Functions import (
    fetch_all_weights, m_visualiza_peso, m_tabla_conversiones, 
    m_about_page, m_registro_rm, m_porcentajes, m_home_page, update_profile
)
from utils import check_password


def main():
    if not check_password():
        st.stop()

    user = st.session_state["current_user"]
    display_profile_pic(user)
    display_sidebar(user)
    handle_page_routing(user)


def display_profile_pic(user):
    profile_pic_path = os.path.join("profile_pics", f"{user}.png")
    if os.path.exists(profile_pic_path):
        with open(profile_pic_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode()
        image_html = f"""
        <div style="display: flex; justify-content: left; margin-top: -50px;">
            <img src="data:image/png;base64,{encoded_image}" width="70">
        </div>
        """
        st.sidebar.markdown(image_html, unsafe_allow_html=True)


def display_sidebar(user):
    st.sidebar.title(user)
    if st.sidebar.button('Actualizar Perfil'):
        st.session_state.page = 'Actualizar Perfil'
    st.sidebar.markdown('---')
    if 'page' not in st.session_state:
        st.session_state.page = 'Inicio'
    sidebar_buttons()


def sidebar_buttons():
    pages = {
        'Inicio': 'Inicio',
        'Registrar Pesos': 'Registrar Pesos',
        'Ver Registros': 'Ver Registros',
        'Porcentajes': 'Porcentajes',
        'Tabla Lbs/Kg': 'Tabla Lbs/Kg',
    }
    for button, page in pages.items():
        if st.sidebar.button(button):
            st.session_state.page = page
    if st.sidebar.button('Cerrar Sesión'):
        logout_user()
        st.rerun()


def logout_user():
    for key in st.session_state.keys():
        del st.session_state[key]


def handle_page_routing(user):
    page = st.session_state.page
    if page == 'Inicio':
        m_home_page(user)
    elif page == 'Registrar Pesos':
        m_registro_rm(user)
    elif page == 'Ver Registros':
        m_visualiza_peso(user)
    elif page == 'Porcentajes':
        m_porcentajes(user)
    elif page == 'Tabla Lbs/Kg':
        m_tabla_conversiones()
    elif page == 'Actualizar Perfil':
        update_profile(user)


if __name__ == "__main__":
    main()
