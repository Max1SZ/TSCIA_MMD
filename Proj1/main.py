from functions import *

#-----------------
# Menú simple
while True:
    print("\n--- MENÚ ---\n\
|  1. Insertar uno o varios CSVs\n\
|  2. Checar un CSV\n\
|  3. Añadir datos a un CSV\n\
|  4. Eliminar celda\n\
|  5. Modificar un CSV\n\
| 6. Guardar todos los cambios\n\
| 7. Subir datos a SQL\n\
| 8. Unificar tablas\n\
| 9. Reportes\n\
| 0. Salir")

    opcion = input("Elige una opción: ")
    #add_row_csv
    if opcion == "1":
        cargar_csv()
    elif opcion == "2":
        check_csv()
    elif opcion == "3":
        add_row_csv()
    elif opcion == "4":
        delete_row_csv()
    elif opcion == "5":
        modify_csv()
    elif opcion == "6":
        save_all_csvs()
    elif opcion == "7":
        upload_to_sql()
    elif opcion == "8":
        unify_tables()
    elif opcion == "9":
        print("\n--- REPORTES ---")
        print("1. Ranking clientes")
        print("2. Ticket promedio")
        print("3. Facturas más altas")
        print("4. Ventas por mes")
        print("5. Producto más vendido")
        print("6. Ventas por rubro")
        print("7. Gráfico ventas mensuales")
        print("8. Top productos facturación")
        sub = input("Elige reporte: ")
        if sub == "1": ranking()
        elif sub == "2": ticket_promedio()
        elif sub == "3": top_facturas()
        elif sub == "4": ventas_por_mes()
        elif sub == "5": top_prods()
        elif sub == "6": det_rubro()
        elif sub == "7": grafico_ventas_mensuales()
        elif sub == "8": fac_prod()
        else: print("Opción inválida")
    elif opcion == "0":
        print("👋 Saliendo del programa...")
        break
    else:
        print("Opción no válida")