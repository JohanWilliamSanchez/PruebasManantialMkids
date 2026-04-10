import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de la página
st.title("🚀 Gestión de Asistencia Manantial")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. Lectura de datos (Lista de niños)
df_niños = conn.read(worksheet="Niños")

# 2. Interfaz de registro
st.subheader("Registrar Asistencia")
niño_seleccionado = st.selectbox("Selecciona al niño:", df_niños["Nombre"])
fecha_hoy = st.date_input("Fecha", datetime.now())

if st.button("Guardar Asistencia"):
    # Aquí iría la lógica para añadir una fila al Excel
    st.success(f"Asistencia registrada para {niño_seleccionado}")

# 3. Visualización de Gráficos
st.divider()
st.subheader("Estadísticas de Seguimiento")
# Ejemplo rápido de gráfico
data_grafico = pd.DataFrame({"Niño": ["Juan", "Pedro", "Ana"], "Asistencias": [5, 3, 8]})
st.bar_chart(data=data_grafico, x="Niño", y="Asistencias")