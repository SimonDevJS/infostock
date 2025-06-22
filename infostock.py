import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox


# Paleta de colores para día
paleta_dia = {
    'ventana_bg': '#E3F2FD',
    'frame_bg': '#F9FAFB',
    'boton_bg': '#007BFF',
    'boton_fg': 'white',
    'texto_etiquetas_fg': '#333333',
    'etiqueta_bg': '#DDEAF6',
    'valor_bg': '#FFFFFF',
    'valor_fg': '#333333'
}

# Paleta de colores para noche
paleta_noche = {
    'ventana_bg': '#1C1C1E',
    'frame_bg': '#2C2C2E',
    'boton_bg': '#0A84FF',
    'boton_fg': 'white',
    'texto_etiquetas_fg': '#F5F5F5',
    'etiqueta_bg': '#4D4D4D',
    'valor_bg': '#000000',
    'valor_fg': '#FFFFFF'
}

# Establecer modo noche
modo_noche = False

# Funcion para aplicar la paleta dia noche
def aplicar_paleta(paleta):
    ventana.config(bg=paleta['ventana_bg'])
    frame_interior.config(bg=paleta['frame_bg'])
    boton_info.config(bg=paleta['boton_bg'], fg=paleta['boton_fg'])
    entrada_simbolo.config(bg=paleta['valor_bg'], fg=paleta['valor_fg'])

    # actualizar los widgets dentro del grame
    for widget in frame_interior.winfo_children():
        if isinstance(widget, tk.Label):
            if 'valor' in widget.winfo_name():
                widget.configure(bg=paleta['valor_bg'], fg=paleta['valor_fg'])
            else:
                widget.configure(bg=paleta['etiqueta_bg'], fg=paleta['texto_etiquetas_fg'])

# Funcion para alternar entre modos
def alternar_modo():
    global modo_noche
    if var.get() == 1:
        modo_noche = True
        aplicar_paleta(paleta_noche)
    else:
        modo_noche = False
        aplicar_paleta(paleta_dia)

# Funcion para borrar el placeholder del Entry
def on_entry_click(event):
    if entrada_simbolo.get() == "Stock Symbol":
        entrada_simbolo.delete(0, "end")
        entrada_simbolo.config(fg=paleta_dia['texto_etiquetas_fg'] if not modo_noche else paleta_noche['texto_etiquetas_fg'])

# Función para extraerdatos
def obtener_info():
    simbolo = entrada_simbolo.get()
    url = 'https://finance.yahoo.com/quote/' + simbolo
    if simbolo == "Stock Symbol" or not simbolo:
        messagebox.showwarning("Warning", "Please enter a stock symbol")
        return

    encabezados = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'}

    try:
        html = requests.get(url, headers=encabezados)

        # Crear la sopa
        sopa = BeautifulSoup(html.content, 'lxml')

        # Extraer información de la sopa
        info_encabezado = sopa.find_all("section", {"class": "yf-4vs57a"})[0]
        titulo_simbolo = info_encabezado.find("h1").text
        precio_actual = info_encabezado.find("span", {"class": "yf-ipw1h0"}).text

        # Limpiar el Frame interior
        for widget in frame_interior.winfo_children():
            widget.destroy()

        # Mostrar el encabezado con el nombre y el precio del stock
        color_texto = paleta_dia['texto_etiquetas_fg'] if not modo_noche else paleta_noche['texto_etiquetas_fg']
        color_encabezado = paleta_dia['etiqueta_bg'] if not modo_noche else paleta_noche['etiqueta_bg']
        encabezado = f"{titulo_simbolo} - {precio_actual}"
        encabezado_etiqueta = tk.Label(frame_interior, text=encabezado, font=("Helvetica", 16, "bold"),bg=color_encabezado, fg=color_texto)
        encabezado_etiqueta.grid(row=0, column=0, columnspan=4, pady=10, sticky="n")

        # Extraer ul
        ul_element = sopa.find("ul", {"class": "yf-1jj98ts"})
        if not ul_element:
            messagebox.showerror("Error", "Could not find stock data list.")
            return

        lista_items = ul_element.find_all("li")

        for indice_li, li in enumerate(lista_items):
            spans = li.find_all("span")
            if len(spans) >= 2:
                nombre = spans[0].text.strip()
                valor = spans[1].text.strip()
                fila = (indice_li // 2) + 1
                columna = indice_li % 2
                agregar_a_tabla(nombre, valor, fila, columna)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"The information could not be obtained {e}")

# Funcion para agregar los registros a la tabla
def agregar_a_tabla(nombre, valor, fila, columna):
    color_etiqueta = paleta_dia['etiqueta_bg'] if not modo_noche else paleta_noche['etiqueta_bg']
    color_valor = paleta_dia['valor_bg'] if not modo_noche else paleta_noche['valor_bg']
    color_texto_valor = paleta_dia['valor_fg'] if not modo_noche else paleta_noche['valor_fg']
    color_texto = paleta_dia['texto_etiquetas_fg'] if not modo_noche else paleta_noche['texto_etiquetas_fg']

    etiqueta_widget = tk.Label(frame_interior,
                               text=nombre + ":",
                               font=("Helvetica", 10),
                               anchor="w",
                               name=f"etiqueta_{fila}_{columna}",
                               bg=color_etiqueta,
                               fg=color_texto)
    etiqueta_widget.grid(row=fila, column=columna * 2, sticky="w", padx=10, pady=2)

    valor_widget = tk.Label(frame_interior,
                            text=valor,
                            font=("Helvetica", 10),
                            anchor="w",
                            name=f"valor_{fila}_{columna}",
                            bg=color_valor,
                            fg=color_texto_valor)
    valor_widget.grid(row=fila, column=columna * 2 + 1, sticky="w", padx=10, pady=2)


ventana = tk.Tk()
ventana.geometry("900x400")
ventana.title("InfoStock App")
ruta_icono = "C:/Users/Simon/Desktop/python_aplicado/infostock/infostock.ico"
ventana.iconbitmap(ruta_icono)

# Caja de texto para ingresar el simbolo
entrada_simbolo = tk.Entry(ventana,
                           width=20,
                           font=("Helvetica", 16,),
                           fg="grey")
entrada_simbolo.insert(0, "Stock Symbol")
entrada_simbolo.bind('<FocusIn>', on_entry_click)
entrada_simbolo.pack(pady=20)

# Boton para obtener informacion
boton_info = tk.Button(ventana,
                       text="Get Info",
                       width=20,
                       font=("Helvetica", 16,),
                       relief="flat",
                       command=obtener_info)
boton_info.pack(pady=3)

# Vaariable para manejar el estado del checkbutton
var = tk.IntVar()

# Checkbutton para activar modo noche
check = tk.Checkbutton(ventana,
                       text="Night Mode",
                       variable=var,
                       onvalue=1,
                       offvalue=0,
                       command=alternar_modo)

check.place(relx=0.9, rely=0.05, anchor="ne")

# Frame para el área de resultados
frame_interior = tk.Frame(ventana)
frame_interior.pack(fill="both", padx=10, pady=10, expand=True)

frame_interior.grid_columnconfigure(0, weight=1)
frame_interior.grid_columnconfigure(1, weight=1)
frame_interior.grid_columnconfigure(2, weight=1)
frame_interior.grid_columnconfigure(3, weight=1)


# Iniciar con la paleta dia
aplicar_paleta(paleta_dia)

# Iniciar el loop de la ventana
ventana.mainloop()
