import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import font as tkFont

# Paletas de color
paleta_dia = {
    'ventana_bg': '#F8FAFC',
    'frame_bg': '#FFFFFF',
    'frame_border': '#E2E8F0',
    'boton_bg': '#3B82F6',
    'boton_hover': '#2563EB',
    'boton_fg': '#FFFFFF',
    'texto_etiquetas_fg': '#1E293B',
    'etiqueta_bg': '#F1F5F9',
    'valor_bg': '#FFFFFF',
    'valor_fg': '#0F172A',
    'entrada_bg': '#FFFFFF',
    'entrada_border': '#CBD5E1',
    'entrada_focus': '#3B82F6',
    'header_bg': '#EFF6FF',
    'header_fg': '#1E40AF'
}

paleta_noche = {
    'ventana_bg': '#0F172A',
    'frame_bg': '#1E293B',
    'frame_border': '#334155',
    'boton_bg': '#3B82F6',
    'boton_hover': '#2563EB',
    'boton_fg': '#FFFFFF',
    'texto_etiquetas_fg': '#F1F5F9',
    'etiqueta_bg': '#334155',
    'valor_bg': '#0F172A',
    'valor_fg': '#F8FAFC',
    'entrada_bg': '#334155',
    'entrada_border': '#475569',
    'entrada_focus': '#60A5FA',
    'header_bg': '#1E293B',
    'header_fg': '#60A5FA'
}

modo_noche = False
loading_label = None
loading_animando = False

# Funciones de UI
def aplicar_paleta(p):
    ventana.config(bg=p['ventana_bg'])
    main_frame.config(bg=p['ventana_bg'])
    header_frame.config(bg=p['ventana_bg'])
    input_frame.config(bg=p['ventana_bg'])
    frame_interior.config(bg=p['ventana_bg'])
    titulo_label.config(bg=p['ventana_bg'], fg=p['texto_etiquetas_fg'])
    subtitulo_label.config(bg=p['ventana_bg'], fg=p['texto_etiquetas_fg'])
    toggle_frame.config(bg=p['ventana_bg'])
    toggle_label.config(bg=p['ventana_bg'], fg=p['texto_etiquetas_fg'])
    check.config(bg=p['ventana_bg'], fg=p['texto_etiquetas_fg'], selectcolor=p['frame_bg'])
    label_entrada.config(bg=p['ventana_bg'], fg=p['texto_etiquetas_fg'])
    entrada_simbolo.config(bg=p['entrada_bg'], fg=p['valor_fg'], insertbackground=p['valor_fg'])
    boton_info.config(bg=p['boton_bg'], fg=p['boton_fg'])
    for w in frame_interior.winfo_children():
        if isinstance(w, tk.Label):
            if 'header' in w.winfo_name(): w.config(bg=p['header_bg'], fg=p['header_fg'])
            elif 'valor' in w.winfo_name(): w.config(bg=p['valor_bg'], fg=p['valor_fg'])
            elif 'etiqueta' in w.winfo_name(): w.config(bg=p['etiqueta_bg'], fg=p['texto_etiquetas_fg'])
        elif isinstance(w, tk.Frame):
            w.config(bg=p['frame_bg'])

def alternar_modo():
    global modo_noche
    modo_noche = var.get() == 1
    aplicar_paleta(paleta_noche if modo_noche else paleta_dia)

def on_button_hover(e):
    p = paleta_noche if modo_noche else paleta_dia
    boton_info.config(bg=p['boton_hover'])

def on_button_leave(e):
    p = paleta_noche if modo_noche else paleta_dia
    boton_info.config(bg=p['boton_bg'])

def on_entry_click(e):
    if entrada_simbolo.get() == "Stock Symbol":
        entrada_simbolo.delete(0, "end")
        p = paleta_noche if modo_noche else paleta_dia
        entrada_simbolo.config(fg=p['texto_etiquetas_fg'])

