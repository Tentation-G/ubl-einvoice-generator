"""GUI de validation / génération UBL.

- Multi-filtres dynamiques (colonne + texte, combinés en ET)
- Cocher / décocher toutes les lignes filtrées en un clic
- Sélection indexée par ID métier (robuste au refresh)
- Génération dans un thread (UI jamais figée, pas de double-clic possible)
- Log rétro conservé : > [LEVEL] [timestamp] : message
"""

import os
import sys
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from generate_in_cn_xml_from_bdd import (
    fetch_all_header,
    fetch_all_header_columns,
    gen_all_doc_in_list,
)

ID_COL = 1                  # index de la colonne servant d'ID métier (ex: Control_DocNum)
ALL_COLS = "« Toutes »"     # option de filtre "toutes colonnes"
DEBOUNCE_MS = 300


def clean(value):
    """Nettoie une valeur pour l'affichage dans le Treeview."""
    return (str(value)
            .replace('"', '').replace('{', '').replace('}', '')
            .replace('\r\n', ' ').replace('\n', ' ').strip())


class App:
    def __init__(self):
        self.app = tk.Tk()
        self.app.title("Computah, make those things digital")
        self.app.geometry("1200x600")

        self.rows = []          # données brutes de la bdd
        self.cols = []          # noms des colonnes
        self.selected = set()   # IDs cochés (colonne ID_COL)
        self.filters = []       # [{frame, col_var, txt_var}, ...]
        self._timer = None      # debounce des filtres
        self._queue = queue.Queue()  # logs venant du thread de génération

        self._build_ui()

    # ------------------------------------------------------------ UI
    def _build_ui(self):
        # --- Barre du haut : filtres + actions
        top = tk.Frame(self.app)
        top.pack(fill="x", padx=4, pady=(8, 0))

        self.filters_frame = tk.Frame(top)
        self.filters_frame.pack(side="left", fill="x", expand=True)

        actions = tk.Frame(top)
        actions.pack(side="right")
        self.btn_valider = tk.Button(actions, text="Valider", command=self.valider)
        self.btn_valider.pack(side="right", padx=4)
        self.btn_refresh = tk.Button(actions, text="Rafraichir", command=self.update_data)
        self.btn_refresh.pack(side="right", padx=4)
        tk.Button(actions, text="Tout décocher", command=lambda: self.check_visible(False)).pack(side="right", padx=4)
        tk.Button(actions, text="Cocher filtrés", command=lambda: self.check_visible(True)).pack(side="right", padx=4)
        tk.Button(actions, text="+ Filtre", command=self.add_filter).pack(side="right", padx=12)

        # --- Compteur
        self.counter = tk.Label(self.app, anchor="w", fg="#555")
        self.counter.pack(fill="x", padx=6)

        # --- Tableau + log dans un PanedWindow
        pane = tk.PanedWindow(self.app, orient="vertical", sashwidth=5)
        pane.pack(fill="both", expand=True, padx=2, pady=2)

        wrapper = tk.Frame(pane)
        pane.add(wrapper, stretch="always")

        self.tree = ttk.Treeview(wrapper, columns=("✓",), show="headings")
        scroll_y = ttk.Scrollbar(wrapper, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(wrapper, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_x.pack(fill="x", side="bottom")
        scroll_y.pack(fill="y", side="right")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_click)

        # --- Log
        self.log_box = ScrolledText(pane, height=0, state="disabled", font=("Courier", 10))
        pane.add(self.log_box, stretch="always")
        for tag, color in (("red", "red"), ("blue", "blue"), ("green", "green")):
            self.log_box.tag_configure(tag, foreground=color)

        self.app.update()
        pane.sash_place(0, 0, int(self.app.winfo_height() * 0.7))

    def _rebuild_columns(self):
        all_cols = ("✓", *self.cols)
        self.tree.config(columns=all_cols)
        self.tree.heading("✓", text="✓")
        self.tree.column("✓", width=40, anchor="center", stretch=False)
        for col in self.cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130)
        # met à jour les combobox des filtres existants
        for f in self.filters:
            f["combo"]["values"] = (ALL_COLS, *self.cols)

    # ------------------------------------------------------------ Log
    def log(self, level, msg, color=None):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # padding après le crochet, comme avant : "> [INFO]        [ts]" / "> [VALIDATION]  [ts]"
        line = f"> [{level}]".ljust(16) + f"[{ts}] : {msg}\n"
        self.log_box.config(state="normal")
        self.log_box.insert("end", line, color)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    # ------------------------------------------------------------ Data
    def update_data(self):
        try:
            self.rows = fetch_all_header()
            self.cols = list(fetch_all_header_columns())
        except Exception as e:
            self.log("ERROR", f"Lecture bdd impossible : {e}", "red")
            return

        self._rebuild_columns()

        # purge la sélection des IDs disparus de la bdd
        existing = {clean(r[ID_COL]) for r in self.rows}
        gone = self.selected - existing
        if gone:
            self.selected &= existing
            self.log("INFO", f"<{len(gone)} ID(s) cochés absents de la bdd, retirés> -> {sorted(gone)}")

        self.tab_fill()
        self.log("INFO", "<Data up to date>")

    # ------------------------------------------------------------ Filtres
    def add_filter(self):
        frame = tk.Frame(self.filters_frame)
        frame.pack(side="left", padx=3)

        col_var = tk.StringVar(value=ALL_COLS)
        txt_var = tk.StringVar()
        combo = ttk.Combobox(frame, textvariable=col_var, state="readonly",
                             width=18, values=(ALL_COLS, *self.cols))
        combo.pack(side="left")
        tk.Entry(frame, textvariable=txt_var, width=16).pack(side="left", padx=2)

        flt = {"frame": frame, "col_var": col_var, "txt_var": txt_var, "combo": combo}
        tk.Button(frame, text="✕", command=lambda: self.remove_filter(flt)).pack(side="left")
        self.filters.append(flt)

        col_var.trace_add("write", self._debounced_fill)
        txt_var.trace_add("write", self._debounced_fill)

    def remove_filter(self, flt):
        flt["frame"].destroy()
        self.filters.remove(flt)
        self.tab_fill()

    def _debounced_fill(self, *_):
        if self._timer:
            self.app.after_cancel(self._timer)
        self._timer = self.app.after(DEBOUNCE_MS, self.tab_fill)

    def _match(self, values):
        """True si la ligne (valeurs nettoyées) passe tous les filtres (ET)."""
        for f in self.filters:
            needle = f["txt_var"].get().strip().lower()
            if not needle:
                continue
            col = f["col_var"].get()
            if col == ALL_COLS:
                haystack = " ".join(values).lower()
            else:
                try:
                    haystack = values[self.cols.index(col)].lower()
                except ValueError:
                    continue
            if needle not in haystack:
                return False
        return True

    # ------------------------------------------------------------ Tableau
    def tab_fill(self):
        self._timer = None
        self.tree.delete(*self.tree.get_children())
        shown = 0
        for row in self.rows:
            values = [clean(v) for v in row]
            if not self._match(values):
                continue
            coche = "☑" if values[ID_COL] in self.selected else "☐"
            self.tree.insert("", "end", values=[coche, *values])
            shown += 1
        self._update_counter(shown)

    def _update_counter(self, shown=None):
        if shown is None:
            shown = len(self.tree.get_children())
        self.counter.config(
            text=f"{shown} / {len(self.rows)} ligne(s) affichée(s) — {len(self.selected)} cochée(s)"
        )

    def _row_id(self, iid):
        return self.tree.item(iid, "values")[ID_COL + 1]  # +1 : colonne ✓ devant

    def set_check(self, iid, state):
        row_id = self._row_id(iid)
        if state:
            self.selected.add(row_id)
        else:
            self.selected.discard(row_id)
        self.tree.set(iid, "✓", "☑" if state else "☐")
        self._update_counter()

    def on_click(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell":
            return
        iid = self.tree.identify_row(event.y)
        if iid:
            self.set_check(iid, self._row_id(iid) not in self.selected)

    def check_visible(self, state):
        """Coche/décoche toutes les lignes actuellement affichées (filtrées)."""
        iids = self.tree.get_children()
        for iid in iids:
            self.set_check(iid, state)
        action = "APPEND" if state else "REMOVE"
        self.log(f"INFO][{action}", f"{len(iids)} ligne(s) -> {len(self.selected)} cochée(s) au total")

    # ------------------------------------------------------------ Génération
    def valider(self):
        ids = sorted(self.selected)
        if not ids:
            messagebox.showwarning("Attention", "Aucune ligne sélectionnée.")
            self.log("WARNING", "Aucune ligne sélectionnée", "red")
            return

        preview = ", ".join(ids[:10]) + (f" … (+{len(ids) - 10})" if len(ids) > 10 else "")
        if not messagebox.askyesno("Confirmation", f"Valider {len(ids)} ligne(s) ?\n\n{preview}"):
            return

        self.log("VALIDATION", f"<Génération des UBL> -> {ids}")
        self.btn_valider.config(state="disabled")
        self.btn_refresh.config(state="disabled")
        threading.Thread(target=self._worker, args=(ids,), daemon=True).start()
        self.app.after(100, self._poll_queue)

    def _worker(self, ids):
        """Tourne dans un thread : ne touche jamais à l'UI, pousse dans la queue."""
        try:
            for progress in gen_all_doc_in_list(ids):
                self._queue.put(("GENERATION", str(progress), "blue"))
            self._queue.put(("INFO", "<DONE>", "green"))
        except Exception as e:
            self._queue.put(("ERROR", f"Génération interrompue : {e}", "red"))
        finally:
            self._queue.put(None)  # sentinelle de fin

    def _poll_queue(self):
        while True:
            try:
                item = self._queue.get_nowait()
            except queue.Empty:
                self.app.after(100, self._poll_queue)
                return
            if item is None:  # fin du thread
                self.btn_valider.config(state="normal")
                self.btn_refresh.config(state="normal")
                return
            self.log(*item)

    # ------------------------------------------------------------ Run
    def run(self):
        self.add_filter()       # un filtre par défaut au lancement
        self.update_data()
        self.app.mainloop()


if __name__ == "__main__":
    App().run()