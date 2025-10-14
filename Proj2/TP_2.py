"""
Ejercicio Práctico: Análisis de Recompra en una Campaña de Marketing
Instituto Tecnológico Beltrán - Modelizado de Minería de Datos
"""

# ============================================================================
# IMPORTACIONES
# ============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import warnings
warnings.filterwarnings('ignore')

plt.ion()  # modo interactivo

# ============================================================================
# CARGA Y ANÁLISIS DE DATOS (cambiar por direccion donde este el excel)
# ============================================================================
df = pd.read_excel("C:\\Users\\estudiante\\Desktop\\TareasPYTHON\\2025\\MMD\\Mini_Proyecto_Clientes_Promociones.xlsx")

print("\n📊 Información del Dataset:")
print(df.info())

print("\n📈 Estadísticas Descriptivas:")
print(df.describe())

print("\n👀 Primeras 5 filas del dataset:")
print(df.head())

print("\n🔍 Verificación de valores nulos:")
print(df.isnull().sum())

print("\n📊 Distribución de variables categóricas:")
print("\nGénero:")
print(df['Genero'].value_counts())
print("\nRecibió Promoción:")
print(df['Recibio_Promo'].value_counts())
print("\nRecompra:")
print(df['Recompra'].value_counts())

# ============================================================================
# ANÁLISIS INICIAL DE EFECTIVIDAD
# ============================================================================
total_clientes = len(df)
con_promo = df[df['Recibio_Promo'] == 'Sí']
sin_promo = df[df['Recibio_Promo'] == 'No']
recompra_con_promo = len(con_promo[con_promo['Recompra'] == 'Sí'])
recompra_sin_promo = len(sin_promo[sin_promo['Recompra'] == 'Sí'])

print("\n🎯 ANÁLISIS INICIAL DE EFECTIVIDAD:")
print(f"Total de clientes: {total_clientes}")
print(f"Clientes con promoción: {len(con_promo)} ({len(con_promo)/total_clientes*100:.1f}%)")
print(f"Clientes sin promoción: {len(sin_promo)} ({len(sin_promo)/total_clientes*100:.1f}%)")
print(f"\nTasa de recompra CON promoción: {recompra_con_promo/len(con_promo)*100:.1f}%")
print(f"Tasa de recompra SIN promoción: {recompra_sin_promo/len(sin_promo)*100:.1f}%")

# ============================================================================
# TRANSFORMACIÓN Y CODIFICACIÓN
# ============================================================================
df_procesado = df.copy()
df_procesado['Genero'] = df_procesado['Genero'].map({'F': 0, 'M': 1})
df_procesado['Recibio_Promo'] = df_procesado['Recibio_Promo'].map({'Sí': 1, 'No': 0})
df_procesado['Recompra'] = df_procesado['Recompra'].map({'Sí': 1, 'No': 0})

# ============================================================================
# MODELADO PREDICTIVO - ÁRBOL DE DECISIÓN
# ============================================================================
X = df_procesado.drop(['Cliente_ID', 'Recompra'], axis=1)
y = df_procesado['Recompra']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo = DecisionTreeClassifier(max_depth=4, random_state=42)
modelo.fit(X_train, y_train)
y_pred = modelo.predict(X_test)

cm = confusion_matrix(y_test, y_pred)
accuracy = accuracy_score(y_test, y_pred)
feature_importance = pd.DataFrame({
    'Variable': X.columns,
    'Importancia': modelo.feature_importances_
}).sort_values('Importancia', ascending=False) 

print("\n📊 MATRIZ DE CONFUSIÓN:")
print(cm)
print("\n📈 REPORTE DE CLASIFICACIÓN:")
print(classification_report(y_test, y_pred))
print(f"\n🎯 ACCURACY DEL MODELO: {accuracy*100:.2f}%")
print("\n⭐ IMPORTANCIA DE LAS VARIABLES:")
print(feature_importance.to_string(index=False))

