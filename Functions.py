import streamlit as st
from airtable_db import insert_weight, fetch_all_weights, load_data_from_db, insert_user_profile, get_user_profile,insert_or_update_user_profile
from utils import load_exercises_Json, calcular_rm, get_table_style, formateo_pd_visualizaPeso
import plotly.express as px
import pandas as pd
from pathlib import Path
import pytz
from datetime import datetime
# from utils_openai import obtener_mensaje_motivacional


# Opción Registro de RM
def m_registro_rm(user):
    st.title('Registro de RM')
    EjerciciosJson = load_exercises_Json()

    exercise = st.selectbox('Elegir ejercicio', (EjerciciosJson))
    st.radio('Barra', ['45 Lbs.'])
    valorBarra = int(45)

    discos = st.number_input('Suma Total Libras', min_value=0)
    weight = discos + valorBarra
    repes = st.number_input('Número de Repeticiones', min_value=1, max_value=10)

    # Calcular el RM en tiempo real
    rm, rm_kg = calcular_rm(weight, repes)

    # Mostrar el cálculo del RM
    st.markdown(f'**RM estimado:** {rm} lbs ({rm_kg} kg)')

    with st.form(key='weight_form'):
        submit_button = st.form_submit_button(label='Guardar')

        if submit_button:
            insert_weight(exercise, rm, user)
            st.success(f'Registrado {rm} lbs para {exercise}')

# Opción Visualizar Pesos
def m_visualiza_peso(usuario):
   
    st.header('Registro Histórico de RM', divider='gray')

    # Cargar datos desde Airtable
    df = load_data_from_db(usuario)

    # Verificar si el dataframe está vacío
    if df.empty:
        st.warning("No hay datos disponibles para mostrar.")
        return

    df_formateado,df_graficos,df_sinfiltro = formateo_pd_visualizaPeso(df)
   

    JsonEjercicios = load_exercises_Json()
    selected_exercise = st.selectbox('Selecciona Ejercicio', JsonEjercicios)

    df_ejercicio = df_formateado[df_formateado['Ejercicio'] == selected_exercise]
    df_ejercicio.head(30)
    df_graficos = df_graficos[df_graficos['Ejercicio'] == selected_exercise]
    # st.write(df_ejercicio)

    st.write(get_table_style(), unsafe_allow_html=True)
    st.markdown(df_ejercicio.to_html(index=False, classes='dataframe'), unsafe_allow_html=True)
    

      # Imprimir líneas en blanco antes del markdown
    
    st.write("\n")
    st.write('---')

    # highlighted_text = f'<p style="color:yellow; font-size:15px;">Cálculo en base a RM máximo registrado: {max_weight} lbs el {fecha_str}</p>'
    highlighted_text = f'<p style="color:yellow; font-size:15px;">Evolución RM para {selected_exercise}</p>'
    st.markdown(highlighted_text, unsafe_allow_html=True)

    # fig = px.line(df_graficos, x='Fecha', y="RM Libras")
    # st.plotly_chart(fig, theme="streamlit")



    # # #df_sinfiltro['Fecha'] = pd.to_datetime(df_sinfiltro['Fecha'])  # Asegúrate de que las fechas estén en formato datetime
    # df_sinfiltro['Fecha'] = pd.to_datetime(df_sinfiltro['Fecha'], format='%d-%m-%Y %H:%M', dayfirst=True)  # Asegúrate de que las fechas estén en formato datetime
    # st.line_chart(df_graficos, x='Fecha', y="RM Libras")


    # Grafico todos los ejercicios con una línea de tiempo común
    df_graficos['Fecha'] = pd.to_datetime(df_graficos['Fecha'], format='%d-%m-%Y %H:%M', dayfirst=True)  # Asegúrate de que las fechas estén en formato datetime
    fig = px.line(df_graficos, x='Fecha', y='RM Libras', markers=True)
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        autosize=True,
        width=800,  # Ajusta el ancho según sea necesario
        height=500,  # Ajusta la altura según sea necesario
        margin=dict(l=0, r=0, t=0, b=0),  # Ajusta los márgenes según sea necesario
        xaxis=dict(tickangle=-45)  # Rotar etiquetas del eje X
    )
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")