def mostrar_loading():
    global loading_label, loading_animando
    p = paleta_noche if modo_noche else paleta_dia
    loading_label = tk.Label(frame_interior, text="⏳ Loading...", font=font_normal, fg=p['texto_etiquetas_fg'], bg=p['ventana_bg'], name="loading_label")
    loading_label.grid(row=0, column=0, columnspan=4, pady=40)
    loading_animando = True
    animar_loading(0)

def animar_loading(i):
    if not loading_animando: return
    puntos = "." * (i % 4)
    try:
        loading_label.config(text=f"⏳ Loading{puntos}")
        ventana.after(500, lambda: animar_loading(i + 1))
    except: pass

def ocultar_loading():
    global loading_label, loading_animando
    loading_animando = False
    if loading_label:
        loading_label.destroy()
        loading_label = None

def obtener_info():
    simbolo = entrada_simbolo.get()
    url = f'https://finance.yahoo.com/quote/{simbolo}'
    if simbolo == "Stock Symbol" or not simbolo:
        messagebox.showwarning("⚠️ Warning", "Please enter a stock symbol")
        return

    headers = {'User-Agent': 'Mozilla/5.0'}

    for w in frame_interior.winfo_children():
        w.destroy()
    mostrar_loading()
    ventana.config(cursor="wait")
    boton_info.config(state="disabled")
    ventana.update_idletasks()

    try:
        html = requests.get(url, headers=headers)
        soup = BeautifulSoup(html.content, 'lxml')
        info = soup.find_all("section", {"class": "yf-4vs57a"})[0]
        titulo = info.find("h1").text
        precio = info.find("span", {"class": "yf-ipw1h0"}).text

        ocultar_loading()
        ventana.config(cursor="")
        boton_info.config(state="normal")

        p = paleta_noche if modo_noche else paleta_dia
        header_frame = tk.Frame(frame_interior, relief="solid", bd=2, padx=20, pady=15, bg=p['header_bg'], name="header_frame")
        header_frame.grid(row=0, column=0, columnspan=4, pady=(0, 20), sticky="ew")
        tk.Label(header_frame, text=f"📊 {titulo}", font=font_titulo, bg=p['header_bg'], fg=p['header_fg'], name="header_titulo").pack(anchor="w")
        tk.Label(header_frame, text=f"💰 ${precio}", font=font_subtitulo, bg=p['header_bg'], fg=p['header_fg'], name="header_precio").pack(anchor="w", pady=(5, 0))

        ul = soup.find("ul", {"class": "yf-1jj98ts"})
        if not ul:
            messagebox.showerror("❌ Error", "Could not find stock data list.")
            return
        items = ul.find_all("li")
        tk.Label(frame_interior, text="📈 Detailed Stock Information", font=font_subtitulo, bg=p['ventana_bg'], fg=p['texto_etiquetas_fg']).grid(row=1, column=0, columnspan=4, pady=(10, 15), sticky="w")

        for i, li in enumerate(items):
            spans = li.find_all("span")
            if len(spans) >= 2:
                nombre = spans[0].text.strip()
                valor = spans[1].text.strip()
                fila = (i // 2) + 2
                columna = i % 2
                agregar_a_tabla(nombre, valor, fila, columna)
    except Exception as e:
        ocultar_loading()
        ventana.config(cursor="")
        boton_info.config(state="normal")
        messagebox.showerror("❌ Error", f"An error occurred: {e}")

def agregar_a_tabla(nombre, valor, fila, columna):
    p = paleta_noche if modo_noche else paleta_dia
    item = tk.Frame(frame_interior, relief="solid", bd=1, padx=15, pady=10, bg=p['frame_bg'])
    item.grid(row=fila, column=columna * 2, columnspan=2, sticky="ew", padx=5, pady=3)
    tk.Label(item, text=f"{nombre}:", font=font_etiqueta, anchor="w", name=f"etiqueta_{fila}_{columna}", bg=p['etiqueta_bg'], fg=p['texto_etiquetas_fg']).pack(fill="x", pady=(0, 3))
    tk.Label(item, text=valor, font=font_valor, anchor="w", name=f"valor_{fila}_{columna}", bg=p['valor_bg'], fg=p['valor_fg']).pack(fill="x")

ventana = tk.Tk()
ventana.geometry("1000x700")
ventana.title("📈 InfoStock Pro")
ventana.minsize(800, 600)

# Centrar
ventana.update_idletasks()
x = (ventana.winfo_screenwidth() // 2) - 500
y = (ventana.winfo_screenheight() // 2) - 350
ventana.geometry(f"1000x700+{x}+{y}")

# Fuentes
font_titulo = tkFont.Font(family="Segoe UI", size=18, weight="bold")
font_subtitulo = tkFont.Font(family="Segoe UI", size=14, weight="bold")
font_normal = tkFont.Font(family="Segoe UI", size=11)
font_entrada = tkFont.Font(family="Segoe UI", size=14)
font_boton = tkFont.Font(family="Segoe UI", size=12, weight="bold")
font_etiqueta = tkFont.Font(family="Segoe UI", size=10, weight="bold")
font_valor = tkFont.Font(family="Segoe UI", size=10)

main_frame = tk.Frame(ventana, padx=30, pady=20)
main_frame.pack(fill="both", expand=True)
header_frame = tk.Frame(main_frame)
header_frame.pack(fill="x", pady=(0, 20))

titulo_label = tk.Label(header_frame, text="📈 InfoStock Pro", font=font_titulo)
titulo_label.pack(side="left")
subtitulo_label = tk.Label(header_frame, text="Real-time Stock Market Data", font=font_normal)
subtitulo_label.pack(side="left", padx=(15, 0))

toggle_frame = tk.Frame(header_frame)
toggle_frame.pack(side="right")
toggle_label = tk.Label(toggle_frame, text="🌙 Dark Mode", font=font_normal)
toggle_label.pack(side="right", padx=(0, 10))
var = tk.IntVar()
check = tk.Checkbutton(toggle_frame, variable=var, onvalue=1, offvalue=0, command=alternar_modo)
check.pack(side="right")

ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=(0, 20))
input_frame = tk.Frame(main_frame)
input_frame.pack(fill="x", pady=(0, 20))
label_entrada = tk.Label(input_frame, text="Enter Stock Symbol (e.g., AAPL, GOOGL):", font=font_normal)
label_entrada.pack(anchor="w", pady=(0, 8))

entry_button_frame = tk.Frame(input_frame)
entry_button_frame.pack(fill="x")
entrada_simbolo = tk.Entry(entry_button_frame, width=25, font=font_entrada, relief="solid", bd=2)
entrada_simbolo.insert(0, "Stock Symbol")
entrada_simbolo.bind('<FocusIn>', on_entry_click)
entrada_simbolo.bind('<Return>', lambda e: obtener_info())
entrada_simbolo.pack(side="left", padx=(0, 15), ipady=8)

boton_info = tk.Button(entry_button_frame, text="🔍 Get Stock Info", font=font_boton, relief="flat", bd=0, padx=25, pady=10, cursor="hand2", command=obtener_info)
boton_info.pack(side="left")
boton_info.bind("<Enter>", on_button_hover)
boton_info.bind("<Leave>", on_button_leave)

ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=(20, 20))
canvas_frame = tk.Frame(main_frame)
canvas_frame.pack(fill="both", expand=True)
canvas = tk.Canvas(canvas_frame, highlightthickness=0)
scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
frame_interior = tk.Frame(scrollable_frame, padx=20, pady=20)
frame_interior.pack(fill="both", expand=True)
frame_interior.grid_columnconfigure(0, weight=1)
frame_interior.grid_columnconfigure(1, weight=1)
frame_interior.grid_columnconfigure(2, weight=1)
frame_interior.grid_columnconfigure(3, weight=1)
tk.Label(frame_interior, text="💡 Enter a stock symbol above to get started\n\nPopular symbols: AAPL, GOOGL, MSFT, TSLA, AMZN, META", font=font_normal, justify="center").grid(row=0, column=0, columnspan=4, pady=50)

aplicar_paleta(paleta_dia)
ventana.mainloop()