import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_icon='🏠', page_title='Home', layout='centered') # Pestaña navegador
@st.cache_data
def load_data():
    return pd.read_excel('Datos.xlsx')
df = load_data()

# Botón para resetear cache
if st.button('🔄 Resetear Cache'):
    st.cache_data.clear()
    st.success("¡Cache reseteado!")

st.image('./src/logo.png', width=400) # Logo

st.markdown('***')
if st.checkbox('Total de viajes y distancia promedio por tipo de flota y ciudad'):
    st.write('¿Cuál es el total de viajes y la distancia promedio por tipo de flota y ciudad?')

    # Filtro de distancia
    filter_value = st.number_input('Ingrese distancia a filtrar', min_value=0.0, step=1.0)
    if filter_value >= 0:
        df_trips = df[df['Distancia'] >= filter_value]
    else:
        df_trips = df.copy()

    # Agrupo por ciudad y tipo de flota
    df_trips = df_trips.groupby(['city', 'fleet']).agg(
        total_trips=('Distancia', 'count'),
        distance_average=('Distancia', 'mean')
    ).reset_index()

    # Ordenar por ciudad y tipo de flota
    df_trips = df_trips.sort_values(by=['city', 'fleet'])

    # Agregar totales por ciudad
    city_total = df_trips.groupby('city').agg(
        total_trips=('total_trips', 'sum'),
        distance_average=('distance_average', 'mean')
    ).reset_index()

    # Agregar una columna adicional "fleet" para identificar los totales
    city_total['fleet'] = 'Todas'

    # Combinar totales por ciudad con los datos desglosados por flota
    result = pd.concat([df_trips, city_total], sort=False).sort_values(
        by=['city', 'fleet'], na_position='last'
    )

    # Mostrar la tabla resultante
    st.dataframe(result)

st.markdown('***')
if st.checkbox('## Usuarios con mayor gasto total y gasto promedio'):
    st.write('¿Cuáles son los cinco usuarios con mayor gasto total y cuál es su gasto promedio por viaje?')
    # Filtro
    selected_city = st.selectbox('Seleccione la ciudad (o deje en blanco para todas):', [""] + list(df['city'].unique()))
    selected_fleet = st.selectbox('Seleccione la flota (o deje en blanco para todas):', [""] + list(df['fleet'].unique()))
    # Filtrar el DataFrame según las selecciones
    df_filtered = df.copy()
    if selected_city:
        df_filtered = df_filtered[df_filtered['city'] == selected_city]
    if selected_fleet:
        df_filtered = df_filtered[df_filtered['fleet'] == selected_fleet]
    # Calcular el gasto total y promedio por usuario
    df_users = df_filtered.groupby('user_id').agg(gasto_total=('trip_cost', 'sum'),gasto_promedio=('trip_cost', 'mean')).reset_index()
    # Ordenar por gasto total y seleccionar los 5 usuarios con mayor gasto
    top_users = df_users.sort_values(by='gasto_total', ascending=False).head(5)
    st.dataframe(top_users)
    # Creo gráfico de barras
    fig, ax = plt.subplots(figsize=(8, 5)) 
    ax.barh(top_users['user_id'], top_users['gasto_total'], label='Gasto Total', alpha=0.7)
    ax.barh(top_users['user_id'], top_users['gasto_promedio'], label='Gasto Promedio por Viaje', alpha=0.7)
    # Personalizar el gráfico
    ax.set_xlabel('Gasto ($)')
    ax.set_ylabel('Usuarios')
    ax.set_title('Usuarios con mayor gasto total y promedio por viaje')
    ax.legend()
    ax.invert_yaxis()
    st.pyplot(fig)

st.markdown('***')
if st.checkbox('Comparación de viajes completados y cancelados por ciudad y flota'):
    # Crear una columna para indicar si el viaje fue cancelado
    df_trips_new = df.copy()
    df_trips_new['canceled'] = ~df_trips_new['completed']
    # Agrupar por ciudad y flota para contar completados y cancelados
    df_grouped = df_trips_new.groupby(['city', 'fleet']).agg(completed_count=('completed', 'sum'),canceled_count=('canceled', 'sum')).reset_index()
    # Calcular totales y porcentajes
    df_grouped['total_trips'] = df_grouped['completed_count'] + df_grouped['canceled_count']
    df_grouped['completed_percentage'] = (df_grouped['completed_count'] / df_grouped['total_trips'] * 100).round(2)
    df_grouped['canceled_percentage'] = (df_grouped['canceled_count'] / df_grouped['total_trips'] * 100).round(2)
    # Seleccionar columnas finales para visualización
    df_result = df_grouped[['city', 'fleet', 'completed_count', 'canceled_count','completed_percentage', 'canceled_percentage']]
    st.dataframe(df_result) 

