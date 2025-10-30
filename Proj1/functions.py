'''
-----------------
DataManager
El codigo lo que hara sera:
* Permitir al usuario cargar uno o varios archivos CSV.
* Mostrar un menú para agregar, modificar o eliminar filas en los DataFrames cargados.
* Permitir guardar los cambios en los archivos CSV originales.
* Subir los datos modificados a una base de datos SQL.
* Utiliza pandas para manejar los datos y SQLAlchemy para la conexión con la base de datos.

NOTAS DE HOY:
*hacer que pueda cargar uno o todos los csv de una:
que pongas solo el directorio donde se encuentran en vez de el archivo en especifico.

*que el listar los csv muestre TODOS los datos que estan en el csv seleccionado, sin saltarse nada, incluido el ultimo dato.

*al añadir un nuevo dato y haya id que sea en automatico e incremental
id = len(lista)+1
*

-----------------'''

import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plt

# Conexión a la base de datos (cambia prueba1 por tu base si deseas.)

engine = sqlalchemy.create_engine("mysql+pymysql://root:@localhost/prueba1")

# Diccionario para almacenar los DataFrames y sus rutas
# Diccionario global
csvs = {}  # nombre_archivo : {"df": DataFrame, "ruta": str, "formato": str}

#-----------------
# Cargar archivos
def cargar_archivos():
    rutas = input("\nRutas de los archivos (CSV, JSON o XML, separadas por coma): ").split(",")
    for ruta in rutas:
        ruta = ruta.strip()
        if not ruta:
            continue

        nombre = ruta.split("/")[-1].split(".")[0]
        formato = ruta.split(".")[-1].lower()

        try:
            if formato == "csv":
                df = pd.read_csv(ruta)
            elif formato == "json":
                df = pd.read_json(ruta)
            elif formato == "xml":
                df = pd.read_xml(ruta)
            else:
                print(f"❌ Formato no soportado: {ruta}")
                continue

            csvs[nombre] = {"df": df, "ruta": ruta, "formato": formato}
            print(f"✅ {nombre} ({formato}) cargado correctamente.")
        except Exception as e:
            print(f"⚠️ Error al cargar {ruta}: {e}")

#-----------------
# Guardar según formato original
def guardar_archivo(nombre):
    if nombre not in csvs:
        print(f"❌ No se encontró el archivo: {nombre}")
        return
    df = csvs[nombre]["df"]
    ruta = csvs[nombre]["ruta"]
    formato = csvs[nombre]["formato"]

    try:
        if formato == "csv":
            df.to_csv(ruta, index=False)
        elif formato == "json":
            df.to_json(ruta, orient="records", indent=2)
        elif formato == "xml":
            df.to_xml(ruta, index=False)
        print(f"✅ Cambios guardados en {ruta}")
    except Exception as e:
        print(f"❌ Error al guardar {nombre}: {e}")

#-----------------
def get_csvs_requeridos(*rutas_o_nombres):
    dfs = []
    for entrada in rutas_o_nombres:
        nombre = entrada.split("/")[-1].split(".")[0]
        if nombre not in csvs:
            print(f"❌ Falta el archivo: {nombre}")
            return None
        dfs.append(csvs[nombre]["df"])
    return dfs

#-----------------
def check_csv():
    if not csvs:
        print("No hay archivos cargados.")
        return
    print("Archivos disponibles:")
    for i, nombre in enumerate(csvs):
        print(f"{i+1}. {nombre}")
    try:
        idx = int(input("Elige el número del archivo: ")) - 1
        nombre = list(csvs.keys())[idx]
        df = csvs[nombre]["df"]
        print(df)
    except (ValueError, IndexError):
        print("Opción inválida.")

#-----------------
def modify_csv():
    if not csvs:
        print("No hay archivos cargados.")
        return
    print("\nArchivos disponibles:")
    for i, nombre in enumerate(csvs):
        print(f"{i+1}. {nombre}")
    try:
        idx = int(input("Elige el número del archivo: ")) - 1
        nombre = list(csvs.keys())[idx]
        df = csvs[nombre]["df"]
        print("Columnas disponibles:", list(df.columns))
        fila = int(input("Número de fila a modificar: "))
        if fila < 0 or fila >= len(df):
            print("Fila inválida.")
            return
        columna = input("Nombre de la columna a modificar: ").strip()
        if columna not in df.columns:
            print("Columna inválida.")
            return
        nuevo_valor = input("Nuevo valor: ")
        df.at[fila, columna] = nuevo_valor
        guardar_archivo(nombre)
        csvs[nombre]["df"] = df
    except (ValueError, IndexError):
        print("Entrada inválida.")

