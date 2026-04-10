import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("🔍 Explorador de Hojas - Manantial")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

st.write("Conectando al Spreadsheet...")

try:
    # Este comando 'client' nos da acceso directo a la librería gspread que usa por debajo
    # para listar todos los nombres de las pestañas
    client = conn.client
    # Obtenemos el ID del spreadsheet desde la URL que pusiste en los secrets
    spreadsheet_id = st.secrets["connections"]["gsheets"]["spreadsheet"].split("/d/")[1].split("/")[0]
    
    # Abrimos el archivo y listamos las hojas
    sh = client.open_by_key(spreadsheet_id)
    hojas = sh.worksheets()
    
    nombres_hojas = [hoja.title for hoja in hojas]

    st.success(f"¡Conexión exitosa! He encontrado {len(nombres_hojas)} hojas:")
    
    # Mostramos la lista con viñetas
    for nombre in nombres_hojas:
        st.markdown(f"* **`{nombre}`**")
    
    st.info("💡 Copia el nombre tal cual aparece arriba (incluyendo espacios o mayúsculas) y úsalo en tu código de asistencia.")

except Exception as e:
    st.error("No pude listar las hojas.")
    st.exception(e)