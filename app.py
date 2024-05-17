import streamlit as st
from Functions import register_weights, TablaFull2, display_charts, about_page

def main():
    st.sidebar.title('Opciones')

    # Definir botones y asignar estados a session_state
    if 'page' not in st.session_state:
        st.session_state.page = None

    if st.sidebar.button('Registrar Pesos'):
        st.session_state.page = 'Registrar Pesos'
    if st.sidebar.button('Visualizar Pesos'):
        st.session_state.page = 'Visualizar Pesos'
    if st.sidebar.button('Tabla Lbs/Kg'):
        st.session_state.page = 'Tabla Lbs/Kg'    
    if st.sidebar.button('Acerca de'):
        st.session_state.page = 'Acerca de'

    # Comprobar el estado y ejecutar la función correspondiente
    if st.session_state.page == 'Registrar Pesos':
        register_weights()
    elif st.session_state.page == 'Visualizar Pesos':
        display_charts()
    elif st.session_state.page == 'Tabla Lbs/Kg':
        TablaFull2()    
    elif st.session_state.page == 'Acerca de':
        about_page()

if __name__ == "__main__":
    main()
