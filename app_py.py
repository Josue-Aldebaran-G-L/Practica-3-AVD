import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("https://raw.githubusercontent.com/Josue-Aldebaran-G-L/Practica-3-AVD/main/nba_all_elo.csv")
df['date_game'] = pd.to_datetime(df['date_game'], format='%m/%d/%Y')

st.title('Dashboard NBA')

with st.sidebar:
    # Selector de año
    años = sorted(df['year_id'].unique(), reverse=True)
    año_seleccionado = st.selectbox('Seleccionar Año', años)
    
    # Selector de equipo
    equipos = sorted(df['team_id'].unique())
    equipo_seleccionado = st.selectbox('Seleccionar Equipo', equipos)
    
    # Selector de tipo de juego
    tipos_juego = ['Ambos', 'Temporada Regular', 'Playoffs']
    tipo_juego_seleccionado = st.radio('Seleccionar Tipo de Juego', tipos_juego)

# Filtrar los datos
df_filtrado = df[(df['team_id'] == equipo_seleccionado) & (df['year_id'] == año_seleccionado)]

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

col1, col2 = st.columns([7, 3.5])

# Gráfica de líneas para victorias y derrotas acumuladas
if not df_filtrado.empty:
    with col1:
        fig_linea = px.line(
            df_filtrado, 
            x='date_game', 
            y=['victorias_acumuladas', 'derrotas_acumuladas'],
            labels={'value': 'Cantidad', 'date_game': 'Fecha', 'variable': 'Tipo'},
            title='Victorias y Derrotas Acumuladas',
            hover_data={'date_game': True, 'victorias_acumuladas': True, 'derrotas_acumuladas': True}
        )
        
        fig_linea.update_traces(
            hovertemplate=
            '<b>Fecha:</b> %{x}<br>' +
            '<b>Victorias acumuladas:</b> %{y[0]}<br>' +  # Para la primera serie de datos (victorias)
            '<b>Derrotas acumuladas:</b> %{y[1]}<br>' +  # Para la segunda serie de datos (derrotas)
            '<extra></extra>'  # Elimina la leyenda extra
        )
        
        fig_linea.update_layout(
            legend_title_text='Resultado',
            yaxis_title='Cantidad',
            xaxis_title='Fecha'
        )
        st.plotly_chart(fig_linea)
else:
    with col1:
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
    with col2:
        fig_pastel = px.pie(
            datos_pastel, 
            values='Porcentaje', 
            names='Resultado',
            title='Porcentaje de Victorias y Derrotas'
        )
        st.plotly_chart(fig_pastel)
else:
    with col2:
        st.write('No se jugaron partidos.')
