import streamlit as st
from airtable_db import insert_weight, fetch_all_weights, load_data_from_db, insert_user_profile, get_user_profile,insert_or_update_user_profile
from utils import load_exercises_Json, calcular_rm, get_table_style
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
def m_visualiza_peso2(usuario):
    # st.title('Registro Histórico de RM')
    st.header('Registro Histórico de RM', divider='gray')

    # Cargar datos desde Airtable
    df = load_data_from_db(usuario)

    # Verificar si el dataframe está vacío
    if df.empty:
        st.warning("No hay datos disponibles para mostrar.")
        return

    # Eliminar la columna 'id' si existe
    if 'id' in df.columns:
        df = df.drop(columns=['id'])

    # Verificar y eliminar índices duplicados
    if df.index.duplicated().any():
        st.write("Índices duplicados detectados y eliminados.")
        df = df[~df.index.duplicated(keep='first')]

    # Verificar y eliminar columnas duplicadas antes de renombrar
    if df.columns.duplicated().any():
        st.write("Columnas duplicadas detectadas antes de renombrar y eliminadas.")
        df = df.loc[:, ~df.columns.duplicated()]

    # Verificar si las columnas necesarias existen antes de continuar
    required_columns = ['fechahora', 'peso_rm', 'ejercicio']
    if not all(column in df.columns for column in required_columns):
        st.error("Faltan columnas necesarias en los datos.")
        return

    # Convertir 'fechahora' a formato datetime y ajustar a la zona horaria local
    local_tz = pytz.timezone('America/Santiago')
    df['fechahora'] = pd.to_datetime(df['fechahora'], errors='coerce', utc=True).dt.tz_convert(local_tz)
    df['RM (Lbs)'] = pd.to_numeric(df['peso_rm'], errors='coerce').round().astype(int)
    df['Ejercicio'] = df['ejercicio'].astype(str)

    # Verificar si hay fechas no válidas
    if df['fechahora'].isnull().any():
        st.error("Hay fechas no válidas en los datos. Verifica los registros.")
        st.write(df[df['fechahora'].isnull()])  # Mostrar registros con fechas no válidas para depuración

    # Ordenar datos por 'fechahora' de más reciente a más antiguo
    df = df.sort_values(by='fechahora', ascending=True)

    # Cambiar los títulos de las columnas
    df.rename(columns={
        'ejercicio': 'Ejercicio',
        'peso_rm': 'RM (Lbs)',
        'fechahora': 'Fecha'
    }, inplace=True)

    # Verificar y eliminar columnas duplicadas después de renombrar
    if df.columns.duplicated().any():
        df = df.loc[:, ~df.columns.duplicated()]

    # Convertir peso de libras a kilogramos y redondear a enteros
    df['RM (Kg)'] = (df['RM (Lbs)'] * 0.453592).round().astype(int)

    # Filtrar datos por el ejercicio seleccionado
    JsonEjercicios = load_exercises_Json()
    selected_exercise = st.selectbox('Selecciona Ejercicio', JsonEjercicios)

    # Verificar si hay datos para el ejercicio seleccionado
    filtered_data = df[df['Ejercicio'] == selected_exercise]
    if filtered_data.empty:
        st.warning(f"No hay datos disponibles para el ejercicio '{selected_exercise}'.")
        return

    # Agregar una columna en filtered_data con el cálculo (RM (Lbs)-45)/2 y redondear
    filtered_data['Lbs por lado'] = ((filtered_data['RM (Lbs)'] - 45) / 2).round().astype(int)

    # Limitar a los 50 registros más recientes
    filtered_data = filtered_data.head(50)

    # Seleccionar columnas.
    filtered_data = filtered_data[['Ejercicio', 'RM (Lbs)', 'RM (Kg)', 'Lbs por lado', 'Fecha']]

    # Ordenar el dataframe por fecha para la tabla
    filtered_data_table = filtered_data.sort_values(by='Fecha', ascending=False)
    filtered_data_table['Fecha'] = filtered_data_table['Fecha'].dt.strftime('%d-%m-%Y %H:%M')

    # Mostrar la tabla en Streamlit con el estilo ajustado
    st.write(get_table_style(), unsafe_allow_html=True)
    st.markdown(filtered_data_table.to_html(index=False, classes='dataframe'), unsafe_allow_html=True)

    # Ordenar el dataframe por fecha para el gráfico
    filtered_data_chart = filtered_data.sort_values(by='Fecha', ascending=True)

    # Crear el gráfico de líneas
    fig = px.line(filtered_data_chart, x='Fecha', y='RM (Lbs)', title=f'Peso registrado en el tiempo para {selected_exercise}')

    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

    st.write('---')

    Selected_ejercicio = st.multiselect(
    'Selecciona Ejercicios para comparar en el gráfico',
    JsonEjercicios, JsonEjercicios
)

    # Filtrar el dataframe por los ejercicios seleccionados
    filtered_df = df[df['Ejercicio'].isin(Selected_ejercicio)]

    # Ordenar el dataframe por fecha en formato datetime
    filtered_df = filtered_df.sort_values(by='Fecha', ascending=True)

    # Crear una nueva columna con la fecha en formato de cadena para la visualización
    filtered_df['Fecha_str'] = filtered_df['Fecha'].dt.strftime('%d-%m-%Y')

    # Agrupar por Fecha_str y Ejercicio, y tomar el valor máximo de RM (Lbs) para manejar duplicados
    filtered_df_agg = filtered_df.groupby(['Fecha_str', 'Ejercicio'])['RM (Lbs)'].max().reset_index()

    # Pivotar el DataFrame para que sea adecuado para st.line_chart
    filtered_df_pivot = filtered_df_agg.pivot(index='Fecha_str', columns='Ejercicio', values='RM (Lbs)')

    # Mostrar el gráfico
    st.line_chart(filtered_df_pivot)


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


