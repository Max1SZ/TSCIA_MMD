import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
import tempfile
from datetime import datetime
import numpy as np

# Importar librerías de ML
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

# Importar functions
try:
    from functions import *
except ImportError:
    st.error("⚠️ No se encontró functions.py en el directorio")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Data Manager Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 0.3rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">📊 Data Manager Dashboard</h1>', unsafe_allow_html=True)
st.markdown("---")

# Inicializar session state
if 'csvs' not in st.session_state:
    st.session_state.csvs = csvs.copy() if csvs else {}

if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()

if 'historial_cambios' not in st.session_state:
    st.session_state.historial_cambios = []

# Función para registrar cambios
def registrar_cambio(accion, detalles):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.historial_cambios.append({
        'timestamp': timestamp,
        'accion': accion,
        'detalles': detalles
    })

# Función para guardar CSV
def guardar_csv_seguro(df, nombre_archivo, directorio=None):
    try:
        if directorio is None:
            directorio = st.session_state.temp_dir
        
        ruta_completa = os.path.join(directorio, nombre_archivo)
        df.to_csv(ruta_completa, index=False)
        return ruta_completa
    except Exception as e:
        st.error(f"Error al guardar CSV: {e}")
        return None

# Sidebar para navegación
st.sidebar.title("🧭 Navegación")
st.sidebar.markdown("---")

opcion = st.sidebar.radio(
    "Selecciona una sección:",
    [
        "🏠 Inicio",
        "📁 Gestión de CSVs", 
        "🔧 Operaciones con Datos",
        "📊 Reportes y Análisis",
        "🔮 Predicciones (ML)",
        "📋 Informe del Proyecto",
        "🗄️ Base de Datos SQL"
    ]
)

# Información en el sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Estado del Sistema")
st.sidebar.info(f"**CSVs cargados:** {len(st.session_state.csvs)}")
st.sidebar.info(f"**Cambios realizados:** {len(st.session_state.historial_cambios)}")