st.markdown('***')
if st.checkbox('Año promedio de los vehículos por tipo de flota'):
    # Agrupo por tipo de flota y calculo el intervalo de años
    df_years = df.groupby('fleet').agg(min_year=('Año del vehiculo', 'min'), max_year=('Año del vehiculo', 'max')).reset_index()
    df_years['Promedio de Año del vehiculo'] = ((df_years['min_year'] + df_years['max_year']) / 2).round().astype(int)
    # Renombro columnas
    df_years = df_years.rename(columns={'min_year': 'Año más antiguo', 'max_year': 'Año más reciente'})
    st.dataframe(df_years)

st.markdown('***')
if st.checkbox('Costos promedio de viaje por tipo de flota'):
    st.write('¿Qué tipo de flota tiene los costos de viaje completados más altos en promedio?')
    # Filtrar viajes completados
    completed_trips = df[df['completed']]
    # Calculo el costo promedio por tipo de flota
    avg_costs = completed_trips.groupby('fleet').agg(avg_costs=('trip_cost', 'mean')).reset_index()
    # Ordenar por costo descendente
    avg_costs = avg_costs.sort_values(by='avg_costs', ascending=False)
    st.dataframe(avg_costs)

st.markdown('***')
if st.checkbox('Frecuencia de viajes por hora del día'):
    st.write('¿En qué horas del día se realizan más viajes?')
    st.write('¿Cuál es la hora con mayor cantidad de viajes completados?')
    # Convertir a hora ccs. UTC-4
    df['date'] = pd.to_datetime(df['date'])
    df['hour_ccs'] = (df['date'] - pd.Timedelta(hours = 4)).dt.hour
    # Filtros
    fleets = ["Todas"] + list(df['fleet'].unique())
    selected_fleet = st.selectbox('Seleccione el tipo de flota:', options = fleets)
    # Filtrar por flota seleccionada
    if selected_fleet != "Todas":
        filt_trips = df[df['fleet'] == selected_fleet]
    else:
        filt_trips = df.copy()
    # Calculo frecuencia de viajes completados por hora
    h_frequency = filt_trips[filt_trips['completed']].groupby('hour_ccs').size()
    # Calculo promedio
    total_h = filt_trips['hour_ccs'].nunique()
    h_avg = (h_frequency / total_h).reset_index(name='Promedio').round().astype(int)
    # Renombrar columna de hora
    h_table = h_avg.rename(columns={'hour_ccs': 'Hora', 'Promedio': 'Promedio de viajes completados'})
    st.dataframe(h_table)
    
    # Gráfico de barras
    plt.figure(figsize=(8, 5))
    plt.bar(h_table['Hora'], h_table['Promedio de viajes completados'], color='skyblue')
    plt.title(f'Promedio de Viajes Completados por Hora- {selected_fleet}')
    plt.xlabel('Hora del Día')
    plt.ylabel('Promedio de Viajes Completados')
    plt.xticks(range(0, 24))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(plt)

st.markdown('***')
if st.checkbox('Distribución de viajes por usuario'):
    st.write('¿Cuál es la distribución de la cantidad de viajes por usuario?')
    # Filtrar viajes completados
    completed_trips = df[df['completed'] == True]
    # Calcular la cantidad de viajes por usuario
    user_trips = completed_trips.groupby('user_id').size()
    # Clasificar usuarios en intervalos de 2 a 10
    intervals = list(range(0, user_trips.max() + 2, 2))
    user_distribution = pd.cut(user_trips, bins=intervals, right=False).value_counts().sort_index()
    # Crear un DataFrame para la tabla dinámica
    distribution_table = user_distribution.reset_index()
    distribution_table.columns = ['Intervalo de viajes', 'Cantidad de usuarios']
    # Ordenar por cantidad de usuarios de mayor a menor
    distribution_table = distribution_table.sort_values(by='Cantidad de usuarios', ascending=False)
    # Mostrar la tabla en Streamlit
    st.dataframe(distribution_table)
    # Gráfico dinámico
    plt.figure(figsize=(8, 5))
    plt.bar(distribution_table['Intervalo de viajes'].astype(str), distribution_table['Cantidad de usuarios'], color='skyblue')
    plt.title('Distribución de cantidad de viajes por usuario')
    plt.xlabel('Intervalo de viajes')
    plt.ylabel('Cantidad de usuarios')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(plt)

st.markdown('***')
if st.checkbox('Tabla dinámica de viajes por ciudad y tipo de flota'):
    st.write('Seleccione el tipo de flota para visualizar la cantidad de viajes por ciudad.')
    # Filtro
    # Filtrar viajes completados
    completed_trips = df[df['completed'] == True]
    fleets = ["Todas"] + list(completed_trips['fleet'].unique()) 
    selected_fleet = st.selectbox('Seleccione el tipo de flota:', options=fleets)
    # Filtrar datos según la flota seleccionada
    if selected_fleet != "Todas":
        filt_trips = completed_trips[completed_trips['fleet'] == selected_fleet]
    else:
        filt_trips = completed_trips.copy()
    # Cantidad de viajes por ciudad
    city_trips = filt_trips.groupby('city').size().reset_index(name='Cantidad de Viajes')
    # Ordenar la tabla
    city_trips = city_trips.sort_values(by='Cantidad de Viajes', ascending=False)
    st.dataframe(city_trips)