# def update_profile(user):
#     #  print(f"Perfil de {user} actualizado")  # Ejemplo de implementación de la función

#         # Formulario de entrada de datos
#     st.title("Formulario de Registro de Usuario")

#     nombre = st.text_input("Nombre")
#     edad = st.number_input("Edad", min_value=15, max_value=60)
#     sexo = st.selectbox("Sexo", ["Hombre", "Mujer"])
#     dias_entrenamiento = st.slider("Cuantos días entrenas a la Semana", 1, 7)

#     if st.button("Guardar datos"):
#         # Guardar datos en Airtable
#         insert_user_profile(user, nombre, edad, sexo, dias_entrenamiento)
#         st.success("Datos guardados exitosamente.")

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
            insert_or_update_user_profile(user, nombre, edad, sexo, dias_entrenamiento, accion)
            st.success("Datos guardados exitosamente.")
    except Exception as e:
        print(f"Error update_profile: {e}")
        st.error("Ocurrió un error al guardar los datos. Inténtalo de nuevo más tarde.")



def formateo_pd(df):
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



def m_visualiza_peso(usuario):
   
    st.header('Registro Histórico de RM', divider='gray')

    # Cargar datos desde Airtable
    df = load_data_from_db(usuario)

    # Verificar si el dataframe está vacío
    if df.empty:
        st.warning("No hay datos disponibles para mostrar.")
        return

    df_formateado,df_graficos,df_sinfiltro = formateo_pd(df)
   

    JsonEjercicios = load_exercises_Json()
    selected_exercise = st.selectbox('Selecciona Ejercicio', JsonEjercicios)

    df_ejercicio = df_formateado[df_formateado['Ejercicio'] == selected_exercise]
    df_ejercicio.head(30)
    df_graficos = df_graficos[df_graficos['Ejercicio'] == selected_exercise]
    # st.write(df_ejercicio)

    st.write(get_table_style(), unsafe_allow_html=True)
    st.markdown(df_ejercicio.to_html(index=False, classes='dataframe'), unsafe_allow_html=True)
    

      # Imprimir líneas en blanco antes del markdown
    st.write('---')

    st.markdown(f'Gráfico de RM para {selected_exercise}')

    fig = px.line(df_graficos, x='Fecha', y="RM Libras")
    st.plotly_chart(fig, theme="streamlit")



    #Grafico todos los ejercicios.
    # fig = px.line(df_sinfiltro, x='Fecha', y='RM Libras', color='Ejercicio', markers=True)
    # st.plotly_chart(fig, theme="streamlit")


    # df_sinfiltro['Fecha'] = pd.to_datetime(df_sinfiltro['Fecha'])  # Asegúrate de que las fechas estén en formato datetime
    df_sinfiltro['Fecha'] = pd.to_datetime(df_sinfiltro['Fecha'], format='%d-%m-%Y %H:%M', dayfirst=True)  # Asegúrate de que las fechas estén en formato datetime
    fig = px.line(df_sinfiltro, x='Fecha', y='RM Libras', color='Ejercicio', markers=True)
    # fig.update_layout(legend=dict(
    #         orientation="h",
    #         # yanchor="bottom",
    #         y=-0.3,
    #         xanchor="center",
    #         x=0.5
    #     ))
    st.plotly_chart(fig, theme="streamlit")