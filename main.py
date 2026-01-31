#Programa para registrar finanzas personales.

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
from saludo_inicio import mostrar_pantalla_inicio
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import os
from datetime import datetime

# Diccionario para guardar los movimientos por mes ('YYYY-MM')
finanzas = {}
mes_actual = None
ventana_principal = None
label_meta_ahorro = None
label_progreso_ahorro = None

# Gastos frecuentes predeterminados
gastos_frecuentes_default = [
    "Cuenta de Luz",
    "Cuenta de Agua",
    "Pago de Arriendo",
    "Cuenta de Internet"
]

def cargar_datos():
    global finanzas
    try:
        with open("finanzas.json", "r") as f:
            finanzas = json.load(f)
    except FileNotFoundError:
        finanzas = {}

def guardar_datos():
    with open("finanzas.json", "w") as f:
        json.dump(finanzas, f, indent=4)
    if ventana_principal:
        ventana_principal.destroy()

def formatear_dinero(numero):
    """Formatea un número a un formato de dinero con puntos como separadores de miles."""
    return f"{numero:,.0f}".replace(",", ".")

def validar_fecha(fecha_str):
    """Valida que la fecha tenga el formato DD-MM-YYYY."""
    try:
        partes = fecha_str.split("-")
        if len(partes) != 3:
            return False
        dia, mes, anio = partes
        if len(dia) != 2 or len(mes) != 2 or len(anio) != 4:
            return False
        dia_int = int(dia)
        mes_int = int(mes)
        anio_int = int(anio)
        if dia_int < 1 or dia_int > 31:
            return False
        if mes_int < 1 or mes_int > 12:
            return False
        if anio_int < 1900 or anio_int > 2100:
            return False
        return True
    except ValueError:
        return False

def agregar_ingreso():
    monto_str = entry_monto.get()
    desc = entry_desc.get()
    fecha = entry_fecha.get()

    if not desc:
        messagebox.showerror("Error", "Debe ingresar una observación.")
        return
    
    if not fecha:
        messagebox.showerror("Error", "Debe ingresar una fecha.")
        return
    
    if not validar_fecha(fecha):
        messagebox.showerror("Error", "La fecha debe tener el formato DD-MM-YYYY (ej: 31-01-2026)")
        return

    if monto_str.isdigit():
        monto = int(monto_str)
        finanzas[mes_actual].append(("Ingreso", monto, desc, fecha))
        actualizar_balance()
        
        total_ingresos = sum(m[1] for m in finanzas[mes_actual] if m[0] == "Ingreso")
        messagebox.showinfo("Ingresos del Mes", f"Tus ingresos del mes en curso ascienden a ${formatear_dinero(total_ingresos)}.")

        entry_monto.delete(0, tk.END)
        entry_desc.delete(0, tk.END)
        entry_fecha.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "El monto debe ser un número")

def agregar_gasto():
    monto_str = entry_monto.get()
    desc = entry_desc.get()
    fecha = entry_fecha.get()

    if not desc:
        messagebox.showerror("Error", "Debe ingresar una observación.")
        return
    
    if not fecha:
        messagebox.showerror("Error", "Debe ingresar una fecha.")
        return
    
    if not validar_fecha(fecha):
        messagebox.showerror("Error", "La fecha debe tener el formato DD-MM-YYYY (ej: 31-01-2026)")
        return

    if monto_str.isdigit():
        monto = int(monto_str)
        finanzas[mes_actual].append(("Gasto", -monto, desc, fecha))
        actualizar_balance()
        entry_monto.delete(0, tk.END)
        entry_desc.delete(0, tk.END)
        entry_fecha.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "El monto debe ser un número")

def agregar_ahorro():
    monto_str = entry_monto.get()
    desc = entry_desc.get()
    fecha = entry_fecha.get()

    if not desc:
        messagebox.showerror("Error", "Debe ingresar una observación.")
        return
    
    if not fecha:
        messagebox.showerror("Error", "Debe ingresar una fecha.")
        return
    
    if not validar_fecha(fecha):
        messagebox.showerror("Error", "La fecha debe tener el formato DD-MM-YYYY (ej: 31-01-2026)")
        return

    if monto_str.isdigit():
        monto = int(monto_str)
        finanzas[mes_actual].append(("Ahorro", monto, desc, fecha))
        actualizar_balance()
        entry_monto.delete(0, tk.END)
        entry_desc.delete(0, tk.END)
        entry_fecha.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "El monto debe ser un número")

