import streamlit as st
import pandas as pd
from datetime import date
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ERP Profesional FP&A", layout="wide")
st.title("🛡️ ERP Profesional: Control de Stock, Costos y Ventas")

# --- ESTRUCTURA DE DATOS (BASE DE DATOS EN MEMORIA) ---
if 'productos' not in st.session_state:
    st.session_state.productos = pd.DataFrame(columns=['SKU', 'Descripción', 'IVA %', 'Derechos %'])
if 'precios_venta' not in st.session_state:
    st.session_state.precios_venta = pd.DataFrame(columns=['SKU', 'Precio Venta Sin IVA $', 'Fecha'])
if 'costos' not in st.session_state:
    st.session_state.costos = pd.DataFrame(columns=['SKU', 'Costo USD', 'Fecha'])
if 'tc' not in st.session_state:
    st.session_state.tc = pd.DataFrame(columns=['Fecha', 'Valor TC'])
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=['CUIT/DNI', 'Nombre', 'Ciudad'])
if 'ventas' not in st.session_state:
    st.session_state.ventas = pd.DataFrame(columns=['Fecha', 'CUIT Cliente', 'SKU', 'Precio Pactado $', 'Total con IVA $'])

# --- FUNCIONES DE SOPORTE PARA IMPORT/EXPORT ---
def descargar_plantilla(df, nombre):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Descargar Plantilla {nombre}",
        data=csv,
        file_name=f"plantilla_{nombre.lower()}.csv",
        mime="text/csv"
    )

def subir_csv(tabla_key):
    archivo = st.file_uploader(f"Subir archivo para {tabla_key}", type=["csv"], key=f"subir_{tabla_key}")
    if archivo:
        try:
            df_nuevo = pd.read_csv(archivo)
            st.session_state[tabla_key] = pd.concat([st.session_state[tabla_key], df_nuevo], ignore_index=True).drop_duplicates()
            st.success(f"Se cargaron {len(df_nuevo)} registros correctamente.")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

# --- NAVEGACIÓN LATERAL ---
menu = st.sidebar.radio("MÓDULOS DE GESTIÓN", [
    "📦 Maestro de Productos (SKU)", 
    "🏷️ Precios de Venta", 
    "🚢 Costos en USD", 
    "💵 Tipo de Cambio", 
    "👥 Base de Clientes", 
    "🛒 Registrar Venta", 
    "📊 Informe de Rentabilidad"
])

# --- 1. MAESTRO DE PRODUCTOS ---
if menu == "📦 Maestro de Productos (SKU)":
    st.header("Gestión de Artículos y Atributos")
    descargar_plantilla(st.session_state.productos, "Productos")
    subir_csv('productos')
    st.subheader("Productos Cargados")
    st.dataframe(st.session_state.productos, use_container_width=True)
    with st.expander("➕ Carga Manual"):
        with st.form("f_p"):
            sku = st.text_input("SKU")
            desc = st.text_input("Descripción")
            iva = st.number_input("IVA %", value=21.0)
            der = st.number_input("Derechos %", value=0.0)
            if st.form_submit_button("Guardar"):
                st.session_state.productos.loc[len(st.session_state.productos)] = [sku, desc, iva, der]
                st.rerun()

# --- 2. PRECIOS DE VENTA ---
elif menu == "🏷️ Precios de Venta":
    st.header("Historial de Precios de Venta (Sin IVA)")
    descargar_plantilla(st.session_state.precios_venta, "Precios")
    subir_csv('precios_venta')
    if not st.session_state.productos.empty:
        with st.form("f_pre"):
            s = st.selectbox("SKU", st.session_state.productos['SKU'])
            p = st.number_input("Precio Sin IVA $", min_value=0.0)
            f = st.date_input("Fecha Vigencia")
            if st.form_submit_button("Actualizar Precio"):
                st.session_state.precios_venta.loc[len(st.session_state.precios_venta)] = [s, p, str(f)]
                st.success("Precio registrado.")
    st.dataframe(st.session_state.precios_venta, use_container_width=True)

