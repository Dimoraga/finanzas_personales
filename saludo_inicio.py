import tkinter as tk

def mostrar_pantalla_inicio(callback):
    """
    Muestra una pantalla de bienvenida con un botón "Comenzar".

    Args:
        callback (function): La función a llamar cuando se presiona el botón "Comenzar".
    """
    ventana = tk.Tk()
    ventana.title("Bienvenido Gestor_Finanzas 1.0")
    ventana.geometry("600x300")

    label_saludo = tk.Label(ventana, text="Bienvenido a tu Gestor de Finanzas", font=("Arial", 14))
    label_saludo.pack(pady=20)

    def on_comenzar():
        ventana.destroy()
        callback()

    boton_comenzar = tk.Button(ventana, text="Comenzar", command=on_comenzar, font=("Arial", 14))
    boton_comenzar.pack(pady=20)

    ventana.mainloop()

if __name__ == '__main__':
    # Esto es para probar la pantalla de inicio de forma independiente
    def test_callback():
        print("Botón 'Comenzar' presionado. Aquí se iniciaría la aplicación principal.")
    
    mostrar_pantalla_inicio(test_callback)