def registrar_gasto_frecuente(nombre_gasto, ventana_gastos):
    """Registra un gasto frecuente pidiendo el monto y fecha al usuario."""
    monto = simpledialog.askinteger(
        "Monto",
        f"Ingrese el monto para {nombre_gasto}:",
        parent=ventana_gastos,
        minvalue=0
    )
    
    if monto is not None:
        fecha = simpledialog.askstring(
            "Fecha",
            f"Ingrese la fecha del gasto (DD-MM-YYYY):",
            parent=ventana_gastos
        )
        
        if fecha and validar_fecha(fecha):
            finanzas[mes_actual].append(("Gasto", -monto, nombre_gasto, fecha))
            actualizar_balance()
            messagebox.showinfo("Éxito", f"Gasto frecuente '{nombre_gasto}' registrado por ${formatear_dinero(monto)} el {fecha}")
        elif fecha:
            messagebox.showerror("Error", "La fecha debe tener el formato DD-MM-YYYY (ej: 31-01-2026)")
        else:
            messagebox.showerror("Error", "Debe ingresar una fecha.")

def agregar_nuevo_gasto_frecuente(ventana_gastos):
    """Permite al usuario agregar un nuevo tipo de gasto frecuente."""
    nombre = simpledialog.askstring(
        "Nuevo Gasto Frecuente",
        "Ingrese el nombre del nuevo gasto frecuente:",
        parent=ventana_gastos
    )
    
    if nombre:
        # Guardar el nuevo gasto frecuente en el diccionario de finanzas
        if "gastos_frecuentes_personalizados" not in finanzas:
            finanzas["gastos_frecuentes_personalizados"] = []
        
        if nombre not in finanzas["gastos_frecuentes_personalizados"]:
            finanzas["gastos_frecuentes_personalizados"].append(nombre)
            messagebox.showinfo("Éxito", f"Gasto frecuente '{nombre}' agregado. Cierre y vuelva a abrir esta ventana para verlo.")
        else:
            messagebox.showwarning("Advertencia", f"El gasto '{nombre}' ya existe.")

def abrir_ventana_gastos_frecuentes():
    """Abre una ventana con botones para los gastos frecuentes."""
    ventana_gastos = tk.Toplevel(ventana_principal)
    ventana_gastos.title("Gastos Frecuentes")
    ventana_gastos.geometry("400x500")
    
    # Título
    tk.Label(
        ventana_gastos,
        text="Seleccione un gasto frecuente",
        font=("Arial", 12, "bold")
    ).pack(pady=10)
    
    # Frame para los botones
    frame_botones = tk.Frame(ventana_gastos)
    frame_botones.pack(pady=10, padx=20, fill="both", expand=True)
    
    # Obtener lista completa de gastos frecuentes
    gastos_frecuentes = gastos_frecuentes_default.copy()
    if "gastos_frecuentes_personalizados" in finanzas:
        gastos_frecuentes.extend(finanzas["gastos_frecuentes_personalizados"])
    
    # Crear botones para cada gasto frecuente
    for gasto in gastos_frecuentes:
        btn = tk.Button(
            frame_botones,
            text=gasto,
            command=lambda g=gasto: registrar_gasto_frecuente(g, ventana_gastos),
            width=30,
            height=2,
            bg="#FFE4B5"
        )
        btn.pack(pady=5)
    
    # Separador
    tk.Label(ventana_gastos, text="───────────────────────").pack(pady=10)
    
    # Botón para agregar nuevo gasto frecuente
    btn_nuevo = tk.Button(
        ventana_gastos,
        text="+ Agregar Nuevo Gasto Frecuente",
        command=lambda: agregar_nuevo_gasto_frecuente(ventana_gastos),
        width=30,
        height=2,
        bg="#90EE90",
        font=("Arial", 10, "bold")
    )
    btn_nuevo.pack(pady=10)
    
    # Botón para cerrar
    btn_cerrar = tk.Button(
        ventana_gastos,
        text="Cerrar",
        command=ventana_gastos.destroy,
        width=15
    )
    btn_cerrar.pack(pady=10)