#-----------------
def add_row_csv():
    if not csvs:
        print("No hay archivos cargados.")
        return
    print("\nArchivos disponibles:")
    for i, nombre in enumerate(csvs):
        print(f"{i+1}. {nombre}")
    try:
        idx = int(input("Elige el número del archivo: ")) - 1
        nombre = list(csvs.keys())[idx]
        df = csvs[nombre]["df"]
        print("Columnas disponibles:", list(df.columns))
        nueva_fila = {}
        for col in df.columns:
            valor = input(f"Ingrese valor para '{col}': ")
            nueva_fila[col] = valor
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        csvs[nombre]["df"] = df
        guardar_archivo(nombre)
        print("✅ Nueva fila añadida y guardada.")
    except (ValueError, IndexError):
        print("Entrada inválida.")

#-----------------
def delete_row_csv():
    if not csvs:
        print("No hay archivos cargados.")
        return
    print("\nArchivos disponibles:")
    for i, nombre in enumerate(csvs):
        print(f"{i+1}. {nombre}")
    try:
        idx = int(input("Elige el número del archivo: ")) - 1
        nombre = list(csvs.keys())[idx]
        df = csvs[nombre]["df"]
        print(df.head())
        fila = int(input("Número de fila a eliminar (0 es la primera): "))
        if fila < 0 or fila >= len(df):
            print("❌ Fila inválida.")
            return
        df = df.drop(fila).reset_index(drop=True)
        csvs[nombre]["df"] = df
        guardar_archivo(nombre)
        print(f"✅ Fila {fila} eliminada.")
    except (ValueError, IndexError):
        print("Entrada inválida.")

#-----------------
def save_all_csvs():
    for nombre in csvs:
        guardar_archivo(nombre)

#-----------------
def upload_to_sql(nombre=None):
    if not csvs:
        print("No hay archivos cargados.")
        return
    dfs = {nombre: csvs[nombre]} if nombre else csvs
    for n, datos in dfs.items():
        try:
            datos["df"].to_sql(n, con=engine, if_exists='replace', index=False)
            print(f"✅ {n} subido a SQL")
        except Exception as e:
            print(f"❌ No se pudo subir {n}: {e}")

#-----------------
def unify_tables():
    if len(csvs) < 2:
        print("Necesitas al menos 2 archivos cargados.")
        return
    print("\nArchivos disponibles:")
    for i, nombre in enumerate(csvs):
        print(f"{i+1}. {nombre}")
    try:
        indices = input("Elige los números de los archivos a unir (ej: 1,2,3): ")
        indices = [int(x.strip()) - 1 for x in indices.split(",") if x.strip().isdigit()]
        if len(indices) < 2:
            print("Debes seleccionar al menos 2 archivos.")
            return
        nombre_base = list(csvs.keys())[indices[0]]
        merged_df = csvs[nombre_base]["df"]
        for idx in indices[1:]:
            nombre = list(csvs.keys())[idx]
            df = csvs[nombre]["df"]
            print(f"\nUniendo {nombre_base} con {nombre}...")
            print("Columnas disponibles en base:", list(merged_df.columns))
            print("Columnas disponibles en", nombre, ":", list(df.columns))
            key = input("Columna en común para unir: ").strip()
            merged_df = pd.merge(merged_df, df, on=key, how="left")
            nombre_base += f"_{nombre}"
        print("\nResultado:")
        print(merged_df.head())
        guardar = input("¿Guardar como nuevo archivo? (s/n): ").strip().lower()
        if guardar == "s":
            nuevo_nombre = f"{nombre_base}_merge"
            ruta = f"{nuevo_nombre}.csv"
            merged_df.to_csv(ruta, index=False)
            csvs[nuevo_nombre] = {"df": merged_df, "ruta": ruta, "formato": "csv"}
            print(f"✅ Guardado como {ruta}")
    except Exception as e:
        print(f"Error al unir tablas: {e}")

# -------------------------------
# Función que une ventas, facturas y clientes
# -------------------------------
def vc():
    dfs = get_csvs_requeridos("clientes", "facturas_det", "ventas", "facturas_enc")
    if dfs is None:
        print("❌ No se pudieron cargar los DataFrames necesarios.")
        return None
    clientes, facturas_det, ventas, facturas_enc = dfs

    try:
        df = pd.merge(ventas, facturas_det, on="id_factura", how="inner")
        df = pd.merge(df, facturas_enc, on="id_sucursal", how="left")
        df = pd.merge(df, clientes, on="id_cliente", how="left")
        return df
    except Exception as e:
        print(f"❌ Error al unir los datos: {e}")
        return None

# -------------------------------
# Ranking de clientes por total comprado
# -------------------------------
def ranking():
    ventas_clientes = vc()
    if ventas_clientes is None:
        print("No se pudo generar el DataFrame combinado.")
        return
    df_ranking = ventas_clientes.groupby('nombre')['total'].sum().reset_index()
    df_ranking = df_ranking.sort_values(by='total', ascending=False)
    print("Top 10 clientes por total comprado:")
    print(df_ranking.head(10))
    return df_ranking

