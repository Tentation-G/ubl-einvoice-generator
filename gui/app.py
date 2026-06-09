import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from datetime import datetime as dt
now = dt.now().strftime('%Y-%m-%d %H:%M:%S')

from generate_in_cn_xml_from_bdd import *

# App param
app = tk.Tk()
app.geometry("1200x600")

# Recup bdd
rows = []
cols = ["", "Doc"]
def update_data():
    global rows, cols
    rows = fetch_all_header()
    cols = fetch_all_header_columns()

    # Refresh colonnes
    all_cols = ("✓", *cols)
    tree.config(columns=all_cols)
    tree.heading("✓", text="✓")
    tree.column("✓", width=40, anchor="center")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col)

    tk.Label(frame_search, text=f"Rechercher ({cols[1]}) :").pack(side="left")
    log(f"> [INFO]        [{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] : <Data up to date>")

## == Filtre ==
# Recherche Inv/Cn
search_var = tk.StringVar()
frame_search = tk.Frame(app)
frame_search.pack(fill="x", padx=2, pady=(10, 0))
#tk.Label(frame_search, text=f"Rechercher ({cols[1]}) :").pack(side="left")
tk.Entry(frame_search, textvariable=search_var, width=30).pack(side="left", padx=8)

# Bouton refresh Data
tk.Button(frame_search, text="Rafraichir", command=update_data).pack(side="right", padx=10)

# Bouton Validation -> gen ubl
def valider():
    if not list_id:
        messagebox.showwarning("Attention", "Aucune ligne sélectionnée.")
        log(f"> [WARNING]     [{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] : Aucune ligne selectionnée", "red")
        return
    ok = messagebox.askyesno("Confirmation", f"Valider {len(list_id)} ligne(s) ?\n\n{list_id}")
    if ok:
        log(f"> [VALIDATION]  [{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] : <Génération des ULB> -> {list_id}")
        for progress in gen_all_doc_in_list(list_id):
            log(f"> [GENERATION]  [{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] : {progress}", "blue")
            app.update()
        log(f"> [INFO]        [{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] : <DONE>", "green")


tk.Button(frame_search, text="Valider", command=valider).pack(side="right", padx=10)

## == Tableaux ==
# Wrapper pour tableau + scrollbar
pane = tk.PanedWindow(app, orient="vertical", sashwidth=5)
pane.pack(fill="both", expand=True, padx=2, pady=2)

wrapper_tab = tk.Frame(pane)
pane.add(wrapper_tab, stretch="always")

# Construction du tableau avec colonne checkbox en plus
all_cols = ("✓", *cols)
tree = ttk.Treeview(wrapper_tab, columns=all_cols, show="headings")
tree.tag_configure("gris", background="#f0f0f0")
tree.heading("✓", text="✓")
tree.column("✓", width=40, anchor="center")
for col in cols:
    tree.heading(col, text=col)

# Scrollbar horizontal
scroll_x = ttk.Scrollbar(wrapper_tab, orient="horizontal", command=tree.xview)
tree.configure(xscrollcommand=scroll_x.set)

scroll_x.pack(fill="x", side="bottom")
tree.pack(fill="both", expand=True)

# Etat des checkboxes
checks = {}

## == Log lives matter ==
# Zone de log
log_box = ScrolledText(pane, height=0, state="disabled", font=("Courier", 10))
pane.add(log_box, stretch="always")

app.update()
pane.sash_place(0, 0, int(app.winfo_height() * 0.7))

log_box.tag_configure("red", foreground="red")
log_box.tag_configure("blue", foreground="blue")
log_box.tag_configure("green", foreground="green")

def log(msg, color=None):
    log_box.config(state="normal")
    log_box.insert("end", msg + "\n", color)
    log_box.see("end")
    log_box.config(state="disabled")

def tab_fill():
    """Vide et re-remplit le tableau selon le filtre de recherche"""
    filtre = search_var.get()
    tree.delete(*tree.get_children())
    for row in rows:
        # filtre sur cols[1] -> [Control_DocNum]
        if filtre and filtre not in str(row[1]).lower():
            continue
        clean = [str(v).replace('"', '').replace('{', '').replace('}', '').replace('\r\n', ' ').replace('\n', ' ') for v in row]
        coche = "☑" if checks.get(tuple(clean)) else "☐"

        tree.insert("", "end", values=[coche, *clean])

        #index = len(tree.get_children())
        #tag = "gris" if index % 2 == 0 else ""
        #tree.insert("", "end", values=[coche, *clean], tags=(tag,))

def set_check(iid, state):
    """Coche/décoche une ligne et synchronise checks + list_id."""
    vals = tree.item(iid, "values")
    row_data = tuple(vals[1:])  # tout sauf la colonne ✓
    checks[row_data] = state
    tree.set(iid, "✓", "☑" if state else "☐")

    if state:
        if vals[2] not in list_id:
            list_id.append(vals[2])
            log(f"> [INFO][APPEND][{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] : {list_id}")
    else:
        if vals[2] in list_id:
            list_id.remove(vals[2])
            if list_id :
                log(f"> [INFO][REMOVE][{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] : {list_id}")
            if not list_id :
                log(f"> [INFO][REMOVE][{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] : <Liste vide>")


list_id = []
def on_click(event):
    """Bascule la checkbox quand on clique sur une ligne."""
    iid = tree.identify_row(event.y)
    if not iid:
        return
    vals = tree.item(iid, "values")
    row_data = tuple(vals[1:])  # tout sauf la colonne ✓
    set_check(iid, not checks.get(row_data, False))  # toggle

tree.bind("<ButtonRelease-1>", on_click)

search_timer = None
def on_search(*_):
    global search_timer
    if search_timer:
        app.after_cancel(search_timer)
    search_timer = app.after(300, tab_fill)

search_var.trace_add("write", on_search)

# Start

if __name__ == "__main__":
    update_data()

    tab_fill()
    app.mainloop()