def actualizar_balance():
    ingresos = [m for m in finanzas[mes_actual] if m[0] == "Ingreso"]
    gastos = [m for m in finanzas[mes_actual] if m[0] == "Gasto"]
    ahorros = [m for m in finanzas[mes_actual] if m[0] == "Ahorro"]

    total_ingresos = sum(m[1] for m in ingresos)
    total_gastos = sum(m[1] for m in gastos) # Los gastos ya son negativos
    total_ahorros = sum(m[1] for m in ahorros)

    balance = total_ingresos + total_gastos - total_ahorros
    
    label_balance.config(text=f"Balance actual: ${formatear_dinero(balance)}")

    # Actualizar columna de ingresos
    for item in tree_ingresos.get_children():
        tree_ingresos.delete(item)
    for movimiento in ingresos:
        if len(movimiento) >= 4:
            _, monto, desc, fecha = movimiento[0], movimiento[1], movimiento[2], movimiento[3]
            tree_ingresos.insert("", tk.END, values=(fecha, f"${formatear_dinero(monto)}", desc))
        else:
            _, monto, desc = movimiento[0], movimiento[1], movimiento[2]
            tree_ingresos.insert("", tk.END, values=("-", f"${formatear_dinero(monto)}", desc))
    
    # Actualizar columna de gastos
    for item in tree_gastos.get_children():
        tree_gastos.delete(item)
    for movimiento in gastos:
        if len(movimiento) >= 4:
            _, monto, desc, fecha = movimiento[0], movimiento[1], movimiento[2], movimiento[3]
            tree_gastos.insert("", tk.END, values=(fecha, f"${formatear_dinero(abs(monto))}", desc))
        else:
            _, monto, desc = movimiento[0], movimiento[1], movimiento[2]
            tree_gastos.insert("", tk.END, values=("-", f"${formatear_dinero(abs(monto))}", desc))

    # Actualizar columna de ahorros
    for item in tree_ahorros.get_children():
        tree_ahorros.delete(item)
    for movimiento in ahorros:
        if len(movimiento) >= 4:
            _, monto, desc, fecha = movimiento[0], movimiento[1], movimiento[2], movimiento[3]
            tree_ahorros.insert("", tk.END, values=(fecha, f"${formatear_dinero(monto)}", desc))
        else:
            _, monto, desc = movimiento[0], movimiento[1], movimiento[2]
            tree_ahorros.insert("", tk.END, values=("-", f"${formatear_dinero(monto)}", desc))

    # Actualizar totales
    label_total_ingresos.config(text=f"Ingresos Totales: ${formatear_dinero(total_ingresos)}")
    label_total_gastos.config(text=f"Gastos Totales: ${formatear_dinero(abs(total_gastos))}")
    label_total_ahorros.config(text=f"Total Ahorro: ${formatear_dinero(total_ahorros)}")
    
    # Actualizar progreso de meta de ahorro
    meta_ahorro_key = f"{mes_actual}_meta_ahorro"
    if meta_ahorro_key in finanzas and finanzas[meta_ahorro_key] > 0:
        meta_ahorro = finanzas[meta_ahorro_key]
        porcentaje_cumplido = (total_ahorros / meta_ahorro) * 100
        porcentaje_faltante = 100 - porcentaje_cumplido if porcentaje_cumplido < 100 else 0
        
        if porcentaje_cumplido >= 100:
            mensaje_progreso = f"¡Felicitaciones! Has cumplido tu meta de ahorro (100%)\n¡Has ahorrado un {porcentaje_cumplido:.1f}% de tu meta!"
            color_progreso = "green"
        else:
            mensaje_progreso = f"Progreso: {porcentaje_cumplido:.1f}% cumplido | {porcentaje_faltante:.1f}% faltante\nAhorro actual: ${formatear_dinero(total_ahorros)} de ${formatear_dinero(meta_ahorro)}"
            color_progreso = "orange"
        
        label_progreso_ahorro.config(text=mensaje_progreso, fg=color_progreso)

