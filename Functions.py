import streamlit as st
from airtable_db import insert_weight, fetch_all_weights, load_data_from_db
from utils import load_exercises_Json, calcular_rm
import plotly.express as px
import pandas as pd
from pathlib import Path
import pytz

# Opción Registro de RM
def m_registro_rm(user):
    st.title('Registro de Pesos Levantados')
    EjerciciosJson = load_exercises_Json()

    exercise = st.selectbox('Elegir ejercicio', (EjerciciosJson))
    st.radio('Barra', ['45 Lbs.'])
    valorBarra = int(45)

    discos = st.number_input('Total Discos (lbs)', min_value=0)
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
    st.title('Visualización de Pesos')

    # Cargar datos desde Airtable
    df = load_data_from_db(usuario)

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

    # Convertir 'fechahora' a formato datetime y ajustar a la zona horaria local
    local_tz = pytz.timezone('America/Santiago')  # Ajusta según tu zona horaria
    df['fechahora'] = pd.to_datetime(df['fechahora'], errors='coerce', utc=True).dt.tz_convert(local_tz)
    df['RM (Lbs)'] = pd.to_numeric(df['peso_rm'], errors='coerce')
    df['Ejercicio'] = df['ejercicio'].astype(str)

    # Verificar si hay fechas no válidas
    if df['fechahora'].isnull().any():
        st.error("Hay fechas no válidas en los datos. Verifica los registros.")
        st.write(df[df['fechahora'].isnull()])  # Mostrar registros con fechas no válidas para depuración

    # Ordenar datos por 'fechahora' de más reciente a más antiguo
    df = df.sort_values(by='fechahora', ascending=False)

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
    filtered_data = df[df['Ejercicio'] == selected_exercise]

    # Limitar a los 50 registros más recientes
    filtered_data = filtered_data.head(50)

    # Seleccionar columnas y ajustar formato de la fecha
    filtered_data = filtered_data[['Ejercicio', 'RM (Lbs)', 'RM (Kg)', 'Fecha']]
    filtered_data['Fecha'] = filtered_data['Fecha'].dt.strftime('%Y-%m-%d %H:%M')

    # Reiniciar el índice del DataFrame para evitar duplicados
    filtered_data.reset_index(drop=True, inplace=True)

    # Verificar datos filtrados
    st.write("Historial:", filtered_data)

    # Mostrar la tabla en Streamlit con el estilo ajustado
    st.write("""
        <style>
        .dataframe {
            width: 100%;
            border-collapse: collapse;
        }
        .dataframe th, .dataframe td {
            padding: 10px;
            text-align: center;
            border: 1px solid #ddd;
        }
        .dataframe th {
            background-color: #444;  /* Color de fondo oscuro */
            color: white;  /* Color del texto blanco */
        }
        </style>
    """, unsafe_allow_html=True)

    # Crear el gráfico de líneas 1
    fig = px.line(filtered_data, x='Fecha', y='RM (Lbs)', title=f'Peso registrado en el tiempo para {selected_exercise}')
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

    # Crear el gráfico de líneas 2
    fig = px.line(df, x='Fecha', y='RM (Lbs)', color='Ejercicio',
                  title='Peso por Tipo de Ejercicio a lo Largo del Tiempo')

    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)

# Opción Porcentajes
def m_porcentajes(usuario):
    # Cargar datos desde Airtable
    df = load_data_from_db(usuario)

    st.title('Porcentajes')

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

    # Obtener el mayor peso registrado para el ejercicio seleccionado
    max_weight = filtered_data['RM (Lbs)'].max()

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

    # Generar HTML para la tabla
    table_html = df_percentages.to_html(index=False, classes='dataframe')

    # Estilo CSS para la tabla
    st.write("""
        <style>
        .dataframe {
            width: 100%;
            border-collapse: collapse;
        }
        .dataframe th, .dataframe td {
            padding: 4px;  /* Ajustar el alto de cada celda */
            text-align: center;
            border: 1px solid #ddd;
        }
        .dataframe th {
            background-color: #444;  /* Color de fondo oscuro */
            color: white;  /* Color del texto blanco */
        }
        </style>
    """, unsafe_allow_html=True)

    st.write('Tabla de Porcentajes:')
    st.markdown(table_html, unsafe_allow_html=True)

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

    # Convertir el DataFrame a HTML y ocultar el índice
    html = Tabla_filtrada.to_html(index=False, classes='dataframe')

    # Mostrar la tabla en Streamlit con el estilo ajustado
    st.write("""
        <style>
        .dataframe {
            width: 100%;
            border-collapse: collapse;
        }
        .dataframe th, .dataframe td {
            padding: 5px;
            text-align: center;
            border: 1px solid #ddd;
        }
        .dataframe th {
            background-color: #444;  /* Color de fondo oscuro */
            color: white;  /* Color del texto blanco */
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(html, unsafe_allow_html=True)

# Opción Acerca de
def m_about_page():
    st.title('Acerca de')
