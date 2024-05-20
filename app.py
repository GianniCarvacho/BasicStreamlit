import streamlit as st
import hmac
import os
import base64
from streamlit_option_menu import option_menu
from Functions import fetch_all_weights, m_visualiza_peso, m_tabla_conversiones, m_registro_rm, m_porcentajes

# Función para verificar la contraseña
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

def main():
    if not check_password():
        st.stop()
    
    user = st.session_state["current_user"]
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

    st.sidebar.title(f'Opciones - {user}')

    with st.sidebar:
        selected = option_menu(
            "Main Menu", ["Registrar Pesos", "Visualizar Pesos", "Porcentajes", "Tabla Lbs/Kg", "Cerrar Sesión"],
            icons=["pencil", "eye", "percent", "table", "door-closed"],
            menu_icon="cast", default_index=0,
        )

    if selected == "Registrar Pesos":
        st.session_state.page = 'Registrar Pesos'
    elif selected == "Visualizar Pesos":
        st.session_state.page = 'Visualizar Pesos'
    elif selected == "Porcentajes":
        st.session_state.page = 'Porcentajes'
    elif selected == "Tabla Lbs/Kg":
        st.session_state.page = 'Tabla Lbs/Kg'
    elif selected == "Cerrar Sesión":
        for key in list(st.session_state.keys()):
            if key not in ['passwords']:  # Mantener las contraseñas y otros datos esenciales
                del st.session_state[key]
        st.rerun()

    if 'page' in st.session_state:
        if st.session_state.page == 'Registrar Pesos':
            m_registro_rm(user)
        elif st.session_state.page == 'Visualizar Pesos':
            m_visualiza_peso(user)
        elif st.session_state.page == 'Porcentajes':
            m_porcentajes(user)
        elif st.session_state.page == 'Tabla Lbs/Kg':
            m_tabla_conversiones(user)

if __name__ == "__main__":
    main()