def generar_reporte_pdf():
    """Genera un reporte PDF con todos los movimientos del mes actual."""
    try:
        # Crear nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"Reporte_Finanzas_{mes_actual}_{timestamp}.pdf"
        ruta_archivo = os.path.join(os.path.expanduser("~"), "Documents", nombre_archivo)
        
        # Crear documento PDF
        doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
        elementos = []
        
        # Estilos
        estilos = getSampleStyleSheet()
        estilo_titulo = estilos['Heading1']
        estilo_normal = estilos['Normal']
        
        # Título
        titulo = Paragraph(f"<b>Reporte de Finanzas Personales - {mes_actual}</b>", estilo_titulo)
        elementos.append(titulo)
        elementos.append(Spacer(1, 0.3*inch))
        
        # Calcular totales
        ingresos = [m for m in finanzas[mes_actual] if m[0] == "Ingreso"]
        gastos = [m for m in finanzas[mes_actual] if m[0] == "Gasto"]
        ahorros = [m for m in finanzas[mes_actual] if m[0] == "Ahorro"]
        
        total_ingresos = sum(m[1] for m in ingresos)
        total_gastos = sum(m[1] for m in gastos)
        total_ahorros = sum(m[1] for m in ahorros)
        balance = total_ingresos + total_gastos - total_ahorros
        
        # Tabla de resumen
        datos_resumen = [
            ["Concepto", "Monto"],
            ["Total Ingresos", f"${formatear_dinero(total_ingresos)}"],
            ["Total Gastos", f"${formatear_dinero(abs(total_gastos))}"],
            ["Total Ahorros", f"${formatear_dinero(total_ahorros)}"],
            ["Balance Final", f"${formatear_dinero(balance)}"]
        ]
        
        tabla_resumen = Table(datos_resumen, colWidths=[3*inch, 2*inch])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elementos.append(tabla_resumen)
        elementos.append(Spacer(1, 0.5*inch))
        
        # Detalle de Ingresos
        if ingresos:
            elementos.append(Paragraph("<b>Detalle de Ingresos:</b>", estilos['Heading2']))
            elementos.append(Spacer(1, 0.2*inch))
            
            datos_ingresos = [["Fecha", "Monto", "Observación"]]
            for movimiento in ingresos:
                if len(movimiento) >= 4:
                    _, monto, desc, fecha = movimiento[0], movimiento[1], movimiento[2], movimiento[3]
                    datos_ingresos.append([fecha, f"${formatear_dinero(monto)}", desc])
                else:
                    _, monto, desc = movimiento[0], movimiento[1], movimiento[2]
                    datos_ingresos.append(["-", f"${formatear_dinero(monto)}", desc])
            
            tabla_ingresos = Table(datos_ingresos, colWidths=[1*inch, 1.5*inch, 3.5*inch])
            tabla_ingresos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabla_ingresos)
            elementos.append(Spacer(1, 0.3*inch))
        
        # Detalle de Gastos
        if gastos:
            elementos.append(Paragraph("<b>Detalle de Gastos:</b>", estilos['Heading2']))
            elementos.append(Spacer(1, 0.2*inch))
            
            datos_gastos = [["Fecha", "Monto", "Observación"]]
            for movimiento in gastos:
                if len(movimiento) >= 4:
                    _, monto, desc, fecha = movimiento[0], movimiento[1], movimiento[2], movimiento[3]
                    datos_gastos.append([fecha, f"${formatear_dinero(abs(monto))}", desc])
                else:
                    _, monto, desc = movimiento[0], movimiento[1], movimiento[2]
                    datos_gastos.append(["-", f"${formatear_dinero(abs(monto))}", desc])
            
            tabla_gastos = Table(datos_gastos, colWidths=[1*inch, 1.5*inch, 3.5*inch])
            tabla_gastos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabla_gastos)
            elementos.append(Spacer(1, 0.3*inch))
        
        # Detalle de Ahorros
        if ahorros:
            elementos.append(Paragraph("<b>Detalle de Ahorros:</b>", estilos['Heading2']))
            elementos.append(Spacer(1, 0.2*inch))
            
            datos_ahorros = [["Fecha", "Monto", "Observación"]]
            for movimiento in ahorros:
                if len(movimiento) >= 4:
                    _, monto, desc, fecha = movimiento[0], movimiento[1], movimiento[2], movimiento[3]
                    datos_ahorros.append([fecha, f"${formatear_dinero(monto)}", desc])
                else:
                    _, monto, desc = movimiento[0], movimiento[1], movimiento[2]
                    datos_ahorros.append(["-", f"${formatear_dinero(monto)}", desc])
            
            tabla_ahorros = Table(datos_ahorros, colWidths=[1*inch, 1.5*inch, 3.5*inch])
            tabla_ahorros.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabla_ahorros)
        
        # Generar PDF
        doc.build(elementos)
        
        messagebox.showinfo("Éxito", f"Reporte generado exitosamente:\n{ruta_archivo}")
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el reporte:\n{str(e)}")

