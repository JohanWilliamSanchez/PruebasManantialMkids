import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gestión Mkids", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos(nombre_hoja):
    try:
        df = conn.read(worksheet=nombre_hoja, ttl=0)
        df.columns = df.columns.str.strip()
        return df.fillna("")
    except Exception:
        return pd.DataFrame()

def guardar_datos(nombre_hoja, df_nuevo):
    df_existente = cargar_datos(nombre_hoja)
    
    if df_existente.empty:
        df_final = df_nuevo
    else:
        # Alinear columnas para evitar desorden
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_final = df_final[df_existente.columns]  # <- mantiene el orden de columnas original
    
    conn.update(worksheet=nombre_hoja, data=df_final)
    st.cache_data.clear()  # <- fuerza recarga en la siguiente lectura

st.title("⛪ Sistema de Gestión Manantial Mkids")

tabs = st.tabs(["📍 Asistencia", "👶 Estudiantes", "👥 Acudientes", "🔗 Vincular"])

# --- TAB: ASISTENCIA ---
with tabs[0]:
    st.subheader("Registrar Asistencia")
    df_est = cargar_datos("Estudiantes")
    
    if not df_est.empty:
        df_est['Selector'] = df_est['Identificación'].astype(str) + " - " + df_est['Primer Nombre'] + " " + df_est['Primer Apellido']
        seleccion = st.selectbox("Seleccione el Estudiante", df_est['Selector'].tolist())
        id_estudiante = seleccion.split(" - ")[0]

        if st.button("Registrar Entrada"):
            nueva_asistencia = pd.DataFrame([{
                "Identificacion Estudiante": id_estudiante,
                "Fecha Asistencia": datetime.now().strftime("%Y-%m-%d"),
                "Hora Asistencia": datetime.now().strftime("%H:%M:%S"),
                "Domingos Sin Asistir": 0
            }])
            guardar_datos("Asistencia", nueva_asistencia)
            st.success("✅ Asistencia registrada correctamente.")
            st.balloons()
            st.rerun()
    else:
        st.error("No hay estudiantes registrados aún.")

# --- TAB: ESTUDIANTES ---
with tabs[1]:
    st.subheader("Nuevo Estudiante")
    with st.form("form_est", clear_on_submit=True):
        id_e = st.text_input("Identificación")
        p_n = st.text_input("Primer Nombre")
        s_n = st.text_input("Segundo Nombre")
        p_a = st.text_input("Primer Apellido")
        s_a = st.text_input("Segundo Apellido")
        f_n = st.date_input("Fecha Nacimiento", min_value=datetime(2010, 1, 1))
        
        if st.form_submit_button("Guardar"):
            nuevo_e = pd.DataFrame([{
                "Identificación": id_e, "Primer Nombre": p_n, "Segundo Nombre": s_n,
                "Primer Apellido": p_a, "Segundo Apellido": s_a, "Fecha Nacimiento": str(f_n)
            }])
            guardar_datos("Estudiantes", nuevo_e)
            st.success("✅ Estudiante guardado.")
            st.rerun()

# --- TAB: ACUDIENTES ---
with tabs[2]:
    st.subheader("Nuevo Acudiente")
    with st.form("form_acu", clear_on_submit=True):
        ced = st.text_input("Cédula Acudiente")
        nom = st.text_input("Nombre Completo")
        cel = st.text_input("Celular")
        
        if st.form_submit_button("Guardar Acudiente"):
            nuevo_a = pd.DataFrame([{
                "Nombre Acudiente": nom, "Celular Acudiente": cel, "Cedula Acudiente": ced
            }])
            guardar_datos("Acudiente", nuevo_a)
            st.success("✅ Acudiente guardado.")
            st.rerun()

# --- TAB: VINCULAR ---
with tabs[3]:
    st.subheader("Relacionar Estudiante y Acudiente")
    df_e = cargar_datos("Estudiantes")
    df_a = cargar_datos("Acudiente")
    
    if not df_e.empty and not df_a.empty:
        col1, col2 = st.columns(2)
        est_id = col1.selectbox("Estudiante", df_e['Identificación'].tolist())
        acu_id = col2.selectbox("Acudiente (Cédula)", df_a['Cedula Acudiente'].tolist())
        
        if st.button("Vincular"):
            vinculo = pd.DataFrame([{
                "Identificacion Estudiante": est_id, "Cedula Acudiente": acu_id
            }])
            guardar_datos("Acudiente Estudiantes", vinculo)
            st.success("✅ Vínculo creado.")
            st.rerun()
    else:
        st.warning("Debes tener estudiantes y acudientes registrados primero.")