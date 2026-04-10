
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gestión Mkids", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos(nombre_hoja):
    try:
        df = conn.read(worksheet=nombre_hoja, ttl=0)
        df.columns = df.columns.str.strip().str.replace('\xa0', ' ').str.replace('\u200b', '')
        return df.fillna("")
    except Exception:
        return pd.DataFrame()

def guardar_datos(nombre_hoja, df_nuevo):
    df_existente = cargar_datos(nombre_hoja)
    if df_existente.empty:
        df_final = df_nuevo
    else:
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
    conn.update(worksheet=nombre_hoja, data=df_final)
    st.cache_data.clear()

def limpiar_id(serie):
    return serie.astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

st.title("⛪ Sistema de Gestión Manantial Mkids")

tabs = st.tabs(["📍 Asistencia", "👶 Estudiantes", "👥 Acudientes", "🔗 Vincular", "📅 Hoy"])

# --- TAB: ASISTENCIA ---
with tabs[0]:
    st.subheader("Registrar Asistencia")
    df_est = cargar_datos("Estudiantes")

    if not df_est.empty and len(df_est.columns) > 0:
        col_id = df_est.columns[0]
        df_est[col_id] = limpiar_id(df_est[col_id])
        df_est['Selector'] = df_est[col_id] + " - " + df_est['Primer Nombre'] + " " + df_est['Primer Apellido']
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
            df_est_actual = cargar_datos("Estudiantes")
            col_nombre = df_est_actual.columns[0] if not df_est_actual.empty and len(df_est_actual.columns) > 0 else "Identificación"
            nuevo_e = pd.DataFrame([{
                col_nombre: id_e,
                "Primer Nombre": p_n,
                "Segundo Nombre": s_n,
                "Primer Apellido": p_a,
                "Segundo Apellido": s_a,
                "Fecha Nacimiento": str(f_n)
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
                "Nombre Acudiente": nom,
                "Celular Acudiente": cel,
                "Cedula Acudiente": ced
            }])
            guardar_datos("Acudiente", nuevo_a)
            st.success("✅ Acudiente guardado.")
            st.rerun()

# --- TAB: VINCULAR ---
with tabs[3]:
    st.subheader("Relacionar Estudiante y Acudiente")
    df_e = cargar_datos("Estudiantes")
    df_a = cargar_datos("Acudiente")

    if not df_e.empty and not df_a.empty and len(df_e.columns) > 0:
        col_id_est = df_e.columns[0]
        df_e[col_id_est] = limpiar_id(df_e[col_id_est])
        df_a['Cedula Acudiente'] = limpiar_id(df_a['Cedula Acudiente'])

        df_e['Selector Est'] = df_e[col_id_est] + " - " + df_e['Primer Nombre'] + " " + df_e['Primer Apellido']
        df_a['Selector Acu'] = df_a['Cedula Acudiente'] + " - " + df_a['Nombre Acudiente']

        col1, col2 = st.columns(2)
        sel_est = col1.selectbox("Estudiante", df_e['Selector Est'].tolist())
        sel_acu = col2.selectbox("Acudiente", df_a['Selector Acu'].tolist())

        est_id = sel_est.split(" - ")[0]
        acu_id = sel_acu.split(" - ")[0]

        if st.button("Vincular"):
            vinculo = pd.DataFrame([{
                "Identificacion Estudiante": est_id,
                "Cedula Acudiente": acu_id
            }])
            guardar_datos("Acudiente Estudiantes", vinculo)
            st.success(f"✅ Vínculo creado: {sel_est} ↔ {sel_acu}")
            st.rerun()
    else:
        st.warning("Debes tener estudiantes y acudientes registrados primero.")

# --- TAB: HOY ---
with tabs[4]:
    hoy = datetime.now().strftime("%Y-%m-%d")
    st.subheader(f"📅 Asistencia de Hoy — {hoy}")

    df_asist = cargar_datos("Asistencia")
    df_est = cargar_datos("Estudiantes")

    if df_asist.empty or df_est.empty:
        st.info("No hay registros de asistencia aún.")
    else:
        df_asist['Fecha Asistencia'] = df_asist['Fecha Asistencia'].astype(str).str[:10]
        df_hoy = df_asist[df_asist['Fecha Asistencia'] == hoy].copy()

        if df_hoy.empty:
            st.info("No hay registros de asistencia para hoy todavía.")
        else:
            col_id_est = df_est.columns[0] if len(df_est.columns) > 0 else None

            if col_id_est is None:
                st.error("No se pudo leer la columna de identificación de estudiantes.")
            else:
                df_hoy['Identificacion Estudiante'] = limpiar_id(df_hoy['Identificacion Estudiante'])
                df_est[col_id_est] = limpiar_id(df_est[col_id_est])

                df_hoy = df_hoy.merge(
                    df_est[[col_id_est, 'Primer Nombre', 'Primer Apellido']],
                    left_on='Identificacion Estudiante',
                    right_on=col_id_est,
                    how='left'
                )

                df_hoy['Primer Nombre'] = df_hoy['Primer Nombre'].fillna("Desconocido")
                df_hoy['Primer Apellido'] = df_hoy['Primer Apellido'].fillna("")
                df_hoy['Nombre Completo'] = df_hoy['Primer Nombre'] + " " + df_hoy['Primer Apellido']

                st.metric("Total asistentes hoy", len(df_hoy))
                st.dataframe(
                    df_hoy[['Nombre Completo', 'Identificacion Estudiante', 'Hora Asistencia']],
                    use_container_width=True,
                    hide_index=True
                )