# ============================================================================
# RECOMENDACIONES ESTRATÉGICAS
# ============================================================================
print("\n🎯 RECOMENDACIONES ESTRATÉGICAS:")
print("""
1. Aumentar el monto de promociones entre $600-$800.
2. Enfocarse en clientes con ingresos mayores a $40,000.
3. Implementar programas de lealtad después de la 2° compra.
4. Priorizar segmento de edad 35–50 años.
5. Personalizar montos según historial de compras.
6. Hacer seguimiento post-promoción a quienes recibieron descuentos.
""")

# ============================================================================
# DASHBOARD ESTÁTICO CON TKINTER
# ============================================================================
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# esto es para integrar matplotlib en tkinter
def mostrar_dashboard(df, feature_importance, accuracy,
                      recompra_con_promo, con_promo,
                      recompra_sin_promo, sin_promo):
    root = tk.Tk()
    root.title("Dashboard de Recompra - Campaña de Marketing")
    root.geometry("1200x700")
    root.configure(bg="#f5f5f5")

    titulo = tk.Label(root,
                      text="📊 Dashboard Ejecutivo - Recompra de Clientes",
                      font=("Segoe UI", 18, "bold"),
                      bg="#f5f5f5", fg="#333")
    titulo.pack(pady=10)

    frame_graficos = ttk.Frame(root)
    frame_graficos.pack(pady=10, padx=10)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    fig.tight_layout(pad=3)

    # Gráfico 1: Efectividad de promociones
    tasas = pd.DataFrame({
        'Categoría': ['Con Promoción', 'Sin Promoción'],
        'Tasa de Recompra (%)': [
            recompra_con_promo / len(con_promo) * 100,
            recompra_sin_promo / len(sin_promo) * 100
        ]
    })
    sns.barplot(x='Categoría', y='Tasa de Recompra (%)',
                data=tasas, palette=['#4ecdc4', '#ff6b6b'], ax=axes[0])
    axes[0].set_title("Efectividad de Promociones", fontsize=11)
    for i, v in enumerate(tasas['Tasa de Recompra (%)']):
        axes[0].text(i, v + 1, f"{v:.1f}%", ha='center', fontsize=9)

    # Gráfico 2: Variables más importantes
    top_features = feature_importance.head(5)
    sns.barplot(x='Importancia', y='Variable',
                data=top_features, ax=axes[1], palette="viridis")
    axes[1].set_title("Variables Más Importantes", fontsize=11)

    # Gráfico 3: Distribución de recompra
    recompra_counts = df['Recompra'].value_counts()
    axes[2].pie(recompra_counts,
                labels=['No Recompra', 'Recompra'],
                autopct='%1.1f%%',
                colors=['#ff6b6b', '#4ecdc4'],
                startangle=90)
    axes[2].set_title("Distribución General", fontsize=11)

    # Integrar figura en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame_graficos)
    canvas.draw()
    canvas.get_tk_widget().pack()

    # Bloque de métricas
    texto_metricas = f"""
🎯 PRECISIÓN DEL MODELO: {accuracy*100:.2f} %

📈 Variables Clave:
• {feature_importance.iloc[0]['Variable']}
• {feature_importance.iloc[1]['Variable']}
• {feature_importance.iloc[2]['Variable']}

💡 Conclusión:
El modelo predice la recompra con buena precisión
en base a promociones, ingresos y historial de compras.
"""
    lbl_metricas = tk.Label(root, text=texto_metricas,
                            font=("Consolas", 11),
                            bg="#fff8e1", justify="left",
                            anchor="w", relief="solid",
                            padx=10, pady=10)
    lbl_metricas.pack(fill="x", padx=20, pady=10)

    btn_salir = tk.Button(root, text="Cerrar Dashboard",
                          command=root.destroy,
                          bg="#ff6b6b", fg="white",
                          font=("Segoe UI", 11, "bold"),
                          relief="flat", padx=15, pady=5)
    btn_salir.pack(pady=10)

    root.mainloop()

# === LLAMAR AL DASHBOARD ===
plt.close('all')
mostrar_dashboard(df, feature_importance, accuracy,
                  recompra_con_promo, con_promo,
                  recompra_sin_promo, sin_promo)
