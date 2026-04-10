import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gestión Manantial", layout="wide")

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos(hoja):
    try:
        df = conn.read(worksheet=hoja, ttl=0)
        df.columns = df.columns.str.strip()
        return df.fillna("")
    except:
        return pd.DataFrame()

# --- INTERFAZ ---
st.title("⛪ Sistema de Gestión Manantial Mkids")

tab_asistencia, tab_estudiantes, tab_acudientes, tab_monitor = st.tabs([
    "📍 Registro Asistencia", 
    "👶 Estudiantes", 
    "👥 Acudientes", 
    "🔍 Monitor de Conexión"
])

# ---------------------------------------------------------
# PESTAÑA: ESTUDIANTES (Registro)
# ---------------------------------------------------------
with tab_estudiantes:
    st.subheader("Registrar Nuevo Estudiante")
    with st.form("form_estudiante"):
        id_est = st.text_input("Identificación (ID)")
        p_nom = st.text_input("Primer Nombre")
        p_ape = st.text_input("Primer Apellido")
        f_nac = st.date_input("Fecha de Nacimiento")
        
        if st.form_submit_button("Guardar Estudiante"):
            nuevo_est = pd.DataFrame([{"Identificación": id_est, "Primer Nombre": p_nom, "Primer Apellido": p_ape, "Fecha Nacimiento": str(f_nac)}])
            # Se asume que la hoja de estudiantes se llama "Hoja 1" o "Estudiantes"
            conn.create(worksheet="Hoja 1", data=nuevo_est)
            st.success(f"Estudiante {p_nom} registrado.")

# ---------------------------------------------------------
# PESTAÑA: ACUDIENTES Y RELACIONES
# ---------------------------------------------------------
with tab_acudientes:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Nuevo Acudiente")
        with st.form("form_acudiente"):
            cedula = st.text_input("Cédula Acudiente")
            nombre_acu = st.text_input("Nombre Completo")
            celular = st.text_input("Celular")
            if st.form_submit_button("Registrar Acudiente"):
                nuevo_acu = pd.DataFrame([{"Cedula Acudiente": cedula, "Nombre Acudiente": nombre_acu, "Celular Acudiente": celular}])
                conn.create(worksheet="Acudiente", data=nuevo_acu)
                st.success("Acudiente guardado.")

    with col_b:
        st.subheader("Vincular Estudiante ↔️ Acudiente")
        df_est = cargar_datos("Hoja 1")
        df_acu = cargar_datos("Acudiente")
        
        if not df_est.empty and not df_acu.empty:
            est_sel = st.selectbox("Selecciona Estudiante", df_est['Identificación'].tolist(), 
                                   format_func=lambda x: f"{x} - {df_est[df_est['Identificación']==x]['Primer Nombre'].values[0]}")
            acu_sel = st.selectbox("Selecciona Acudiente", df_acu['Cedula Acudiente'].tolist(),
                                   format_func=lambda x: f"{x} - {df_acu[df_acu['Cedula Acudiente']==x]['Nombre Acudiente'].values[0]}")
            
            if st.button("Crear Vínculo"):
                vinculo = pd.DataFrame([{"Identificacion Estudiante": est_sel, "Cedula Acudiente": acu_sel}])
                conn.create(worksheet="Acudiente Estudiantes", data=vinculo)
                st.success("Vínculo creado correctamente.")

# ---------------------------------------------------------
# PESTAÑA: ASISTENCIA
# ---------------------------------------------------------
with tab_asistencia:
    st.subheader("Marcación de Asistencia")
    df_asistencia_est = cargar_datos("Hoja 1")
    
    if not df_asistencia_est.empty:
        df_asistencia_est['Nombre Full'] = df_asistencia_est['Primer Nombre'] + " " + df_asistencia_est['Primer Apellido']
        seleccionado = st.selectbox("Buscar Estudiante", df_asistencia_est['Nombre Full'].tolist())
        id_final = df_asistencia_est[df_asistencia_est['Nombre Full'] == seleccionado]['Identificación'].values[0]
        
        if st.button("Registrar Entrada"):
            asist_data = pd.DataFrame([{
                "Identificacion Estudiante": str(id_final),
                "Fecha Asistencia": datetime.now().strftime("%Y-%m-%d"),
                "Hora Asistencia": datetime.now().strftime("%H:%M:%S"),
                "Domingos Sin Asistir": 0
            }])
            conn.create(worksheet="Asistencia", data=asist_data)
            st.success(f"Asistencia confirmada para {seleccionado}")
            st.balloons()

# ---------------------------------------------------------
# PESTAÑA: MONITOR (Tu código de validación)
# ---------------------------------------------------------
with tab_monitor:
    st.info("Estado de las hojas en Google Sheets")
    # Aquí puedes dejar el código que ya te funcionó para listar hojas
    if st.button("Verificar nombres de hojas"):
        try:
            import gspread
            gc = gspread.service_account_from_dict(dict(st.secrets["connections"]["gsheets"]))
            url = st.secrets["connections"]["gsheets"]["spreadsheet"]
            sh = gc.open_by_key(url.split("/d/")[1].split("/")[0])
            for h in sh.worksheets():
                st.write(f"📄 {h.title} - {h.row_count} filas")
        except Exception as e:
            st.error(f"Error: {e}")