def limpiar_todo_datos():
    """Limpia todos los datos de ingresos, gastos y ahorros del mes actual después de confirmar."""
    respuesta = messagebox.askyesno(
        "Confirmar",
        "¿Está seguro que desea borrar toda la información?",
        icon='warning'
    )
    
    if respuesta:
        # Limpiar todos los movimientos del mes actual
        finanzas[mes_actual] = []
        # Actualizar la vista
        actualizar_balance()
        messagebox.showinfo("Éxito", "Toda la información ha sido eliminada.")

def abrir_ventana_principal(mes, anio):
    global mes_actual, ventana_principal, entry_monto, entry_desc, entry_fecha, label_balance
    global tree_ingresos, tree_gastos, tree_ahorros, label_total_ingresos, label_total_gastos, label_total_ahorros
    global label_meta_ahorro, label_progreso_ahorro
    
    mes_actual = f"{anio}-{mes:02d}"
    if mes_actual not in finanzas:
        finanzas[mes_actual] = []

    ventana_principal = tk.Tk()
    ventana_principal.title(f"Finanzas Personales - {mes_actual}")

    # --- Fila de entradas ---
    tk.Label(ventana_principal, text="Monto:").grid(row=0, column=0, padx=5, pady=5)
    entry_monto = tk.Entry(ventana_principal, width=15)
    entry_monto.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(ventana_principal, text="Fecha (DD-MM-YYYY):").grid(row=0, column=2, padx=5, pady=5)
    entry_fecha = tk.Entry(ventana_principal, width=15)
    entry_fecha.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(ventana_principal, text="Observaciones:").grid(row=0, column=4, padx=5, pady=5)
    entry_desc = tk.Entry(ventana_principal, width=25)
    entry_desc.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

    # --- Fila de botones ---
    btn_ingreso = tk.Button(ventana_principal, text="Ingresos de este mes", command=agregar_ingreso)
    btn_ingreso.grid(row=1, column=0, columnspan=2, pady=10)

    btn_gasto = tk.Button(ventana_principal, text="Registrar Gasto", command=agregar_gasto)
    btn_gasto.grid(row=1, column=2, columnspan=2, pady=10)

    btn_ahorro = tk.Button(ventana_principal, text="Ahorro", command=agregar_ahorro)
    btn_ahorro.grid(row=1, column=4, columnspan=2, pady=10)

    # --- Fila de Balance General ---
    label_balance = tk.Label(ventana_principal, text="Balance actual: $0", font=("Arial", 12, "bold"))
    label_balance.grid(row=2, column=0, columnspan=6, pady=5)
    
    # --- Meta de Ahorro ---
    meta_ahorro_key = f"{mes_actual}_meta_ahorro"
    if meta_ahorro_key in finanzas:
        meta_ahorro = finanzas[meta_ahorro_key]
        label_meta_ahorro = tk.Label(ventana_principal, text=f"Tu meta de ahorro de este mes es de ${formatear_dinero(meta_ahorro)}", font=("Arial", 11, "bold"), fg="blue")
        label_meta_ahorro.grid(row=3, column=0, columnspan=6, pady=5)
        
        # --- Progreso de Ahorro ---
        label_progreso_ahorro = tk.Label(ventana_principal, text="Progreso: 0% cumplido | 100% faltante", font=("Arial", 10), fg="orange")
        label_progreso_ahorro.grid(row=4, column=0, columnspan=6, pady=5)

    # --- Cabeceras de columnas ---
    tk.Label(ventana_principal, text="Ingresos", font=("Arial", 11, "bold")).grid(row=5, column=0, columnspan=2)
    tk.Label(ventana_principal, text="Gastos", font=("Arial", 11, "bold")).grid(row=5, column=2, columnspan=2)
    tk.Label(ventana_principal, text="Ahorros", font=("Arial", 11, "bold")).grid(row=5, column=4, columnspan=2)

    # --- Columnas de movimientos con Treeview (estilo Excel) ---
    # Treeview para Ingresos
    tree_ingresos = ttk.Treeview(ventana_principal, columns=("Fecha", "Monto", "Descripción"), show="headings", height=12)
    tree_ingresos.heading("Fecha", text="Fecha")
    tree_ingresos.heading("Monto", text="Monto")
    tree_ingresos.heading("Descripción", text="Descripción")
    tree_ingresos.column("Fecha", width=90, anchor="center")
    tree_ingresos.column("Monto", width=90, anchor="e")
    tree_ingresos.column("Descripción", width=150, anchor="w")
    tree_ingresos.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
    
    # Scrollbar para Ingresos
    scroll_ingresos = ttk.Scrollbar(ventana_principal, orient="vertical", command=tree_ingresos.yview)
    tree_ingresos.configure(yscrollcommand=scroll_ingresos.set)
    scroll_ingresos.grid(row=6, column=1, sticky="nse", pady=5)

    # Treeview para Gastos
    tree_gastos = ttk.Treeview(ventana_principal, columns=("Fecha", "Monto", "Descripción"), show="headings", height=12)
    tree_gastos.heading("Fecha", text="Fecha")
    tree_gastos.heading("Monto", text="Monto")
    tree_gastos.heading("Descripción", text="Descripción")
    tree_gastos.column("Fecha", width=90, anchor="center")
    tree_gastos.column("Monto", width=90, anchor="e")
    tree_gastos.column("Descripción", width=150, anchor="w")
    tree_gastos.grid(row=6, column=2, columnspan=2, padx=5, pady=5, sticky="nsew")
    
    # Scrollbar para Gastos
    scroll_gastos = ttk.Scrollbar(ventana_principal, orient="vertical", command=tree_gastos.yview)
    tree_gastos.configure(yscrollcommand=scroll_gastos.set)
    scroll_gastos.grid(row=6, column=3, sticky="nse", pady=5)

    # Treeview para Ahorros
    tree_ahorros = ttk.Treeview(ventana_principal, columns=("Fecha", "Monto", "Descripción"), show="headings", height=12)
    tree_ahorros.heading("Fecha", text="Fecha")
    tree_ahorros.heading("Monto", text="Monto")
    tree_ahorros.heading("Descripción", text="Descripción")
    tree_ahorros.column("Fecha", width=90, anchor="center")
    tree_ahorros.column("Monto", width=90, anchor="e")
    tree_ahorros.column("Descripción", width=150, anchor="w")
    tree_ahorros.grid(row=6, column=4, columnspan=2, padx=5, pady=5, sticky="nsew")
    
    # Scrollbar para Ahorros
    scroll_ahorros = ttk.Scrollbar(ventana_principal, orient="vertical", command=tree_ahorros.yview)
    tree_ahorros.configure(yscrollcommand=scroll_ahorros.set)
    scroll_ahorros.grid(row=6, column=5, sticky="nse", pady=5)

    # --- Fila de totales por columna ---
    label_total_ingresos = tk.Label(ventana_principal, text="Ingresos Totales: $0", font=("Arial", 10, "bold"))
    label_total_ingresos.grid(row=7, column=0, columnspan=2, pady=5)

    label_total_gastos = tk.Label(ventana_principal, text="Gastos Totales: $0", font=("Arial", 10, "bold"))
    label_total_gastos.grid(row=7, column=2, columnspan=2, pady=5)

    label_total_ahorros = tk.Label(ventana_principal, text="Total Ahorro: $0", font=("Arial", 10, "bold"))
    label_total_ahorros.grid(row=7, column=4, columnspan=2, pady=5)

    # --- Botón para gastos frecuentes ---
    btn_gastos_frecuentes = tk.Button(ventana_principal, text="Gastos Frecuentes", command=abrir_ventana_gastos_frecuentes, bg="#FFE4B5", font=("Arial", 10, "bold"))
    btn_gastos_frecuentes.grid(row=8, column=0, columnspan=2, pady=5, sticky="ew", padx=5)

    # --- Botón para generar reporte PDF ---
    btn_reporte = tk.Button(ventana_principal, text="Generar Reporte PDF", command=generar_reporte_pdf, bg="lightblue")
    btn_reporte.grid(row=8, column=2, columnspan=2, pady=5, sticky="ew", padx=5)
    
    # --- Botón LIMPIAR ---
    btn_limpiar = tk.Button(ventana_principal, text="LIMPIAR", command=limpiar_todo_datos, bg="#FF6B6B", fg="white", font=("Arial", 10, "bold"))
    btn_limpiar.grid(row=8, column=4, columnspan=2, pady=5, sticky="ew", padx=5)

    # --- Botón para guardar ---
    btn_guardar = tk.Button(ventana_principal, text="Guardar y Salir", command=guardar_datos, bg="#FFB6C1")
    btn_guardar.grid(row=9, column=0, columnspan=6, pady=10)

    actualizar_balance()
    ventana_principal.mainloop()

