#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Composant UI partage pour gerer les fichiers JSON des autres periodes.

Affiche les periodes liees (auto-decouvertes dans le dossier ou ajoutees
manuellement) et permet d'en ajouter / retirer. Les modifications sont
persistees dans le bloc `_metadata` du fichier JSON courant.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Callable, Optional

# Import conditionnel
try:
    from ..services.period_history import (
        read_payload,
        resolve_period_links,
        discover_sibling_period_files,
        add_period_link,
        remove_period_link,
        set_period_link_code,
        update_file_metadata,
        period_code_of_file,
        suggested_period_code_for_link,
    )
    from ..utils.semester import Period, PERIOD_CODES
    from ..utils.paths import get_documents_dir
    from . import theme
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from services.period_history import (
        read_payload,
        resolve_period_links,
        discover_sibling_period_files,
        add_period_link,
        remove_period_link,
        set_period_link_code,
        update_file_metadata,
        period_code_of_file,
        suggested_period_code_for_link,
    )
    from utils.semester import Period, PERIOD_CODES
    from utils.paths import get_documents_dir
    from gui import theme


class PeriodLinksDialog:
    """Fenetre de gestion des liens vers les JSON des autres periodes."""

    def __init__(self, parent, json_path: str, current_code: str,
                 on_change: Optional[Callable[[], None]] = None):
        self.json_path = json_path
        self.current_code = (current_code or "").strip().upper()
        self.on_change = on_change
        self._row_paths: dict[str, str] = {}

        # Charger la metadata courante du fichier
        self.metadata, _data = read_payload(json_path)

        self.root = tk.Toplevel(parent) if parent else tk.Toplevel()
        self.root.title(theme.DIALOG_PERIOD_LINKS_TITLE)
        self.root.geometry("700x400")
        theme.setup_root_scaling(self.root)
        try:
            self.root.transient(parent)
            self.root.grab_set()
        except Exception:
            pass

        style = ttk.Style()
        theme.apply_theme(style)
        self._create_interface()
        self._refresh()

    def _create_interface(self):
        frame = ttk.Frame(self.root, padding=theme.PADDING_COMPACT)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        current_label = "—"
        period = Period.from_code(self.current_code)
        if period:
            current_label = period.label
        ttk.Label(
            frame,
            text=f"Période courante : {current_label}",
            font=theme.font_ui(theme.FONT_SIZE_HEADER, bold=True),
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 4))

        ttk.Label(
            frame,
            text="Fichiers JSON des autres périodes pris en compte pour la vue d'ensemble :",
            font=theme.font_body(),
        ).grid(row=1, column=0, sticky=tk.W, pady=(0, 6))

        # Tableau des liens
        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ('periode', 'fichier', 'source')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        self.tree.heading('periode', text='Période')
        self.tree.heading('fichier', text='Fichier')
        self.tree.heading('source', text='Origine')
        self.tree.column('periode', width=110)
        self.tree.column('fichier', width=360)
        self.tree.column('source', width=140)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Boutons
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Button(buttons_frame, text=theme.BTN_ADD_JSON, command=self._add_link).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(buttons_frame, text=theme.BTN_EDIT_PERIOD, command=self._edit_link_period).grid(
            row=0, column=1, padx=(0, 8)
        )
        ttk.Button(buttons_frame, text=theme.BTN_REMOVE_SELECTION, command=self._remove_link).grid(
            row=0, column=2, padx=(0, 8)
        )
        ttk.Button(buttons_frame, text="Fermer", command=self._close).grid(
            row=0, column=3, padx=(0, 0)
        )

        self.info_label = ttk.Label(frame, text="", font=theme.font_body(), foreground='gray')
        self.info_label.grid(row=4, column=0, sticky=tk.W, pady=(8, 0))

    def _link_source_label(self, code: str, path: str, manual_codes: set) -> str:
        """Libelle d'origine pour une ligne du tableau."""
        auto_detected = period_code_of_file(path)
        overrides = self.metadata.get("period_link_overrides") or {}
        store_key = os.path.basename(path)
        has_override = any(
            overrides.get(k) == code
            for k in overrides
            if k == store_key or k.endswith(store_key)
        )
        if has_override or (auto_detected and auto_detected != code):
            return "Corrigé"
        if code in manual_codes:
            return "Manuel"
        return "Auto"

    def _refresh(self):
        """Recalcule et affiche l'ensemble effectif des liens."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._row_paths.clear()

        effective = resolve_period_links(self.json_path, self.metadata, self.current_code)
        manual = self.metadata.get("period_links", {}) or {}
        manual_codes = {c.strip().upper() for c in manual if isinstance(c, str)}

        order = list(PERIOD_CODES)
        for code in sorted(effective, key=lambda c: order.index(c) if c in order else 99):
            path = effective[code]
            self._row_paths[code] = path
            period = Period.from_code(code)
            label = period.label if period else code
            source = self._link_source_label(code, path, manual_codes)
            self.tree.insert('', tk.END, iid=code,
                             values=(label, os.path.basename(path), source))

        count = len(effective)
        self.info_label.config(
            text=f"{count} période(s) liée(s)" if count else "Aucune période liée"
        )

    def _persist(self):
        """Sauvegarde la metadata modifiee et notifie l'appelant."""
        try:
            update_file_metadata(self.json_path, self.metadata)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'enregistrer les liens:\n{e}")
            return
        if self.on_change:
            try:
                self.on_change()
            except Exception:
                pass

    def _ask_period_code(
        self,
        file_path: str,
        title: str = "Période du fichier",
        initial_code: Optional[str] = None,
    ) -> Optional[str]:
        """
        Dialogue modal pour choisir manuellement la periode d'un JSON.
        """
        detected = period_code_of_file(file_path)
        suggested = suggested_period_code_for_link(file_path)
        default = initial_code or suggested or detected or "T1"

        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        frame = ttk.Frame(dlg, padding=theme.PADDING_NORMAL)
        frame.grid(row=0, column=0)

        ttk.Label(
            frame,
            text=os.path.basename(file_path),
            font=theme.font_body(bold=True),
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))

        hint_parts = []
        if detected:
            hint_parts.append(f"contenu/métadonnées : {detected}")
        if suggested and suggested != detected:
            hint_parts.append(f"nom de fichier : {suggested}")
        if hint_parts:
            ttk.Label(
                frame,
                text="Détection — " + " ; ".join(hint_parts),
                font=theme.font_body(),
                foreground='gray',
            ).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))

        ttk.Label(frame, text="Attribuer à la période :").grid(
            row=2, column=0, sticky=tk.W, padx=(0, 8)
        )
        var = tk.StringVar(value=default)
        combo = ttk.Combobox(
            frame,
            textvariable=var,
            values=list(PERIOD_CODES),
            state='readonly',
            width=8,
        )
        combo.grid(row=2, column=1, sticky=tk.W)

        result: dict[str, Optional[str]] = {"code": None}

        def _ok():
            code = var.get().strip().upper()
            if code not in PERIOD_CODES:
                messagebox.showwarning("Période invalide", "Choisissez une période valide.", parent=dlg)
                return
            if code == self.current_code:
                messagebox.showwarning(
                    "Attention",
                    "Ce fichier ne peut pas être attribué à la période courante.",
                    parent=dlg,
                )
                return
            result["code"] = code
            dlg.destroy()

        def _cancel():
            dlg.destroy()

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn_frame, text="OK", command=_ok).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btn_frame, text="Annuler", command=_cancel).grid(row=0, column=1)

        dlg.wait_window()
        return result["code"]

    def _add_link(self):
        file_path = filedialog.askopenfilename(
            title="Choisir le JSON d'une autre période",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")],
            initialdir=get_documents_dir(),
        )
        if not file_path:
            return

        if os.path.abspath(file_path) == os.path.abspath(self.json_path):
            messagebox.showwarning("Attention", "Ce fichier est déjà la période courante.")
            return

        code = self._ask_period_code(file_path, title="Attribuer la période")
        if not code:
            return

        added = add_period_link(self.metadata, self.json_path, file_path, period_code=code)
        if not added:
            messagebox.showerror("Erreur", "Impossible d'ajouter ce lien.")
            return
        self._persist()
        self._refresh()

    def _edit_link_period(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Information", "Sélectionnez une période à modifier.")
            return
        code = selection[0]
        file_path = self._row_paths.get(code)
        if not file_path:
            return

        new_code = self._ask_period_code(
            file_path,
            title="Modifier la période attribuée",
            initial_code=code,
        )
        if not new_code or new_code == code:
            return

        try:
            set_period_link_code(
                self.metadata,
                self.json_path,
                file_path,
                new_code,
                self.current_code,
            )
        except ValueError as e:
            messagebox.showwarning("Attention", str(e))
            return

        self._persist()
        self._refresh()

    def _remove_link(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Information", "Sélectionnez une période à retirer.")
            return
        code = selection[0]
        remove_period_link(self.metadata, self.json_path, code, self.current_code)
        self._persist()
        self._refresh()

    def _close(self):
        self.root.destroy()


def open_period_links_dialog(parent, json_path: str, current_code: str,
                             on_change: Optional[Callable[[], None]] = None):
    """
    Ouvre le dialogue de gestion des periodes liees.

    Args:
        parent: Fenetre parente Tk.
        json_path: Chemin du JSON courant.
        current_code: Code de la periode courante.
        on_change: Callback appele apres chaque modification persistee.

    Returns:
        L'instance PeriodLinksDialog, ou None si json_path invalide.
    """
    if not json_path or not os.path.exists(json_path):
        messagebox.showerror(
            "Fichier manquant",
            "Aucun fichier JSON courant. Créez ou chargez d'abord un fichier.",
        )
        return None
    return PeriodLinksDialog(parent, json_path, current_code, on_change=on_change)