# Función para cargar CSVs mejorada
def cargar_csv_streamlit():
    st.subheader("📁 Cargar Archivos CSV")
    
    # Opción 1: Subir archivos
    uploaded_files = st.file_uploader(
        "Opción 1: Selecciona uno o varios archivos CSV",
        type=['csv'],
        accept_multiple_files=True,
        help="Puedes cargar múltiples archivos CSV a la vez"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                # Intentar diferentes encodings
                df = None
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                    try:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    st.error(f"No se pudo leer {uploaded_file.name}")
                    continue
                
                nombre = uploaded_file.name.replace(".csv", "")
                ruta_temp = guardar_csv_seguro(df, uploaded_file.name)
                
                if ruta_temp:
                    # Actualizar session state y diccionario global
                    st.session_state.csvs[nombre] = {"df": df, "ruta": ruta_temp, "formato": "csv"}
                    csvs[nombre] = {"df": df, "ruta": ruta_temp, "formato": "csv"}
                    
                    registrar_cambio("CSV Cargado", f"{nombre} con {df.shape[0]} filas")
                    st.success(f"✅ {nombre} cargado correctamente")
                    
                    with st.expander(f"👁️ Vista previa de {nombre}"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Filas", df.shape[0])
                        col2.metric("Columnas", df.shape[1])
                        col3.metric("Celdas", df.shape[0] * df.shape[1])
                        st.dataframe(df.head(10), use_container_width=True)
                    
            except Exception as e:
                st.error(f"❌ Error al cargar {uploaded_file.name}: {e}")
    
    st.markdown("---")
    
    # Opción 2: Cargar desde directorio
    st.subheader("📂 Opción 2: Cargar todos los CSVs de una carpeta")
    directorio = st.text_input(
        "Ruta del directorio:",
        placeholder="C:/Users/tu_usuario/datos/",
        help="Ingresa la ruta completa de la carpeta con tus CSVs"
    )
    
    if st.button("🔍 Cargar CSVs del directorio"):
        if directorio and os.path.exists(directorio):
            archivos_csv = [f for f in os.listdir(directorio) if f.endswith('.csv')]
            
            if archivos_csv:
                for archivo in archivos_csv:
                    try:
                        ruta_completa = os.path.join(directorio, archivo)
                        df = pd.read_csv(ruta_completa)
                        nombre = archivo.replace(".csv", "")
                        
                        st.session_state.csvs[nombre] = {"df": df, "ruta": ruta_completa, "formato": "csv"}
                        csvs[nombre] = {"df": df, "ruta": ruta_completa, "formato": "csv"}
                        
                        st.success(f"✅ {nombre} cargado")
                    except Exception as e:
                        st.error(f"Error con {archivo}: {e}")
                
                st.rerun()
            else:
                st.warning("No se encontraron archivos CSV en ese directorio")
        else:
            st.error("Directorio no válido")

# ============================================================================
# PÁGINA DE INICIO
# ============================================================================
if opcion == "🏠 Inicio":
    st.header("Bienvenido al Data Manager")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🎯 Funcionalidades Principales
        
        #### 📁 **Gestión de Datos**
        - Cargar archivos CSV individuales o carpetas completas
        - Visualizar datos completos (sin omitir registros)
        - Agregar filas con IDs autoincrementales
        - Modificar y eliminar registros
        
        #### 🔧 **Operaciones Avanzadas**
        - Modificar celdas específicas
        - Unificar múltiples tablas con JOIN
        - Exportar datos procesados
        
        #### 📊 **Análisis y Reportes**
        - Rankings de clientes
        - Análisis de ventas por mes/rubro
        - Tickets promedio
        - Productos más vendidos
        - Gráficos interactivos
        
        #### 🔮 **Predicciones con Machine Learning**
        - Modelos de regresión lineal
        - Predicciones sobre ventas y tendencias
        - Análisis predictivo de datos
        
        #### 🗄️ **Base de Datos SQL**
        - Exportar a MySQL
        - Sincronización automática
        """)
    
    with col2:
        st.markdown("### 📊 Estado Actual")
        
        st.metric("CSVs Cargados", len(st.session_state.csvs))
        st.metric("Cambios Realizados", len(st.session_state.historial_cambios))
        
        if st.session_state.csvs:
            st.markdown("### 📋 Archivos Activos")
            for nombre, datos in st.session_state.csvs.items():
                df = datos["df"]
                with st.expander(f"📄 {nombre}"):
                    st.write(f"**Filas:** {df.shape[0]}")
                    st.write(f"**Columnas:** {df.shape[1]}")
        else:
            st.info("No hay archivos cargados")

# ============================================================================
# PÁGINA DE GESTIÓN DE CSVs
# ============================================================================
elif opcion == "📁 Gestión de CSVs":
    st.header("📁 Gestión de Archivos CSV")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Cargar CSVs", 
        "👁️ Ver CSVs (Completo)", 
        "➕ Añadir Filas", 
        "🗑️ Eliminar Filas"
    ])
    
    with tab1:
        cargar_csv_streamlit()
    
    with tab2:
        st.subheader("Visualizar CSVs Completos")
        if st.session_state.csvs:
            csv_seleccionado = st.selectbox(
                "Selecciona un CSV:",
                list(st.session_state.csvs.keys()),
                key="ver_csv_select"
            )
            
            if csv_seleccionado:
                df = st.session_state.csvs[csv_seleccionado]["df"]
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Filas", df.shape[0])
                col2.metric("Total Columnas", df.shape[1])
                col3.metric("Valores Nulos", df.isnull().sum().sum())
                col4.metric("Memoria", f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB")
                
                st.markdown("---")
                st.markdown("### 📊 Datos Completos (sin omitir ningún registro)")
                
                # MOSTRAR TODOS LOS DATOS SIN SALTARSE NADA
                st.dataframe(df, use_container_width=True, height=600)
                
                st.info(f"Mostrando todas las {len(df)} filas del archivo")
                
                with st.expander("📈 Estadísticas"):
                    st.write(df.describe())
        else:
            st.warning("⚠️ No hay CSVs cargados")
    
    with tab3:
        st.subheader("➕ Añadir Nueva Fila")
        if st.session_state.csvs:
            csv_seleccionado = st.selectbox(
                "Selecciona CSV:",
                list(st.session_state.csvs.keys()),
                key="add_select"
            )
            
            if csv_seleccionado:
                df = st.session_state.csvs[csv_seleccionado]["df"]
                
                st.info(f"📋 Columnas: {', '.join(df.columns)}")
                
                with st.form("nueva_fila_form"):
                    nueva_fila = {}
                    
                    cols = st.columns(2)
                    for idx, col in enumerate(df.columns):
                        with cols[idx % 2]:
                            # ID AUTOINCREMENTAL
                            if col.lower() in ['id', 'id_cliente', 'id_producto', 'id_factura']:
                                nuevo_id = len(df) + 1
                                st.text_input(f"📝 {col}:", value=str(nuevo_id), disabled=True, key=f"add_{col}")
                                nueva_fila[col] = nuevo_id
                            else:
                                nueva_fila[col] = st.text_input(
                                    f"📝 {col}:",
                                    key=f"add_{col}",
                                    help=f"Tipo: {df[col].dtype}"
                                )
                    
                    submitted = st.form_submit_button("✅ Añadir Fila", use_container_width=True)
                    
                    if submitted:
                        try:
                            nuevo_df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
                            
                            st.session_state.csvs[csv_seleccionado]["df"] = nuevo_df
                            csvs[csv_seleccionado]["df"] = nuevo_df
                            
                            # Guardar archivo
                            ruta = st.session_state.csvs[csv_seleccionado]["ruta"]
                            nuevo_df.to_csv(ruta, index=False)
                            
                            registrar_cambio("Fila Añadida", f"{csv_seleccionado}")
                            st.success("✅ Fila añadida correctamente")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        else:
            st.warning("⚠️ No hay CSVs cargados")
    
    with tab4:
        st.subheader("🗑️ Eliminar Fila")
        if st.session_state.csvs:
            csv_seleccionado = st.selectbox(
                "Selecciona CSV:",
                list(st.session_state.csvs.keys()),
                key="delete_select"
            )
            
            if csv_seleccionado:
                df = st.session_state.csvs[csv_seleccionado]["df"]
                
                st.dataframe(df.head(20), use_container_width=True)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fila = st.number_input(
                        "Fila a eliminar (0 = primera):",
                        min_value=0,
                        max_value=len(df)-1,
                        value=0
                    )
                
                with col2:
                    st.markdown("###")
                    if st.button("🗑️ Eliminar", use_container_width=True):
                        try:
                            nuevo_df = df.drop(fila).reset_index(drop=True)
                            
                            st.session_state.csvs[csv_seleccionado]["df"] = nuevo_df
                            csvs[csv_seleccionado]["df"] = nuevo_df
                            
                            ruta = st.session_state.csvs[csv_seleccionado]["ruta"]
                            nuevo_df.to_csv(ruta, index=False)
                            
                            registrar_cambio("Fila Eliminada", f"Fila {fila} en {csv_seleccionado}")
                            st.success(f"✅ Fila {fila} eliminada")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        else:
            st.warning("⚠️ No hay CSVs cargados")

# ============================================================================
# PÁGINA DE OPERACIONES
# ============================================================================
elif opcion == "🔧 Operaciones con Datos":
    st.header("🔧 Operaciones con Datos")
    
    tab1, tab2 = st.tabs(["✏️ Modificar Datos", "🔗 Unificar Tablas"])
    
    with tab1:
        st.subheader("Modificar Celda Específica")
        
        if st.session_state.csvs:
            csv_seleccionado = st.selectbox(
                "Selecciona CSV:",
                list(st.session_state.csvs.keys()),
                key="modify_select"
            )
            
            if csv_seleccionado:
                df = st.session_state.csvs[csv_seleccionado]["df"]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fila = st.number_input("📍 Fila:", min_value=0, max_value=len(df)-1, value=0)
                
                with col2:
                    columna = st.selectbox("📋 Columna:", df.columns.tolist())
                
                with col3:
                    if fila < len(df):
                        valor_actual = df.iloc[fila][columna]
                        st.text_input("📝 Actual:", value=str(valor_actual), disabled=True)
                
                if fila < len(df):
                    with st.expander("👁️ Ver fila completa"):
                        st.write(df.iloc[fila].to_dict())
                
                nuevo_valor = st.text_input("✨ Nuevo valor:")
                
                if st.button("✅ Aplicar Cambio", use_container_width=True):
                    try:
                        if nuevo_valor.strip():
                            df_modificado = df.copy()
                            df_modificado.at[fila, columna] = nuevo_valor
                            
                            st.session_state.csvs[csv_seleccionado]["df"] = df_modificado
                            csvs[csv_seleccionado]["df"] = df_modificado
                            
                            ruta = st.session_state.csvs[csv_seleccionado]["ruta"]
                            df_modificado.to_csv(ruta, index=False)
                            
                            registrar_cambio("Celda Modificada", f"Fila {fila}, Col {columna}")
                            st.success("✅ Cambio aplicado")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning("⚠️ No hay CSVs cargados")
    
    with tab2:
        st.subheader("🔗 Unificar Tablas (Merge)")
        
        if len(st.session_state.csvs) >= 2:
            csvs_seleccionados = st.multiselect(
                "Selecciona CSVs a unir:",
                list(st.session_state.csvs.keys()),
                default=list(st.session_state.csvs.keys())[:2]
            )
            
            if len(csvs_seleccionados) >= 2:
                columna_union = st.text_input("🔑 Columna en común:")
                tipo_union = st.selectbox("Tipo de JOIN:", ["left", "right", "inner", "outer"])
                
                if st.button("🔗 Unificar") and columna_union:
                    try:
                        merged_df = st.session_state.csvs[csvs_seleccionados[0]]["df"]
                        
                        for nombre in csvs_seleccionados[1:]:
                            df = st.session_state.csvs[nombre]["df"]
                            merged_df = pd.merge(merged_df, df, on=columna_union, how=tipo_union)
                        
                        st.success("✅ Tablas unificadas")
                        st.dataframe(merged_df.head(20), use_container_width=True)
                        
                        nuevo_nombre = st.text_input("💾 Nombre:", value="_".join(csvs_seleccionados) + "_merged")
                        
                        if st.button("💾 Guardar"):
                            ruta = guardar_csv_seguro(merged_df, f"{nuevo_nombre}.csv")
                            st.session_state.csvs[nuevo_nombre] = {"df": merged_df, "ruta": ruta, "formato": "csv"}
                            csvs[nuevo_nombre] = {"df": merged_df, "ruta": ruta, "formato": "csv"}
                            st.success(f"✅ Guardado como {nuevo_nombre}")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning("⚠️ Se necesitan al menos 2 CSVs")

# ============================================================================
# PÁGINA DE REPORTES
# ============================================================================
elif opcion == "📊 Reportes y Análisis":
    st.header("📊 Reportes y Análisis")
    
    if st.session_state.csvs:
        # Sincronizar diccionarios
        csvs.update({k: v for k, v in st.session_state.csvs.items()})
        
        reporte = st.selectbox(
            "Selecciona un reporte:",
            [
                "📈 Estadísticas Generales",
                "🏆 Ranking de Clientes",
                "💰 Ticket Promedio",
                "📊 Facturas Más Altas",
                "📅 Ventas por Mes",
                "🎯 Producto Más Vendido",
                "📦 Ventas por Rubro",
                "📈 Gráfico Ventas Mensuales",
                "💎 Top Productos por Facturación"
            ]
        )
        
        if reporte == "📈 Estadísticas Generales":
            st.subheader("📈 Estadísticas Generales")
            
            csv_sel = st.selectbox("Selecciona CSV:", list(st.session_state.csvs.keys()))
            df = st.session_state.csvs[csv_sel]["df"]
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Filas", df.shape[0])
            col2.metric("Columnas", df.shape[1])
            col3.metric("Nulos", df.isnull().sum().sum())
            col4.metric("Duplicados", df.duplicated().sum())
            
            st.dataframe(df.describe(), use_container_width=True)
        
        elif reporte == "🏆 Ranking de Clientes":
            st.subheader("🏆 Ranking de Clientes")
            if st.button("Generar"):
                try:
                    resultado = ranking()
                    if resultado is not None:
                        st.dataframe(resultado.head(10))
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.bar(resultado.head(10)['nombre'], resultado.head(10)['total'])
                        ax.set_title('Top 10 Clientes')
                        ax.set_xlabel('Cliente')
                        ax.set_ylabel('Total')
                        plt.xticks(rotation=45)
                        st.pyplot(fig)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        elif reporte == "💰 Ticket Promedio":
            if st.button("Generar"):
                try:
                    resultado = ticket_promedio()
                    if resultado is not None:
                        st.dataframe(resultado)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        elif reporte == "📊 Facturas Más Altas":
            if st.button("Generar"):
                try:
                    resultado = top_facturas()
                    if resultado is not None:
                        st.dataframe(resultado)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        elif reporte == "📅 Ventas por Mes":
            if st.button("Generar"):
                try:
                    resultado = ventas_por_mes()
                    if resultado is not None:
                        st.dataframe(resultado)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        elif reporte == "🎯 Producto Más Vendido":
            if st.button("Generar"):
                try:
                    resultado = top_prods()
                    if resultado is not None:
                        st.dataframe(resultado)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        elif reporte == "📦 Ventas por Rubro":
            if st.button("Generar"):
                try:
                    resultado = det_rubro()
                    if resultado is not None:
                        st.dataframe(resultado)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        elif reporte == "📈 Gráfico Ventas Mensuales":
            if st.button("Generar"):
                try:
                    grafico_ventas_mensuales()
                    st.pyplot(plt.gcf())
                except Exception as e:
                    st.error(f"Error: {e}")
        
        elif reporte == "💎 Top Productos por Facturación":
            if st.button("Generar"):
                try:
                    resultado = fac_prod()
                    if resultado is not None:
                        st.dataframe(resultado)
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.warning("⚠️ No hay CSVs cargados")

# ============================================================================
# PÁGINA DE PREDICCIONES (ML)
# ============================================================================
elif opcion == "🔮 Predicciones (ML)":
    st.header("🔮 Predicciones con Machine Learning")
    st.markdown("""
    Esta sección permite crear modelos predictivos usando **Regresión Lineal** 
    para predecir valores numéricos basados en variables independientes.
    """)
    
    if st.session_state.csvs:
        csv_sel = st.selectbox("Selecciona CSV:", list(st.session_state.csvs.keys()))
        df = st.session_state.csvs[csv_sel]["df"]
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) >= 2:
            st.markdown("---")
            st.subheader("📊 Configuración del Modelo")
            
            col1, col2 = st.columns(2)
            
            with col1:
                target = st.selectbox(
                    "🎯 Variable a predecir (Y):",
                    numeric_cols,
                    help="Variable dependiente que quieres predecir"
                )
            
            with col2:
                features = st.multiselect(
                    "📋 Variables predictoras (X):",
                    [col for col in numeric_cols if col != target],
                    help="Variables independientes para hacer la predicción"
                )
            
            if features and st.button("🚀 Entrenar Modelo"):
                try:
                    # Preparar datos
                    X = df[features].dropna()
                    y = df.loc[X.index, target]
                    
                    # Dividir datos
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=0.3, random_state=42
                    )
                    
                    # Entrenar modelo
                    modelo = LinearRegression()
                    modelo.fit(X_train, y_train)
                    
                    # Predicciones
                    y_pred = modelo.predict(X_test)
                    
                    # Métricas
                    mse = mean_squared_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                    
                    st.success("✅ Modelo entrenado exitosamente")
                    
                    col1, col2 = st.columns(2)
                    col1.metric("R² Score", f"{r2:.4f}")
                    col2.metric("MSE", f"{mse:.4f}")
                    
                    # Gráfico
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.scatter(y_test, y_pred, alpha=0.5)
                    ax.plot([y_test.min(), y_test.max()], 
                           [y_test.min(), y_test.max()], 
                           'r--', lw=2)
                    ax.set_xlabel('Valores Reales')
                    ax.set_ylabel('Predicciones')
                    ax.set_title('Predicciones vs Valores Reales')
                    st.pyplot(fig)
                    
                    # Predicción manual
                    st.markdown("---")
                    st.subheader("🔮 Hacer Predicción Manual")
                    
                    valores = {}
                    cols = st.columns(len(features))
                    for idx, feature in enumerate(features):
                        with cols[idx]:
                            valores[feature] = st.number_input(
                                f"{feature}:",
                                value=float(X[feature].mean())
                            )
                    
                    if st.button("🎯 Predecir"):
                        entrada = pd.DataFrame([valores])
                        prediccion = modelo.predict(entrada)[0]
                        st.success(f"### Predicción: {prediccion:.2f}")
                        
                        # Guardar modelo en session state
                        st.session_state.modelo_ml = {
                            'modelo': modelo,
                            'features': features,
                            'target': target,
                            'r2': r2,
                            'mse': mse
                        }
                
                except Exception as e:
                    st.error(f"Error al entrenar modelo: {e}")
        else:
            st.warning("Se necesitan al menos 2 columnas numéricas")
    else:
        st.warning("⚠️ No hay CSVs cargados")

# ============================================================================
# PÁGINA DE INFORME DEL PROYECTO
# ============================================================================
elif opcion == "📋 Informe del Proyecto":
    st.header("📋 Informe del Proyecto")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Descripción General",
        "🔧 Funcionalidades",
        "📊 Estadísticas de Uso",
        "📚 Documentación Técnica"
    ])
    
    with tab1:
        st.markdown("""
        # 📊 Data Manager Dashboard
        ## Sistema Integral de Gestión y Análisis de Datos
        
        ---
        
        ### 🎯 Objetivo del Proyecto
        
        **Data Manager Dashboard** es una aplicación web desarrollada con **Streamlit** que permite:
        
        - **Gestionar** archivos CSV de forma intuitiva
        - **Analizar** datos mediante reportes automatizados
        - **Predecir** tendencias usando Machine Learning
        - **Exportar** datos a bases de datos SQL
        ---
        
        ### 🛠️ Tecnologías Utilizadas
        
        | Tecnología | Propósito |
        |------------|-----------|
        | **Python 3.x** | Lenguaje de programación principal |
        | **Streamlit** | Framework para interfaz web |
        | **Pandas** | Manipulación y análisis de datos |
        | **Matplotlib/Seaborn** | Visualización de datos |
        | **Scikit-learn** | Machine Learning |
        | **SQLAlchemy** | Conexión con bases de datos |
        | **MySQL** | Base de datos relacional |
        
        ---
        
        ### 📈 Casos de Uso (de ejemplo)
        
        #### 1️⃣ Gestión de Datos de Ventas
        - Cargar datos de clientes, productos, facturas
        - Analizar patrones de compra
        - Identificar clientes más rentables
        
        #### 2️⃣ Análisis Predictivo
        - Predecir ventas futuras
        - Estimar tickets promedio
        - Proyectar tendencias de mercado
        
        #### 3️⃣ Reportes Ejecutivos
        - Rankings automáticos
        - Gráficos de tendencias
        - Exportación a SQL para BI
        
        ---
        
        ### 🎨 Características Destacadas
        
        ✅ **Interfaz Intuitiva**: Diseño limpio y fácil de usar  
        ✅ **Carga Masiva**: Soporta múltiples archivos y carpetas completas  
        ✅ **Sin Pérdida de Datos**: Visualización completa sin omitir registros  
        ✅ **IDs Autoincrementales**: Gestión automática de identificadores  
        ✅ **Machine Learning Integrado**: Predicciones sin código adicional  
        ✅ **Historial de Cambios**: Trazabilidad de todas las operaciones  
        
        """)
    
    with tab2:
        st.markdown("""
        # 🔧 Funcionalidades Detalladas
        
        ---
        
        ## 📁 Gestión de CSVs
        
        ### Cargar Archivos
        
        **Opción 1: Carga Individual**
        - Selecciona uno o varios archivos CSV
        - Drag & drop o explorador de archivos
        - Previsualización automática
        
        **Opción 2: Carga Masiva por Directorio**
        - Especifica la ruta de una carpeta
        - Carga automática de todos los CSVs
        - Ideal para grandes volúmenes de datos
        
        ### Visualización Completa
        - **Sin omitir datos**: Muestra TODAS las filas
        - Búsqueda y filtrado integrado
        - Estadísticas descriptivas
        - Información de tipos de datos
        
        ### Añadir Filas
        - Formulario dinámico según columnas
        - **IDs autoincrementales**: Generación automática
        - Validación de datos
        - Guardado instantáneo
        
        ### Eliminar Filas
        - Selección por índice
        - Previsualización antes de eliminar
        - Confirmación de acción
        - Actualización automática del archivo
        
        ---
        
        ## 🔧 Operaciones con Datos
        
        ### Modificar Celdas
        - Edición celda por celda
        - Vista previa del valor actual
        - Visualización de fila completa
        - Guardado automático
        
        ### Unificar Tablas (JOIN)
        - Selección múltiple de CSVs
        - Tipos de JOIN: LEFT, RIGHT, INNER, OUTER
        - Especificación de columna clave
        - Exportación del resultado
        
        ---
        
        ## 📊 Reportes y Análisis
        
        ### Reportes Disponibles:
        
        1. **Estadísticas Generales**
           - Resumen descriptivo
           - Distribuciones
           - Valores nulos y duplicados
        
        2. **Ranking de Clientes**
           - Top clientes por compras
           - Gráfico de barras
           - Exportable
        
        3. **Ticket Promedio**
           - Promedio por cliente
           - Análisis de tendencias
        
        4. **Facturas Más Altas**
           - Top facturas
           - Detalle completo
        
        5. **Ventas por Mes**
           - Serie temporal
           - Tendencias mensuales
        
        6. **Producto Más Vendido**
           - Por cantidad
           - Por facturación
        
        7. **Ventas por Rubro**
           - Agrupación por categoría
           - Análisis comparativo
        
        8. **Gráficos Interactivos**
           - Visualizaciones dinámicas
           - Exportación de imágenes
        
        ---
        
        ## 🔮 Predicciones con ML
        
        ### Modelo de Regresión Lineal
        
        **Características:**
        - Selección de variable objetivo
        - Múltiples variables predictoras
        - División train/test automática
        - Métricas de rendimiento (R², MSE)
        
        **Proceso:**
        1. Seleccionar CSV con datos numéricos
        2. Elegir variable a predecir (Y)
        3. Seleccionar variables predictoras (X)
        4. Entrenar modelo
        5. Visualizar resultados
        6. Hacer predicciones manuales
        
        **Métricas:**
        - **R² Score**: Calidad del ajuste (0-1)
        - **MSE**: Error cuadrático medio
        - **Gráfico**: Predicciones vs Valores reales
        
        ---
        
        ## 🗄️ Base de Datos SQL
        
        ### Exportación a MySQL
        - Conexión automática
        - Subida de todos los CSVs o individuales
        - Creación de tablas automática
        - Reemplazo o actualización de datos
        
        ### Configuración
        ```python
        # Conexión configurada en functions.py
        engine = sqlalchemy.create_engine(
            "mysql+pymysql://usuario:password@host/database"
        )
        ```
        
        ---
        
        ## 📥 Descarga de Datos
        
        - Descarga individual por CSV
        - Formato CSV estándar
        - Incluye todos los cambios realizados
        - Conserva estructura original
        
        """)
    
    with tab3:
        st.markdown("# 📊 Estadísticas de Uso del Sistema")
        
        st.markdown("---")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "CSVs Cargados",
                len(st.session_state.csvs),
                delta="Total actual"
            )
        
        with col2:
            total_filas = sum(datos["df"].shape[0] for datos in st.session_state.csvs.values())
            st.metric(
                "Total de Registros",
                total_filas,
                delta="En todos los CSVs"
            )
        
        with col3:
            st.metric(
                "Operaciones Realizadas",
                len(st.session_state.historial_cambios),
                delta="Cambios registrados"
            )
        
        with col4:
            modelo_entrenado = "modelo_ml" in st.session_state
            st.metric(
                "Modelos ML",
                "1" if modelo_entrenado else "0",
                delta="Activos"
            )
        
        st.markdown("---")
        
        # Detalles por CSV
        if st.session_state.csvs:
            st.subheader("📋 Detalles por Archivo")
            
            datos_tabla = []
            for nombre, datos in st.session_state.csvs.items():
                df = datos["df"]
                datos_tabla.append({
                    "Archivo": nombre,
                    "Filas": df.shape[0],
                    "Columnas": df.shape[1],
                    "Memoria (KB)": f"{df.memory_usage(deep=True).sum() / 1024:.2f}",
                    "Valores Nulos": df.isnull().sum().sum(),
                    "Duplicados": df.duplicated().sum()
                })
            
            df_stats = pd.DataFrame(datos_tabla)
            st.dataframe(df_stats, use_container_width=True)
            
            # Gráfico de distribución
            st.markdown("---")
            st.subheader("📊 Distribución de Registros por Archivo")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(df_stats["Archivo"], df_stats["Filas"], color='steelblue')
            ax.set_xlabel("Archivo")
            ax.set_ylabel("Número de Filas")
            ax.set_title("Cantidad de Registros por CSV")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
        
        # Historial de cambios
        st.markdown("---")
        st.subheader("📜 Historial de Cambios")
        
        if st.session_state.historial_cambios:
            df_historial = pd.DataFrame(st.session_state.historial_cambios)
            st.dataframe(df_historial, use_container_width=True)
            
            # Estadísticas del historial
            st.markdown("### 📈 Resumen de Operaciones")
            
            acciones = df_historial['accion'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Operaciones por tipo:**")
                st.write(acciones)
            
            with col2:
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie(acciones.values, labels=acciones.index, autopct='%1.1f%%', startangle=90)
                ax.set_title("Distribución de Operaciones")
                st.pyplot(fig)
        else:
            st.info("No hay operaciones registradas todavía")
        
        # Información del modelo ML (si existe)
        if "modelo_ml" in st.session_state:
            st.markdown("---")
            st.subheader("🔮 Modelo de Machine Learning Activo")
            
            modelo_info = st.session_state.modelo_ml
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Configuración del Modelo:**")
                st.write(f"- Variable objetivo: `{modelo_info['target']}`")
                st.write(f"- Variables predictoras: `{', '.join(modelo_info['features'])}`")
            
            with col2:
                st.write("**Métricas de Rendimiento:**")
                st.metric("R² Score", f"{modelo_info['r2']:.4f}")
                st.metric("MSE", f"{modelo_info['mse']:.4f}")
    
    with tab4:
        st.markdown("""
        # 📚 Documentación Técnica
        
        ---
        
        ## 📂 Estructura del Proyecto
        
        ```
        data-manager-dashboard/
        ├── dashboard.py          # Aplicación principal Streamlit
        ├── functions.py          # Funciones de análisis y reportes
        ├── requirements.txt      # Dependencias del proyecto
        └── data/                 # Directorio de datos (opcional)
        ```
        
        ---
        
        ## 🔧 Instalación
        
        ### Requisitos Previos
        - Python 3.8 o superior
        - pip (gestor de paquetes)
        - MySQL Server (para funcionalidad SQL)
        
        ### Pasos de Instalación
        
        ```bash
        # 1. Clonar o descargar el proyecto
        git clone https://github.com/tu-usuario/data-manager-dashboard.git
        cd data-manager-dashboard
        
        # 2. Crear entorno virtual (recomendado)
        python -m venv venv
        
        # 3. Activar entorno virtual
        # Windows:
        venv\\Scripts\\activate
        # Linux/Mac:
        source venv/bin/activate
        
        # 4. Instalar dependencias
        pip install -r requirements.txt
        
        # 5. Ejecutar la aplicación
        streamlit run dashboard.py
        ```
        
        ---
        
        ## 📦 Dependencias (requirements.txt)
        
        ```txt
        streamlit>=1.28.0
        pandas>=2.0.0
        matplotlib>=3.7.0
        seaborn>=0.12.0
        scikit-learn>=1.3.0
        sqlalchemy>=2.0.0
        pymysql>=1.1.0
        numpy>=1.24.0
        ```
        
        ---
        
        ## ⚙️ Configuración
        
        ### Conexión a Base de Datos MySQL
        
        En `functions.py`, modifica la línea de conexión:
        
        ```python
        engine = sqlalchemy.create_engine(
            "mysql+pymysql://usuario:contraseña@localhost/nombre_bd"
        )
        ```
        
        **Parámetros:**
        - `usuario`: Tu usuario de MySQL
        - `contraseña`: Tu contraseña de MySQL
        - `localhost`: Host del servidor (puede ser IP remota)
        - `nombre_bd`: Nombre de la base de datos
        
        ---
        
        ## 🚀 Ejecución
        
        ### Modo Local
        
        ```bash
        streamlit run dashboard.py
        ```
        
        La aplicación se abrirá en `http://localhost:8501`
        
        ### Modo Producción (Opcional)
        
        ```bash
        streamlit run dashboard.py --server.port 80 --server.address 0.0.0.0
        ```
        
        ---
        
        ## 🧪 Pruebas
        
        ### Datos de Prueba
        
        Puedes generar datos de prueba con la función incluida:
        
        ```python
        from functions import create_export
        
        datos = [
            ("Juan", 30, "Desarrollador"),
            ("María", 28, "Analista"),
            ("Pedro", 35, "Gerente")
        ]
        
        create_export(datos)
        ```
        
        ---
        
        ## 🐛 Solución de Problemas
        
        ### Error: "No module named 'streamlit'"
        
        **Solución:**
        ```bash
        pip install streamlit
        ```
        
        ### Error: Conexión a MySQL fallida
        
        **Causas posibles:**
        - MySQL Server no está corriendo
        - Credenciales incorrectas
        - Puerto bloqueado
        
        **Solución:**
        1. Verifica que MySQL esté corriendo
        2. Comprueba usuario y contraseña
        3. Asegúrate de que el puerto 3306 esté abierto
        
        ### Error: CSV no se carga
        
        **Solución:**
        - Verifica que el archivo sea CSV válido
        - Comprueba el encoding (UTF-8 recomendado)
        - Asegúrate de que no haya caracteres especiales en el nombre
        
        ---
        
        ## 📊 API de Funciones (functions.py)
        
        ### Funciones de Gestión
        
        ```python
        # Cargar archivos
        cargar_archivos()
        
        # Guardar cambios
        guardar_archivo(nombre)
        
        # Subir a SQL
        upload_to_sql(nombre=None)
        
        # Unificar tablas
        unify_tables()
        ```
        
        ### Funciones de Análisis
        
        ```python
        # Ranking de clientes
        ranking()
        
        # Ticket promedio
        ticket_promedio()
        
        # Ventas por mes
        ventas_por_mes()
        
        # Top facturas
        top_facturas()
        
        # Productos más vendidos
        top_prods()
        
        # Ventas por rubro
        det_rubro()
        
        # Top productos por facturación
        fac_prod()
        ```
        
        ### Funciones de Visualización
        
        ```python
        # Gráfico de ventas mensuales
        grafico_ventas_mensuales()
        ```
        
        ---
        
        ## 🔒 Seguridad
        
        ### Recomendaciones:
        
        1. **No subas credenciales al repositorio**
           - Usa variables de entorno
           - Archivo `.env` en `.gitignore`
        
        2. **Sanitiza inputs de usuario**
           - El código ya incluye validaciones básicas
        
        3. **Backups regulares**
           - Guarda copias de tus datos
           - Usa el historial de cambios
        
        ---
        
        ## 📈 Roadmap / Mejoras Futuras
        
        - [ ] Soporte para Excel (XLSX)
        - [ ] Autenticación de usuarios
        - [ ] Más algoritmos de ML (Random Forest, SVM)
        - [ ] Exportación a PDF
        - [ ] API REST
        - [ ] Modo oscuro
        - [ ] Filtros avanzados
        - [ ] Gráficos interactivos (Plotly)
        
        ---
        
        ## 🤝 Contribuciones
        
        ¿Quieres mejorar el proyecto?
        
        1. Fork el repositorio
        2. Crea una rama (`git checkout -b feature/mejora`)
        3. Commit tus cambios (`git commit -m 'Añadir mejora'`)
        4. Push a la rama (`git push origin feature/mejora`)
        5. Abre un Pull Request
        
        ---
        
        ## 📞 Contacto y Soporte
        
        **Desarrollador:** MaxiSZ  
        **Email:** maxisz.1420@gmail.com  
        **GitHub:** https://github.com/Max1SZ
        
        ---
        
        ## 📄 Licencia
        
        Este proyecto fue desarrollado con fines académicos para la cátedra de 
        Procesamiento de Aprendizaje Automático del Instituto Tecnológico Beltrán.
        
        ---
        
        ## 🙏 Agradecimientos
        
        - Profesores Yanina Scudero, David Fernandez y Alejandro Bonavida por 
        darme el conocimiento para realizar este proyecto.
        - Instituto Tecnológico Beltrán
        - Comunidad de Streamlit
        - Bibliotecas open-source utilizadas
        
        """)

# ============================================================================
# PÁGINA DE BASE DE DATOS SQL
# ============================================================================
elif opcion == "🗄️ Base de Datos SQL":
    st.header("🗄️ Base de Datos SQL")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Subir Datos a SQL")
        
        if st.session_state.csvs:
            # Sincronizar con diccionario global
            csvs.update({k: v for k, v in st.session_state.csvs.items()})
            
            csv_seleccionado = st.selectbox(
                "Selecciona CSV para subir:",
                ["📦 Todos los CSVs"] + list(st.session_state.csvs.keys()),
                key="sql_select"
            )
            
            st.info("""
            **Configuración actual:**
            - Host: localhost
            - Base de datos: empresa_ca
            - Motor: MySQL
            
            *Configura la conexión en functions.py*
            """)
            
            if st.button("📤 Subir a MySQL", use_container_width=True):
                try:
                    with st.spinner("Subiendo datos..."):
                        if csv_seleccionado == "📦 Todos los CSVs":
                            upload_to_sql()
                            st.success("✅ Todos los CSVs subidos a SQL")
                            registrar_cambio("SQL Upload", "Todos los CSVs")
                        else:
                            upload_to_sql(csv_seleccionado)
                            st.success(f"✅ {csv_seleccionado} subido a SQL")
                            registrar_cambio("SQL Upload", csv_seleccionado)
                except Exception as e:
                    st.error(f"❌ Error al subir a SQL: {e}")
                    st.info("💡 Verifica la conexión y credenciales en functions.py")
        else:
            st.warning("⚠️ No hay CSVs cargados")
    
    with col2:
        st.subheader("📥 Descargar CSVs Modificados")
        
        if st.session_state.csvs:
            st.info("Descarga los archivos con todos los cambios aplicados")
            
            for nombre, datos in st.session_state.csvs.items():
                df = datos["df"]
                csv_data = df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label=f"📥 Descargar {nombre}.csv",
                    data=csv_data,
                    file_name=f"{nombre}_modificado.csv",
                    mime="text/csv",
                    key=f"download_{nombre}",
                    use_container_width=True
                )
        else:
            st.warning("⚠️ No hay CSVs para descargar")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Data Manager Dashboard**")

with col2:
    st.markdown("Desarrollado con ❤️ usando Streamlit")

with col3:
    st.markdown(f"📅 {datetime.now().strftime('%Y')}")
