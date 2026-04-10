import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Asistencia Manantial", layout="centered")

st.title("🚀 Gestión de Asistencia Manantial ")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. Leer datos de la pestaña 'Estudiantes'
# Asegúrate que en el Excel la pestaña se llame exactamente: Estudiantes
try:
    df_estudiantes = conn.read(worksheet="Estudiantes")
    
    # Crear un nombre completo para mostrar en el buscador
    df_estudiantes['Nombre Completo'] = df_estudiantes['Primer Nombre'] + " " + df_estudiantes['Primer Apellido']
    
    st.subheader("Registrar nueva asistencia")
    
    # Buscador de niños
    seleccion = st.selectbox(
        "Selecciona al niño/a:", 
        options=df_estudiantes['Identificación'].tolist(),
        format_func=lambda x: df_estudiantes[df_estudiantes['Identificación'] == x]['Nombre Completo'].iloc[0]
    )

    fecha = st.date_input("Fecha de asistencia", datetime.now())
    hora = datetime.now().strftime("%H:%M:%S")

    if st.button("Registrar Asistencia"):
        # Estructura para la pestaña 'Asistencia'
        nueva_asistencia = pd.DataFrame([{
            "Identificacion Estudiante": seleccion,
            "Fecha Asistencia": str(fecha),
            "Hora Asistencia": hora,
            "Domingos Sin Asistir": 0
        }])
        
        # Actualizar el Google Sheet
        # Nota: La pestaña en el Excel debe llamarse: Asistencia
        conn.create(worksheet="Asistencia", data=nueva_asistencia)
        st.success(f"¡Asistencia registrada para el ID {seleccion}!")
        st.balloons()

except Exception as e:
    st.error(f"Error de conexión o nombres de pestañas: {e}")
    st.info("Revisa que las pestañas en tu Excel se llamen 'Estudiantes' y 'Asistencia'")

# 2. Visualización simple
st.divider()
st.subheader("Resumen de hoy")
if st.button("Ver lista de hoy"):
    asistencias_hoy = conn.read(worksheet="Asistencia")
    st.write(asistencias_hoy)