# Opción Porcentajes
def m_porcentajes(usuario):
    # Cargar datos desde Airtable
    df = load_data_from_db(usuario)

    st.title('Porcentajes')

    # Verificar si el dataframe está vacío
    if df.empty:
        st.warning("No hay datos disponibles para mostrar.")
        return

    # Cambiar los títulos de las columnas
    df.rename(columns={
        'ejercicio': 'Ejercicio',
        'peso_rm': 'RM (Lbs)',
        'fechahora': 'Fecha'
    }, inplace=True)

    # Filtrar datos por el ejercicio seleccionado
    JsonEjercicios = load_exercises_Json()
    selected_exercise = st.selectbox('Selecciona Ejercicio', JsonEjercicios)
    filtered_data = df[df['Ejercicio'] == selected_exercise]

    # Verificar si hay datos para el ejercicio seleccionado
    if filtered_data.empty:
        st.warning(f"No hay datos disponibles para el ejercicio '{selected_exercise}'.")
        return

    # Obtener el mayor peso registrado para el ejercicio seleccionado
    max_weight = filtered_data['RM (Lbs)'].max()
    fechahora = filtered_data.loc[filtered_data['RM (Lbs)'].idxmax(), 'Fecha']

    # Convertir la fecha a solo el formato de fecha
        # Convertir la fecha a solo el formato de fecha
    fecha_obj = datetime.strptime(fechahora, '%Y-%m-%dT%H:%M:%S.%fZ').date()
    fecha_str = fecha_obj.strftime('%d-%m-%Y')

    # Definir los porcentajes de 120% a 40% disminuyendo de 5% en 5%
    percentages = [f"{p}%" for p in range(120, 35, -5)]

    # Calcular los pesos en libras y kilogramos
    weights_lbs = [round(max_weight * (int(p[:-1]) / 100)) for p in percentages]
    weights_kg = [round(w * 0.453592) for w in weights_lbs]

    # Calcular los discos total y por lado
    discs_total_lbs = [w - 45 for w in weights_lbs]
    discs_per_side_lbs = [round(w / 2) for w in discs_total_lbs]

    # Crear un DataFrame con los porcentajes y pesos
    data = {
        'Porcentaje (%)': percentages,
        'Peso (Lbs)': weights_lbs,
        'Peso Kg': weights_kg,
        'Discos Total (lbs)': discs_total_lbs,
        'Discos por lado (Lbs)': discs_per_side_lbs
    }
    df_percentages = pd.DataFrame(data)

    # Eliminar la primera columna de índice
    df_percentages.reset_index(drop=True, inplace=True)

    # Crear el texto resaltado con valores dinámicos
    highlighted_text = f'<p style="color:yellow; font-size:15px;">Cálculo en base a RM máximo registrado: {max_weight} lbs el {fecha_str}</p>'
    
    # Mostrar el texto en Streamlit
    st.markdown(highlighted_text, unsafe_allow_html=True)

    st.write(get_table_style(), unsafe_allow_html=True)
    st.markdown(df_percentages.to_html(index=False, classes='dataframe'), unsafe_allow_html=True)

# Opción Tabla Conversiones
def m_tabla_conversiones():
    st.title('Tabla Conversiones Lbs/Kg')
    filepath = Path('Archivos/TablaPesos.xlsx')
    Tabla = pd.read_excel(filepath, engine='openpyxl')

    # Seleccionar las columnas deseadas, ejemplo de columnas
    columnas_deseadas = ['Libras por Lado', 'Libras Totales', 'Kilos Totales']
    Tabla_filtrada = Tabla[columnas_deseadas]

    # Resetear el índice para no mostrar la columna del índice en el DataFrame
    Tabla_filtrada = Tabla_filtrada.reset_index(drop=True)

    # Quitar decimales de la columna "Kilos Totales"
    Tabla_filtrada['Kilos Totales'] = Tabla_filtrada['Kilos Totales'].astype(int)

    # Mostrar la tabla en Streamlit con el estilo ajustado
    st.write(get_table_style(), unsafe_allow_html=True)
    st.markdown(Tabla_filtrada.to_html(index=False, classes='dataframe'), unsafe_allow_html=True)


# Opción Acerca de
def m_about_page():
    st.title('Acerca de')


def m_home_page(user):
    st.title('Bienvenido')
    st.write(f"Hola, {user}. Esta es tu página de inicio. ¡Bienvenido!")


#Opcioon Actualizar Perfil
def update_profile(user):
    try: 
        st.title("Formulario de Registro de Usuario")

        # Verificar si el usuario existe en la base de datos
        user_profile = get_user_profile(user)
        
        if user_profile:
            # Si el usuario existe, mostrar los datos actuales en el formulario
            nombre = st.text_input("Nombre", user_profile['fields'].get('nombre', ''))
            edad = st.number_input("Edad", min_value=15, max_value=60, value=user_profile['fields'].get('edad', 15))
            sexo = st.selectbox("Sexo", ["Hombre", "Mujer"], index=["Hombre", "Mujer"].index(user_profile['fields'].get('sexo', 'Hombre')))
            dias_entrenamiento = st.slider("Cuantos días entrenas a la Semana", 1, 7, value=user_profile['fields'].get('total_entren', 1))
            accion = 'update'
        else:
            # Si el usuario no existe, mostrar el formulario vacío
            nombre = st.text_input("Nombre")
            edad = st.number_input("Edad", min_value=15, max_value=60)
            sexo = st.selectbox("Sexo", ["Hombre", "Mujer"])
            dias_entrenamiento = st.slider("Cuantos días entrenas a la Semana", 1, 7)
            accion = 'insert'
        
        
        if st.button("Guardar datos"):
            insert_or_update_user_profile(user, nombre, edad, sexo, dias_entrenamiento)
            st.success("Datos guardados exitosamente.")
    except Exception as e:
        print(f"Error update_profile: {e}")
        st.error("Ocurrió un error al guardar los datos. Inténtalo de nuevo más tarde.")








