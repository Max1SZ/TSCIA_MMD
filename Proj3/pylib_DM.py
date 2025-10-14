import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class DashboardCSV:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard CSV")
        self.root.geometry("700x400")

        # Variables principales
        self.df = None  # DataFrame con los datos del CSV
        self.mejor_comb = None  # Combinación automática (columna categórica, numérica, datos agrupados)

        self._crear_interfaz()  # Inicializa toda la interfaz gráfica

    def _crear_interfaz(self):
        """Crea toda la estructura de pestañas y botones principales."""
        
        # Botón para cargar el CSV
        tk.Button(self.root, text="Cargar CSV", command=self.cargar_archivo,
                  bg='#4CAF50', fg='white', font=('Arial', 12), padx=20, pady=10).pack(pady=10)

        # Contenedor de pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear cada pestaña
        self._crear_tab_preview()        # Vista previa del CSV
        self._crear_tab_automatico()     # Análisis automático
        self._crear_tab_personalizado()  # Análisis manual
        self._crear_tab_exportar()       # Exportar a Excel

    def _crear_tab_preview(self):
        """Pestaña 1: muestra los primeros registros del CSV en texto plano."""
        self.tab_preview = tk.Frame(self.notebook)
        self.notebook.add(self.tab_preview, text="Vista Previa")

        self.text_preview = tk.Text(self.tab_preview, wrap=tk.NONE)
        self.text_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrolls
        tk.Scrollbar(self.tab_preview, orient=tk.VERTICAL, command=self.text_preview.yview).pack(side=tk.RIGHT, fill=tk.Y)
        tk.Scrollbar(self.tab_preview, orient=tk.HORIZONTAL, command=self.text_preview.xview).pack(side=tk.BOTTOM, fill=tk.X)

    def _crear_tab_automatico(self):
        """Pestaña 2: análisis automático de las columnas más relevantes."""
        self.tab_auto = tk.Frame(self.notebook)
        self.notebook.add(self.tab_auto, text="Análisis Automático")

        # Texto de ayuda / resultado
        self.label_info = tk.Label(self.tab_auto, text="Carga un CSV para ver el análisis", font=('Arial', 12))
        self.label_info.pack(pady=10)

        # Slider para top N
        frame_controls = tk.Frame(self.tab_auto)
        frame_controls.pack(pady=10)
        tk.Label(frame_controls, text="Top N:").pack(side=tk.LEFT, padx=5)
        self.slider_top = tk.Scale(frame_controls, from_=5, to=20, orient=tk.HORIZONTAL,
                                   command=self.actualizar_grafico)
        self.slider_top.set(10)
        self.slider_top.pack(side=tk.LEFT)

        # Contenedor del gráfico automático
        self.canvas_frame = tk.Frame(self.tab_auto)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

    def _crear_tab_personalizado(self):
        """Pestaña 3: permite al usuario seleccionar columnas y tipo de agregación."""
        self.tab_custom = tk.Frame(self.notebook)
        self.notebook.add(self.tab_custom, text="Análisis Personalizado")

        frame = tk.Frame(self.tab_custom)
        frame.pack(pady=20)

        # Combos para seleccionar columnas
        self.combo_cat = self._crear_combo(frame, "Columna Categórica:", 0)
        self.combo_num = self._crear_combo(frame, "Columna Numérica:", 1)
        self.combo_agg = self._crear_combo(frame, "Agregación:", 2,
                                           ['Suma', 'Promedio', 'Conteo', 'Máximo', 'Mínimo'])
        self.combo_agg.set('Suma')

        # Botón para analizar personalizado
        tk.Button(frame, text="Analizar", command=self.analizar_custom,
                  bg='#2196F3', fg='white', padx=15, pady=5).grid(row=3, column=0, columnspan=2, pady=10)

        # Contenedor para el gráfico personalizado
        self.canvas_custom_frame = tk.Frame(self.tab_custom)
        self.canvas_custom_frame.pack(fill=tk.BOTH, expand=True)

    def _crear_combo(self, frame, texto, fila, valores=None):
        """Crea un combo box con etiqueta."""
        tk.Label(frame, text=texto).grid(row=fila, column=0, padx=5, pady=5)
        combo = ttk.Combobox(frame, width=25, values=valores or [])
        combo.grid(row=fila, column=1, padx=5, pady=5)
        return combo

    def _crear_tab_exportar(self):
        """Pestaña 4: permite exportar análisis a Excel con gráfico incluido."""
        self.tab_export = tk.Frame(self.notebook)
        self.notebook.add(self.tab_export, text="Exportar")

        frame = tk.Frame(self.tab_export)
        frame.place(relx=0.5, rely=0.5, anchor='center')

        self.label_export = tk.Label(frame, text="Carga un CSV primero", font=('Arial', 12))
        self.label_export.pack(pady=20)

        # Botón para exportar
        self.btn_export = tk.Button(frame, text="Exportar a Excel", command=self.exportar,
                                    bg='#FF9800', fg='white', padx=20, pady=10, state='disabled')
        self.btn_export.pack(pady=10)

    def cargar_archivo(self):
        """Carga un archivo CSV y actualiza todas las pestañas."""
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path: return

        try:
            self.df = pd.read_csv(path)
            self.text_preview.delete('1.0', tk.END)
            self.text_preview.insert('1.0', self.df.head(50).to_string())

            self.analizar_automatico()
            self._actualizar_combos()
            self.btn_export.config(state='normal')

            messagebox.showinfo("Cargado", f"{len(self.df)} filas cargadas.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def analizar_automatico(self):
        """Encuentra automáticamente la mejor combinación categórica-numérica."""
        num_cols = self.df.select_dtypes(include='number').columns
        cat_cols = self.df.select_dtypes(include='object').columns

        max_var = 0
        self.mejor_comb = None

        for cat in cat_cols:
            for num in num_cols:
                try:
                    agrupado = self.df.groupby(cat)[num].sum().sort_values(ascending=False)
                    var = agrupado.var()
                    if var > max_var:
                        max_var = var
                        self.mejor_comb = (cat, num, agrupado)
                except:
                    pass

        if self.mejor_comb:
            cat, num, _ = self.mejor_comb
            self.label_info.config(text=f"Mejor combinación: {cat} vs {num}")
            self.label_export.config(text=f"Exportará: {cat} vs {num}")
            self.actualizar_grafico()

    def actualizar_grafico(self, event=None):
        """Actualiza el gráfico automático según el Top N."""
        self._generar_grafico(self.canvas_frame, *self.mejor_comb, self.slider_top.get())

    def _actualizar_combos(self):
        """Llena los combos de columnas en el análisis personalizado."""
        self.combo_cat['values'] = list(self.df.select_dtypes(include='object').columns)
        self.combo_num['values'] = list(self.df.select_dtypes(include='number').columns)

        if self.combo_cat['values']:
            self.combo_cat.current(0)
        if self.combo_num['values']:
            self.combo_num.current(0)

    def analizar_custom(self):
        """Genera un gráfico con la combinación elegida por el usuario."""
        if self.df is None: return

        cat, num = self.combo_cat.get(), self.combo_num.get()
        agg_map = {
            'Suma': 'sum', 'Promedio': 'mean', 'Conteo': 'count',
            'Máximo': 'max', 'Mínimo': 'min'
        }
        agg_func = agg_map.get(self.combo_agg.get(), 'sum')

        try:
            datos = self.df.groupby(cat)[num].agg(agg_func).sort_values(ascending=False).head(10)
            self._generar_grafico(self.canvas_custom_frame, cat, num, datos)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _generar_grafico(self, frame, cat, num, datos, top_n=None):
        """Crea un gráfico de barras y lo muestra en el frame dado."""
        for widget in frame.winfo_children():
            widget.destroy()

        if top_n: datos = datos.head(top_n)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(datos.index, datos.values)
        ax.set_title(f"{cat} vs {num}", fontsize=12)
        ax.set_xticklabels(datos.index, rotation=45, ha='right')
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def exportar(self):
        """Exporta los datos y el gráfico automático a un archivo Excel."""
        if not self.mejor_comb: return

        path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if not path: return

        try:
            cat, num, datos = self.mejor_comb
            top = datos.head(10)
            png_path = path.replace('.xlsx', '_grafico.png')

            # Crear y guardar gráfico como imagen
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(top.index, top.values, color='skyblue', edgecolor='navy')
            ax.set_title(f"Top 10: {cat} vs {num}")
            ax.set_xticklabels(top.index, rotation=45, ha='right')
            plt.tight_layout()
            fig.savefig(png_path, dpi=150)
            plt.close()

            # Escribir Excel con gráfico insertado
            with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
                self.df.to_excel(writer, sheet_name='Datos', index=False)
                top.reset_index().to_excel(writer, sheet_name='Análisis', index=False)
                writer.sheets['Análisis'].insert_image('D2', png_path)

            messagebox.showinfo("Exportado", f"Excel y gráfico guardados:\n✓ {os.path.basename(path)}\n✓ {os.path.basename(png_path)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# Punto de entrada principal
if __name__ == "__main__":
    root = tk.Tk()
    DashboardCSV(root)
    root.mainloop()
