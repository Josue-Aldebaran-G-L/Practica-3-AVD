import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar el dataset
df = pd.read_csv("https://raw.githubusercontent.com/fivethirtyeight/data/master/nba-elo/nba_all_elo.csv")
df['date_game'] = pd.to_datetime(df['date_game'], format='%m/%d/%Y')

# Título del dashboard
st.title('Dashboard NBA')

# Barra lateral
with st.sidebar:
    # Selector de año
    años = sorted(df['year_id'].unique(), reverse=True)
    año_seleccionado = st.selectbox('Seleccionar Año', años)
    
    # Selector de equipo
    equipos = sorted(df['fran_id'].unique())
    equipo_seleccionado = st.selectbox('Seleccionar Equipo', equipos)
    
    # Selector de tipo de juego
    tipos_juego = ['Ambos', 'Temporada Regular', 'Playoffs']
    tipo_juego_seleccionado = st.radio('Seleccionar Tipo de Juego', tipos_juego)

# Filtrar los datos
df_filtrado = df[(df['fran_id'] == equipo_seleccionado) & (df['year_id'] == año_seleccionado)]

if tipo_juego_seleccionado == 'Temporada Regular':
    df_filtrado = df_filtrado[df_filtrado['is_playoffs'] == 0]
elif tipo_juego_seleccionado == 'Playoffs':
    df_filtrado = df_filtrado[df_filtrado['is_playoffs'] == 1]

# Ordenar por fecha
df_filtrado = df_filtrado.sort_values('date_game').reset_index(drop=True)

# Añadir columnas de victorias y derrotas
df_filtrado['victoria'] = (df_filtrado['game_result'] == 'W').astype(int)
df_filtrado['derrota'] = (df_filtrado['game_result'] == 'L').astype(int)

# Sumas acumulativas
df_filtrado['victorias_acumuladas'] = df_filtrado['victoria'].cumsum()
df_filtrado['derrotas_acumuladas'] = df_filtrado['derrota'].cumsum()

# Gráfica de líneas para victorias y derrotas acumuladas
if not df_filtrado.empty:
    fig_linea = px.line(
        df_filtrado, 
        x='date_game', 
        y=['victorias_acumuladas', 'derrotas_acumuladas'],
        labels={'value': 'Cantidad', 'date_game': 'Fecha', 'variable': 'Tipo'},
        title='Victorias y Derrotas Acumuladas'
    )
    fig_linea.update_layout(
        legend_title_text='Resultado',
        yaxis_title='Cantidad',
        xaxis_title='Fecha'
    )
    st.plotly_chart(fig_linea)
else:
    st.write('No hay datos para esta selección.')

# Gráfica de pastel para porcentaje de victorias y derrotas
total_juegos = len(df_filtrado)
total_victorias = df_filtrado['victoria'].sum()
total_derrotas = df_filtrado['derrota'].sum()

if total_juegos > 0:
    datos_pastel = pd.DataFrame({
        'Resultado': ['Victorias', 'Derrotas'],
        'Porcentaje': [total_victorias / total_juegos * 100, total_derrotas / total_juegos * 100]
    })
    fig_pastel = px.pie(
        datos_pastel, 
        values='Porcentaje', 
        names='Resultado',
        title='Porcentaje de Victorias y Derrotas'
    )
    st.plotly_chart(fig_pastel)
else:
    st.write('No se jugaron partidos.')