def iniciar_app_principal():
    """
    Esta función se ejecuta después de la pantalla de inicio.
    Pide al usuario el mes y el año para comenzar a registrar las finanzas.
    """
    # Usamos una ventana temporal invisible para los diálogos
    ventana_temporal = tk.Tk()
    ventana_temporal.withdraw()  # Ocultamos la ventana principal temporal
    
    ventana_temporal.minsize(700, 500)

    cargar_datos()

    try:
        anio = simpledialog.askinteger("Año", "Ingrese el año (ej: 2026):", parent=ventana_temporal, minvalue=2000, maxvalue=2100)
        if anio is None: 
            ventana_temporal.destroy()
            return
        mes = simpledialog.askinteger("Mes", "Ingrese el mes (1-12):", parent=ventana_temporal, minvalue=1, maxvalue=12)
        if mes is None: 
            ventana_temporal.destroy()
            return
        
        # Preguntar el monto que desea ahorrar este mes
        meta_ahorro = simpledialog.askinteger("Meta de Ahorro", "¿Cuál es el monto que deseas ahorrar este mes?:", parent=ventana_temporal, minvalue=0)
        if meta_ahorro is None:
            ventana_temporal.destroy()
            return
        
        # Guardar la meta de ahorro para este mes
        mes_key = f"{anio}-{mes:02d}"
        if mes_key not in finanzas:
            finanzas[mes_key] = []
        
        # Guardar la meta de ahorro como metadato (podemos usar una clave especial)
        finanzas[f"{mes_key}_meta_ahorro"] = meta_ahorro
        
        messagebox.showinfo("Meta de Ahorro", f"Tu meta de ahorro para {mes_key} es de ${formatear_dinero(meta_ahorro)}.")
        
        ventana_temporal.destroy()
        abrir_ventana_principal(mes, anio)

    except (ValueError, TypeError):
        messagebox.showerror("Error", "Entrada no válida.")
    finally:
        if ventana_temporal.winfo_exists():
            ventana_temporal.destroy()

if __name__ == "__main__":
    mostrar_pantalla_inicio(iniciar_app_principal)