# -------------------------------
# Ticket promedio por cliente
# -------------------------------
def ticket_promedio():
    ventas_clientes = vc()
    if ventas_clientes is None:
        return
    df_ticket = ventas_clientes.groupby('nombre')['total'].mean().reset_index()
    df_ticket.rename(columns={'total': 'ticket_promedio'}, inplace=True)
    print("Top 10 clientes con mayor ticket promedio:")
    print(df_ticket.sort_values(by='ticket_promedio', ascending=False).head(10))
    return df_ticket

# -------------------------------
# Ventas por mes
# -------------------------------
def ventas_por_mes():
    ventas_clientes = vc()
    if ventas_clientes is None:
        return
    if 'fecha_y' not in ventas_clientes.columns:
        print("❌ La columna 'fecha_y' no está disponible.")
        return
    ventas_clientes['fecha_y'] = pd.to_datetime(ventas_clientes['fecha_y'], errors='coerce')
    df_mes = ventas_clientes.groupby(ventas_clientes['fecha_y'].dt.to_period('M'))['total'].sum().reset_index()
    print("Ventas por mes:")
    print(df_mes)
    return df_mes

# -------------------------------
# Facturas más altas
# -------------------------------
def top_facturas():
    ventas_clientes = vc()
    if ventas_clientes is None:
        return
    columnas_requeridas = ['id_factura', 'fecha_y', 'nombre', 'total']
    for col in columnas_requeridas:
        if col not in ventas_clientes.columns:
            print(f"❌ Falta la columna '{col}' en los datos.")
            return
    top_fact = ventas_clientes.sort_values(by='total', ascending=False).head(10)
    print("Facturas con mayores totales:")
    print(top_fact[columnas_requeridas])
    return top_fact[columnas_requeridas]

# -------------------------------
# Producto más vendido en cantidad
# -------------------------------
def top_prods():
    dfs = get_csvs_requeridos("facturas_det", "productos")
    if not dfs:
        return
    facturas_det, productos = dfs
    if 'id_producto' not in facturas_det.columns or 'cantidad' not in facturas_det.columns:
        print("❌ Columnas necesarias no están presentes en facturas_det.")
        return
    prod_qty = facturas_det.groupby('id_producto')['cantidad'].sum().reset_index()
    prod_qty = pd.merge(prod_qty, productos, on='id_producto', how='left')
    resultado = prod_qty.sort_values(by='cantidad', ascending=False).head(1)
    print("Producto más vendido por cantidad:")
    print(resultado)
    return resultado

# -------------------------------
# Ventas totales por rubro
# -------------------------------
def det_rubro():
    dfs = get_csvs_requeridos("facturas_det", "productos", "rubros")
    if not dfs:
        return
    facturas_det, productos, rubros = dfs
    try:
        df = pd.merge(facturas_det, productos, on='id_producto', how='left')
        df = pd.merge(df, rubros, on='id_rubro', how='left')
        rubro_sum = df.groupby('nombre')['cantidad'].sum().reset_index()
        print("Ventas por rubro:")
        print(rubro_sum.sort_values(by='cantidad', ascending=False))
        return rubro_sum
    except Exception as e:
        print(f"❌ Error al calcular ventas por rubro: {e}")
        return

# -------------------------------
# Gráfico de ventas mensuales
# -------------------------------
def grafico_ventas_mensuales():
    df_ventas = ventas_por_mes()
    if df_ventas is None or df_ventas.empty:
        print("❌ No hay datos para graficar.")
        return
    df_ventas.set_index('fecha_y', inplace=True)
    df_ventas['total'].plot(kind='bar', figsize=(10, 5), color='skyblue')
    plt.title('Ventas Mensuales')
    plt.xlabel('Mes')
    plt.ylabel('Total de Ventas')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# -------------------------------
# Top productos por facturación
# -------------------------------
def fac_prod():
    dfs = get_csvs_requeridos("facturas_det", "productos", "rubros")
    if not dfs:
        return
    facturas_det, productos, rubros = dfs
    if not {'id_producto', 'cantidad'}.issubset(facturas_det.columns):
        print("❌ Columnas faltantes en facturas_det.")
        return
    if 'precio_unitario' not in productos.columns:
        print("❌ Falta la columna 'precio_unitario' en productos.")
        return
    merged = pd.merge(facturas_det, productos, on='id_producto', how='left')
    merged['importe'] = merged['cantidad'] * merged['precio_unitario']
    ranking = merged.groupby('descripcion')['importe'].sum().reset_index()
    top10 = ranking.sort_values(by='importe', ascending=False).head(10)
    print("Top productos por facturación:")
    print(top10)
    return top10

# -------------------------------
# Crear y exportar un DataFrame básico
# -------------------------------
def create_export(filas):
    df = pd.DataFrame(filas, columns=["nombre", "edad", "labor"])
    df.to_csv("empleados.csv", index=False)
    print("✅ Datos guardados en empleados.csv")
    return df

