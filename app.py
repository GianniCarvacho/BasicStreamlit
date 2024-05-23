import streamlit as st
import hmac
import os
from Functions import fetch_all_weights, m_visualiza_peso, m_tabla_conversiones, m_about_page, m_registro_rm, m_porcentajes, m_home_page, update_profile
from utils import check_password
import base64



def main():
    if not check_password():
        st.stop()
    
    user = st.session_state["current_user"]
    profile_pic_path = os.path.join("profile_pics", f"{user}.png")
    
    if os.path.exists(profile_pic_path):
        # Codificar la imagen en base64
        with open(profile_pic_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode()

        # HTML para mostrar la imagen
        image_html = f"""
        <div style="display: flex; justify-content: left; margin-top: -50px;">
            <img src="data:image/png;base64,{encoded_image}" width="70">
        </div>
        """
        st.sidebar.markdown(image_html, unsafe_allow_html=True)

    st.sidebar.title(user)

    if st.sidebar.button('Actualizar Perfil'):
        st.session_state.page = 'Actualizar Perfil'  
    st.sidebar.markdown('---')

    if 'page' not in st.session_state:
        st.session_state.page = 'Inicio'

    if st.sidebar.button('Inicio'):
        st.session_state.page = 'Inicio'
    if st.sidebar.button('Registrar Pesos'):
        st.session_state.page = 'Registrar Pesos'
    if st.sidebar.button('Ver Registros'):
        st.session_state.page = 'Ver Registros'
    if st.sidebar.button('Porcentajes'):
        st.session_state.page = 'Porcentajes'
    if st.sidebar.button('Tabla Lbs/Kg'):
        st.session_state.page = 'Tabla Lbs/Kg'
    if st.sidebar.button('Cerrar Sesión'):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

    if st.session_state.page == 'Inicio':
        m_home_page(user)
    if st.session_state.page == 'Registrar Pesos':
        m_registro_rm(user)
    elif st.session_state.page == 'Ver Registros':
        m_visualiza_peso(user)
    elif st.session_state.page == 'Porcentajes':
        m_porcentajes(user)
    elif st.session_state.page == 'Tabla Lbs/Kg':
        m_tabla_conversiones()
    elif st.session_state.page == 'Actualizar Perfil':
        update_profile(user)

if __name__ == "__main__":
    main()
