import streamlit as st
from streamlit_gsheets import GSheetsConnection
import gspread

st.set_page_config(page_title="Monitor Manantial", page_icon="📊")

st.title("🛠️ Panel de Control - Google Sheets")

# Crear las pestañas
tab1, tab2 = st.tabs(["📡 Estado de Conexión", "📋 Inventario de Hojas"])

try:
    # Inicializamos la conexión una sola vez
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Preparamos el acceso a gspread para detalles técnicos
    gc = gspread.service_account_from_dict(dict(st.secrets["connections"]["gsheets"]))
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet_id = url.split("/d/")[1].split("/")[0]
    documento = gc.open_by_key(sheet_id)
    hojas = documento.worksheets()

    # --- CONTENIDO PESTAÑA 1 ---
    with tab1:
        st.success("✅ Conexión establecida con Google Cloud API")
        st.metric("Archivo Vinculado", documento.title)
        st.write("La cuenta de servicio tiene permisos de Editor y el archivo Secrets está configurado correctamente.")
        
        if st.button("🔄 Re-verificar conexión"):
            st.rerun()

    # --- CONTENIDO PESTAÑA 2 ---
    with tab2:
        st.subheader("Hojas encontradas en el documento")
        st.write(f"Se detectaron **{len(hojas)}** pestañas disponibles:")
        
        for i, h in enumerate(hojas, 1):
            with st.expander(f"Hoja #{i}: {h.title}"):
                col1, col2 = st.columns(2)
                col1.write(f"**Filas totales:** {h.row_count}")
                col2.write(f"**Columnas totales:** {h.col_count}")
                # Botón de vista previa rápida
                if st.button(f"Ver datos de {h.title}", key=f"btn_{i}"):
                    data = conn.read(worksheet=h.title, ttl=0)
                    st.dataframe(data.head(10))

except Exception as e:
    st.error("❌ Fallo en la comunicación")
    st.write(f"Error detallado: `{str(e)}`")