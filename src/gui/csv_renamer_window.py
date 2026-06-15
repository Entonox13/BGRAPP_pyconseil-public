#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fenêtre utilitaire pour renommer les fichiers CSV d'un dossier source.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Callable, List, Optional, TYPE_CHECKING

try:
    from ..services.file_reader import get_csv_files_in_directory, FileReaderError
    from ..services.csv_renamer import (
        CsvRenamerError,
        display_name_without_extension,
        normalize_csv_filename,
        rename_csv_files,
    )
    from ..utils.paths import get_documents_dir
    from . import theme
except ImportError:
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from services.file_reader import get_csv_files_in_directory, FileReaderError
    from services.csv_renamer import (
        CsvRenamerError,
        display_name_without_extension,
        normalize_csv_filename,
        rename_csv_files,
    )
    from utils.paths import get_documents_dir
    from gui import theme

if TYPE_CHECKING:
    from .main_window import MainWindow


class _CsvRow:
    """Une ligne du tableau : nom actuel + champ éditable."""

    __slots__ = ("filename", "new_name_var")

    def __init__(self, filename: str):
        self.filename = filename
        display_name = display_name_without_extension(filename)
        self.new_name_var = tk.StringVar(value=display_name)


class CsvRenamerWindow:
    """Fenêtre modale de renommage des CSV PRONOTE."""

    def __init__(
        self,
        parent_window: Optional["MainWindow"] = None,
        initial_directory: Optional[str] = None,
        on_renamed: Optional[Callable[[], None]] = None,
    ):
        self.parent_window = parent_window
        self.on_renamed = on_renamed
        self.directory: Optional[str] = initial_directory
        self._rows: List[_CsvRow] = []

        parent = parent_window.root if parent_window else None
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("Renommer les fichiers CSV - BGRAPP Pyconseil")
        self.root.geometry("720x520")
        self.root.minsize(520, 360)
        theme.setup_root_scaling(self.root)

        if parent:
            self.root.transient(parent)
            self.root.grab_set()

        self._setup_styles()
        self._create_interface()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        if self.directory:
            self._set_directory(self.directory)

    def _setup_styles(self):
        style = ttk.Style()
        theme.apply_theme(style)

    def _create_interface(self):
        main_frame = ttk.Frame(self.root, padding=theme.PADDING_NORMAL)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        title = ttk.Label(
            main_frame,
            text="Renommer les exports CSV PRONOTE",
            style="Title.TLabel",
        )
        title.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))

        hint = ttk.Label(
            main_frame,
            text=(
                "Colonne « Nom » : fichiers actuels. "
                "Colonne « Nouveau nom » : saisissez le nom de matière souhaité "
                "(ex. mathematiques, Anglais LV1). L'extension .csv est conservée."
            ),
            style="Info.TLabel",
            wraplength=680,
        )
        hint.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        dir_frame.columnconfigure(1, weight=1)

        ttk.Button(
            dir_frame,
            text="Choisir dossier",
            command=self._browse_directory,
        ).grid(row=0, column=0, padx=(0, 8))

        self.dir_label = ttk.Label(
            dir_frame,
            text="Aucun dossier sélectionné",
            style="Info.TLabel",
            relief="sunken",
            padding="4",
        )
        self.dir_label.grid(row=0, column=1, sticky=(tk.W, tk.E))

        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

        header = ttk.Frame(table_frame)
        header.grid(row=0, column=0, sticky=(tk.W, tk.E))
        header.columnconfigure(0, weight=2)
        header.columnconfigure(1, weight=3)

        ttk.Label(header, text="Nom", style="Header.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(4, 8)
        )
        ttk.Label(header, text="Nouveau nom", style="Header.TLabel").grid(
            row=0, column=1, sticky=tk.W, padx=(4, 0)
        )

        ttk.Separator(table_frame, orient="horizontal").grid(
            row=0, column=0, sticky=(tk.W, tk.E), pady=(24, 0)
        )

        canvas = tk.Canvas(table_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.rows_frame = ttk.Frame(canvas)
        self.rows_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        self._canvas_window = canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(self._canvas_window, width=e.width),
        )
        canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas = canvas

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))

        self.refresh_btn = ttk.Button(
            btn_frame,
            text="Actualiser",
            command=self._reload_files,
            state="disabled",
        )
        self.refresh_btn.grid(row=0, column=0, padx=(0, 8))

        self.rename_btn = ttk.Button(
            btn_frame,
            text="Renommer",
            command=self._apply_renames,
            state="disabled",
        )
        self.rename_btn.grid(row=0, column=1, padx=(0, 8))

        ttk.Button(btn_frame, text="Fermer", command=self._on_closing).grid(
            row=0, column=2
        )

        self.status_label = ttk.Label(main_frame, text="", style="Info.TLabel")
        self.status_label.grid(row=5, column=0, sticky=tk.W, pady=(8, 0))

    def _on_mousewheel(self, event):
        if not hasattr(self, "_canvas"):
            return
        delta = -1 * (event.delta // 120) if event.delta else 0
        if delta:
            self._canvas.yview_scroll(delta, "units")

    def _browse_directory(self):
        directory = filedialog.askdirectory(
            title="Sélectionner le dossier contenant les CSV",
            initialdir=self.directory or get_documents_dir(),
        )
        if directory:
            self._set_directory(directory)

    def _set_directory(self, directory: str):
        self.directory = directory
        self.dir_label.config(text=directory)
        self.refresh_btn.config(state="normal")
        self.rename_btn.config(state="normal")
        self._reload_files()

    def _clear_rows(self):
        for child in self.rows_frame.winfo_children():
            child.destroy()
        self._rows.clear()

    def _reload_files(self):
        if not self.directory:
            return

        self._clear_rows()
        try:
            csv_paths = get_csv_files_in_directory(self.directory)
        except FileReaderError as exc:
            messagebox.showerror("Erreur", str(exc), parent=self.root)
            self.status_label.config(text="")
            return

        if not csv_paths:
            self.status_label.config(text="Aucun fichier .csv trouvé dans ce dossier.")
            return

        for index, path in enumerate(csv_paths):
            filename = Path(path).name
            row = _CsvRow(filename)
            self._rows.append(row)

            name_label = ttk.Label(
                self.rows_frame,
                text=display_name_without_extension(filename),
                anchor=tk.W,
                padding=(4, 6),
            )
            name_label.grid(row=index, column=0, sticky=(tk.W, tk.E), padx=(0, 8))
            entry = ttk.Entry(self.rows_frame, textvariable=row.new_name_var)
            entry.grid(row=index, column=1, sticky=(tk.W, tk.E), pady=1)

        self.rows_frame.columnconfigure(0, weight=2)
        self.rows_frame.columnconfigure(1, weight=3)
        self.status_label.config(text=f"{len(self._rows)} fichier(s) CSV trouvé(s).")

    def _apply_renames(self):
        if not self.directory or not self._rows:
            return

        renames = {
            row.filename: normalize_csv_filename(row.new_name_var.get())
            for row in self._rows
        }
        try:
            count = rename_csv_files(self.directory, renames)
        except CsvRenamerError as exc:
            messagebox.showerror("Renommage impossible", str(exc), parent=self.root)
            return

        self.status_label.config(text=f"{count} fichier(s) renommé(s).")
        messagebox.showinfo(
            "Renommage terminé",
            f"{count} fichier(s) renommé(s) avec succès.",
            parent=self.root,
        )
        self._reload_files()
        if self.on_renamed:
            self.on_renamed()

    def _on_closing(self):
        self.root.unbind_all("<MouseWheel>")
        if self.parent_window:
            self.root.grab_release()
            self.root.destroy()
        else:
            self.root.quit()
            self.root.destroy()

    def run(self):
        """Lance la boucle principale (mode autonome)."""
        self.root.mainloop()


def open_csv_renamer_window(
    parent_window: Optional["MainWindow"] = None,
    initial_directory: Optional[str] = None,
    on_renamed: Optional[Callable[[], None]] = None,
) -> CsvRenamerWindow:
    """Ouvre la fenêtre de renommage."""
    return CsvRenamerWindow(
        parent_window=parent_window,
        initial_directory=initial_directory,
        on_renamed=on_renamed,
    )
