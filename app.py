import streamlit as st
from Functions import m_tabla_conversiones, m_visualiza_peso, m_about_page, m_registro_rm,m_porcentajes

def main():
    st.sidebar.title('Opciones')

    # Definir botones y asignar estados a session_state
    if 'page' not in st.session_state:
        st.session_state.page = None

    if st.sidebar.button('Registrar Pesos'):
        st.session_state.page = 'Registrar Pesos'
    if st.sidebar.button('Visualizar Pesos'):
        st.session_state.page = 'Visualizar Pesos'
    if st.sidebar.button('Porcentajes'):
        st.session_state.page = 'Porcentajes'  # Añadir nueva opción al menú
    if st.sidebar.button('Tabla Lbs/Kg'):
        st.session_state.page = 'Tabla Lbs/Kg'    
    if st.sidebar.button('Acerca de'):
        st.session_state.page = 'Acerca de'

    # Comprobar el estado y ejecutar la función correspondiente
    if st.session_state.page == 'Registrar Pesos':
        m_registro_rm()
    elif st.session_state.page == 'Visualizar Pesos':
        m_visualiza_peso()
    elif st.session_state.page == 'Porcentajes':
        m_porcentajes()       
    elif st.session_state.page == 'Tabla Lbs/Kg':
        m_tabla_conversiones()    
    elif st.session_state.page == 'Acerca de':
        m_about_page()

if __name__ == "__main__":
    main()
