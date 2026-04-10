import streamlit as st
from streamlit_gsheets import GSheetsConnection
import gspread

st.title("🧪 Prueba de Conexión a Google Sheets")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    st.success("✅ ¡CONEXIÓN EXITOSA!")
    
    # Listar hojas usando gspread directamente
    gc = gspread.service_account_from_dict(dict(st.secrets["connections"]["gsheets"]))
    
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet_id = url.split("/d/")[1].split("/")[0]
    
    documento = gc.open_by_key(sheet_id)
    hojas = documento.worksheets()
    
    st.write(f"**Archivo:** {documento.title}")
    st.write(f"**Total de hojas:** {len(hojas)}")
    st.write("---")
    st.write("### 📋 Hojas encontradas:")
    
    for i, h in enumerate(hojas, 1):
        col1, col2, col3 = st.columns([1, 3, 2])
        with col1:
            st.write(f"**#{i}**")
        with col2:
            st.info(f"📄 {h.title}")
        with col3:
            st.write(f"Filas: {h.row_count} | Cols: {h.col_count}")

except Exception as e:
    st.error("❌ ERROR")
    st.write(f"`{str(e)}`")