# --- 3. COSTOS USD ---
elif menu == "🚢 Costos en USD":
    st.header("Costos Unitarios en USD")
    descargar_plantilla(st.session_state.costos, "Costos")
    subir_csv('costos')
    st.subheader("Cruce de Costos con TC de la Fecha")
    if not st.session_state.costos.empty and not st.session_state.tc.empty:
        c_df, t_df = st.session_state.costos.copy(), st.session_state.tc.copy()
        c_df['Fecha'], t_df['Fecha'] = c_df['Fecha'].astype(str), t_df['Fecha'].astype(str)
        merged = pd.merge(c_df, t_df, on='Fecha', how='left')
        merged['Costo Estimado $ (ARS)'] = merged['Costo USD'] * merged['Valor TC']
        st.dataframe(merged, use_container_width=True)
    else:
        st.info("Cargá datos en 'Costos' y 'Tipo de Cambio' para ver la conversión.")

# --- 4. TIPO DE CAMBIO ---
elif menu == "💵 Tipo de Cambio":
    st.header("Registro de Cotización Diaria")
    descargar_plantilla(st.session_state.tc, "TC")
    subir_csv('tc')
    with st.form("f_tc"):
        f_tc, v_tc = st.date_input("Fecha"), st.number_input("Valor Dólar", min_value=0.0)
        if st.form_submit_button("Guardar TC"):
            st.session_state.tc.loc[len(st.session_state.tc)] = [str(f_tc), v_tc]
            st.rerun()
    st.dataframe(st.session_state.tc, use_container_width=True)

# --- 5. CLIENTES ---
elif menu == "👥 Base de Clientes":
    st.header("Maestro de Clientes")
    descargar_plantilla(st.session_state.clientes, "Clientes")
    subir_csv('clientes')
    st.dataframe(st.session_state.clientes, use_container_width=True)

# --- 6. REGISTRO DE VENTAS ---
elif menu == "🛒 Registrar Venta":
    st.header("Carga de Operaciones")
    if st.session_state.productos.empty or st.session_state.clientes.empty:
        st.error("Faltan Datos: Se requieren Productos y Clientes.")
    else:
        with st.form("f_v"):
            v_fecha = st.date_input("Fecha de Operación")
            cli_noms = st.session_state.clientes.apply(lambda x: f"{x['Nombre']} ({x['CUIT/DNI']})", axis=1)
            c_sel, s_sel = st.selectbox("Cliente", cli_noms), st.selectbox("SKU Producto", st.session_state.productos['SKU'])
            hist = st.session_state.precios_venta[st.session_state.precios_venta['SKU'] == s_sel]
            u_p = hist['Precio Venta Sin IVA $'].iloc[-1] if not hist.empty else 0.0
            p_final, cant = st.number_input("Precio Pactado Sin IVA $", value=float(u_p)), st.number_input("Cantidad", min_value=1)
            if st.form_submit_button("Confirmar Venta"):
                iva = st.session_state.productos[st.session_state.productos['SKU'] == s_sel]['IVA %'].values[0]
                total_iva = (p_final * cant) * (1 + (iva/100))
                cuit = c_sel.split('(')[-1].replace(')', '')
                st.session_state.ventas.loc[len(st.session_state.ventas)] = [str(v_fecha), cuit, s_sel, p_final, total_iva]
                st.success(f"Venta registrada. Total con IVA: ${total_iva:,.2f}")

# --- 7. INFORME DE RENTABILIDAD ---
elif menu == "📊 Informe de Rentabilidad":
    st.header("Reporte de Gestión y Márgenes")
    if st.session_state.ventas.empty:
        st.warning("No hay ventas registradas.")
    else:
        st.write("### Auditoría de Ventas")
        st.dataframe(st.session_state.ventas, use_container_width=True)