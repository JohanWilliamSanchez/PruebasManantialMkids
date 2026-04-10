import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("🧪 Prueba de Conexión a Google Sheets")

try:
    # Crear la conexión
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leer datos directamente (esto valida la conexión sin usar .client)
    df = conn.read()
    
    st.success("✅ ¡CONEXIÓN EXITOSA!")
    st.write(f"**Filas encontradas:** {len(df)}")
    st.dataframe(df.head(10))

except Exception as e:
    st.error("❌ LA CONEXIÓN FALLÓ")
    error_str = str(e)
    st.write(f"Error técnico: `{error_str}`")
    
    # Diagnóstico
    st.write("---")
    st.write("### Verificación de Secrets:")
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        st.success(f"✅ Secret encontrado: `{url[:50]}...`")
    except Exception as se:
        st.error(f"❌ Secret NO encontrado: `{str(se)}`")
        st.code("""
# Crea el archivo: .streamlit/secrets.toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/TU_ID_AQUI"
type = "service_account"
project_id = "tu-proyecto"
private_key_id = "..."
private_key = \"\"\"-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----\"\"\"
client_email = "...@....iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
        """, language="toml")