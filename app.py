import streamlit as st
import hmac
from Functions import m_tabla_conversiones, m_visualiza_peso, m_about_page, m_registro_rm, m_porcentajes

# Función para verificar la contraseña
def check_password():
    """Returns `True` if the user entered the correct password."""
    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets["passwords"] and \
           hmac.compare_digest(st.session_state["password"], st.secrets.passwords[st.session_state["username"]]):
            st.session_state["password_correct"] = True
            st.session_state["current_user"] = st.session_state["username"]
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False
    
    # Return True if the username and password are validated
    if st.session_state.get("password_correct", False):
        return True
    
    # Show login form
    login_form()
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("User not known or password incorrect")
    return False

# Función principal de la aplicación
def main():
    # Verificar la contraseña antes de mostrar el contenido de la aplicación
    if not check_password():
        st.stop()
    
    st.sidebar.title(f'Opciones - {st.session_state["current_user"]}')

    # Definir botones y asignar estados a session_state
    if 'page' not in st.session_state:
        st.session_state.page = None

    if st.sidebar.button('Registrar Pesos'):
        st.session_state.page = 'Registrar Pesos'
    if st.sidebar.button('Visualizar Pesos'):
        st.session_state.page = 'Visualizar Pesos'
    if st.sidebar.button('Porcentajes'):
        st.session_state.page = 'Porcentajes'
    if st.sidebar.button('Tabla Lbs/Kg'):
        st.session_state.page = 'Tabla Lbs/Kg'
    if st.sidebar.button('Acerca de'):
        st.session_state.page = 'Acerca de'
    if st.sidebar.button('Cerrar Sesión'):
        st.session_state.page = None
        st.session_state.password_correct = False

    # Comprobar el estado y ejecutar la función correspondiente
    if st.session_state.page == 'Registrar Pesos':
        m_registro_rm()
    elif st.session_state.page == 'Visualizar Pesos':
        m_visualiza_peso(st.session_state["current_user"])
    elif st.session_state.page == 'Porcentajes':
        m_porcentajes(st.session_state["current_user"])
    elif st.session_state.page == 'Tabla Lbs/Kg':
        m_tabla_conversiones()
    elif st.session_state.page == 'Acerca de':
        m_about_page()

if __name__ == "__main__":
    main()
