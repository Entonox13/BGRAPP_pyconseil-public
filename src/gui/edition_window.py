#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fenêtre d'édition des bulletins de l'application BGRAPP Pyconseil
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import conditionnel
try:
    from ..models.bulletin import Bulletin, Eleve, AppreciationMatiere, PERIOD_CODES
    from ..utils.semester import (
        Period,
        Semester,
        PeriodSystem,
        periods_for_system,
        infer_period_from_bulletins_data,
        period_from_metadata,
        period_system_from_metadata,
    )
    from ..services.json_generator import save_output_json
    from ..services.period_history import (
        resolve_period_links,
        load_history_bulletins,
        build_display_bulletins,
    )
    from .period_links_panel import open_period_links_dialog
    from ..utils.paths import get_documents_dir
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models.bulletin import Bulletin, Eleve, AppreciationMatiere, PERIOD_CODES
    from utils.semester import (
        Period,
        Semester,
        PeriodSystem,
        periods_for_system,
        infer_period_from_bulletins_data,
        period_from_metadata,
        period_system_from_metadata,
    )
    from services.json_generator import save_output_json
    from services.period_history import (
        resolve_period_links,
        load_history_bulletins,
        build_display_bulletins,
    )
    sys.path.insert(0, str(Path(__file__).parent))
    from period_links_panel import open_period_links_dialog
    from utils.paths import get_documents_dir


class EditionWindow:
    """Fenêtre d'édition des bulletins"""
    
    def __init__(self, parent_window=None, json_file_path: Optional[str] = None,
                 initial_semester: Optional[Period] = None):
        self.parent_window = parent_window
        self.json_file_path = json_file_path
        self.bulletins: List[Bulletin] = []
        # Bulletins enrichis des periodes liees (lecture seule, colonnes)
        self.display_bulletins: List[Bulletin] = []
        self.current_bulletin_index: int = 0
        # Période du fichier JSON (édition / sauvegarde / métadonnées) — immuable après chargement
        self._file_period: Period = initial_semester or Period.S2
        # Période affichée dans le sélecteur (consultation des colonnes liées, lecture seule)
        self.period: Period = self._file_period
        # Période imposée par l'appelant (sélection manuelle dans la fenêtre
        # principale) : prioritaire sur la détection automatique au 1er chargement.
        self._forced_initial_period: Optional[Period] = initial_semester
        self.period_codes: List[str] = self._default_period_codes()
        # Périodes éditables : uniquement la période du fichier (un JSON par période)
        self.editable_codes: List[str] = [self._file_period.value]
        self.metadata: Dict[str, Any] = {}
        self.appreciation_widgets: List[Any] = []
        self.appreciation_texts: Dict[str, tk.Text] = {}
        self.general_widgets: List[Any] = []
        self.general_texts: Dict[str, tk.Text] = {}
        
        # Créer la fenêtre
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.root.title("BGRAPP Pyconseil - Édition des bulletins")
        self.root.geometry("1000x700")
        
        self._setup_styles()
        self._create_interface()
        self._apply_period_ui_state()
        
        if json_file_path and os.path.exists(json_file_path):
            self._load_bulletins_from_file(json_file_path)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_styles(self):
        """Configure les styles de l'interface"""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 10))
    
    def _create_interface(self):
        """Crée l'interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        self._create_toolbar(main_frame, 0)
        
        # Zone principale
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        self._create_navigation_panel(content_frame, 0, 0)
        self._create_content_area(content_frame, 0, 1)
        self._create_action_bar(main_frame, 2)

    @property
    def semester(self) -> Period:
        """Alias rétro-compatible : période du fichier (édition / IA / sauvegarde)."""
        return self._file_period

    @semester.setter
    def semester(self, value: Period) -> None:
        self._file_period = value
        self.period = value

    @property
    def file_period(self) -> Period:
        """Période réellement stockée dans le fichier JSON courant."""
        return self._file_period

    def _default_period_codes(self) -> List[str]:
        """Codes de période par défaut selon le système du fichier."""
        system = self._file_period.system if hasattr(self, '_file_period') else PeriodSystem.SEMESTRE
        return [p.value for p in periods_for_system(system)]

    def _determine_period(self, metadata: Optional[Dict[str, Any]], data: List[Dict[str, Any]]) -> Period:
        """Détermine la période active à partir des métadonnées ou des données JSON."""
        period = period_from_metadata(metadata)
        if period:
            return period
        return infer_period_from_bulletins_data(data)

    def _merge_linked_periods(self, current_bulletins: List[Bulletin]) -> List[Bulletin]:
        """
        Construit une copie des bulletins enrichie des périodes liées (lecture
        seule) pour l'affichage des colonnes ; n'altère pas self.bulletins.
        """
        if not self.json_file_path:
            return list(current_bulletins)
        try:
            links = resolve_period_links(self.json_file_path, self.metadata, self._file_period.value)
            if not links:
                return build_display_bulletins(current_bulletins, {}, self._file_period.value)
            history = load_history_bulletins(links)
            return build_display_bulletins(current_bulletins, history, self._file_period.value)
        except Exception:
            return list(current_bulletins)

    def _compute_period_codes(self) -> List[str]:
        """
        Toutes les périodes réellement présentes (période courante + périodes
        liées fusionnées pour l'affichage), dans l'ordre canonique.
        """
        present = set()
        source = self.display_bulletins or self.bulletins
        for bulletin in source:
            for appreciation in bulletin.matieres.values():
                present.update(appreciation.periodes.keys())
        # Toujours inclure la période du fichier (même si vide)
        present.add(self._file_period.value)
        
        if present:
            return [c for c in PERIOD_CODES if c in present]
        
        # Aucune donnée : colonnes par défaut du système (métadonnées/période fichier)
        system = period_system_from_metadata(self.metadata) or self._file_period.system
        return [p.value for p in periods_for_system(system)]

    def _apply_period_ui_state(self):
        """Reconstruit colonnes et sections selon les périodes présentes."""
        if not hasattr(self, 'subjects_tree'):
            return
        
        self.period_codes = self._compute_period_codes()
        # Seule la période du fichier est éditable (un JSON par période)
        self.editable_codes = [self._file_period.value]
        self._configure_subjects_columns()
        self._build_appreciation_widgets()
        self._build_general_widgets()
        self._refresh_period_selector()
        
        # Libellés des boutons IA : période du fichier uniquement
        code = self._file_period.value
        if hasattr(self, 'current_generate_btn'):
            self.current_generate_btn.config(text=f"✨ Générer appréciation {code}")
        if hasattr(self, 'generate_btn'):
            self.generate_btn.config(text=f"✨ Génération appréciation générale ({code})")

    def _metadata_for_save(self) -> Dict[str, Any]:
        """Prépare le bloc _metadata à écrire en tête du JSON."""
        metadata = dict(self.metadata) if self.metadata else {}
        fp = self._file_period
        metadata.update({
            "semester": fp.value,
            "current_period": fp.value,
            "period_system": fp.system.value,
            "period_label": fp.label,
            "semester_label": fp.label,
            "saved_at": datetime.utcnow().isoformat(timespec="seconds"),
        })
        return metadata
    
    def _create_toolbar(self, parent, row):
        """Crée la barre d'outils"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        toolbar_frame.columnconfigure(3, weight=1)
        
        # Titre
        ttk.Label(toolbar_frame, text="📝 Édition des bulletins", style='Title.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        # Bouton charger
        self.load_btn = ttk.Button(toolbar_frame, text="📂 Charger JSON", command=self._load_json_file)
        self.load_btn.grid(row=0, column=1, padx=(20, 10))

        # Bouton périodes liées (autres JSON)
        self.period_links_btn = ttk.Button(toolbar_frame, text="🔗 Périodes liées", command=self._open_period_links)
        self.period_links_btn.grid(row=0, column=5, padx=(10, 10))
        
        # Sélecteur manuel de période (trimestre/semestre)
        self._build_period_selector(toolbar_frame, 2)
        
        # Indicateur position
        self.position_label = ttk.Label(toolbar_frame, text="Aucun bulletin chargé", style='Info.TLabel')
        self.position_label.grid(row=0, column=3, sticky=tk.E)
        
        # Bouton retour
        self.back_btn = ttk.Button(toolbar_frame, text="◀ Retour", command=self._return_to_main)
        self.back_btn.grid(row=0, column=4, padx=(10, 0))

    def _build_period_selector(self, parent, column):
        """Crée le sélecteur de période affichée (consultation, lecture seule)."""
        selector_frame = ttk.Frame(parent)
        selector_frame.grid(row=0, column=column, padx=(0, 15))
        ttk.Label(selector_frame, text="Afficher :", style='Info.TLabel').grid(
            row=0, column=0, padx=(0, 5)
        )
        self.period_var = tk.StringVar()
        self.period_combo = ttk.Combobox(
            selector_frame,
            textvariable=self.period_var,
            state='readonly',
            width=14,
        )
        self.period_combo.grid(row=0, column=1)
        self.period_combo.bind('<<ComboboxSelected>>', self._on_period_selected)

    def _refresh_period_selector(self):
        """Synchronise le sélecteur avec les périodes disponibles (affichage)."""
        if not hasattr(self, 'period_combo'):
            return
        codes = list(self.period_codes) if self.period_codes else [self._file_period.value]
        if self.period.value not in codes:
            codes = [self.period.value] + codes
        self._period_choice_codes = codes
        labels = [
            (Period.from_code(code).label if Period.from_code(code) else code)
            for code in codes
        ]
        self.period_combo['values'] = labels
        try:
            self.period_combo.current(codes.index(self.period.value))
        except ValueError:
            pass

    def _on_period_selected(self, event=None):
        """Change la période affichée (colonnes liées) sans modifier l'édition/sauvegarde."""
        index = self.period_combo.current()
        codes = getattr(self, '_period_choice_codes', [])
        if index < 0 or index >= len(codes):
            return
        selected = Period.from_code(codes[index])
        if not selected or selected == self.period:
            return
        self.period = selected
        self._refresh_period_selector()
        self._update_display()
    
    def _create_navigation_panel(self, parent, row, column):
        """Crée le panneau de navigation"""
        nav_frame = ttk.LabelFrame(parent, text="Navigation", padding="5")
        nav_frame.grid(row=row, column=column, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        nav_frame.columnconfigure(0, weight=1)
        nav_frame.rowconfigure(1, weight=1)
        
        # Boutons navigation
        nav_buttons_frame = ttk.Frame(nav_frame)
        nav_buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        nav_buttons_frame.columnconfigure(1, weight=1)
        
        self.prev_btn = ttk.Button(nav_buttons_frame, text="◀ Précédent", command=self._previous_bulletin, state='disabled')
        self.prev_btn.grid(row=0, column=0, sticky=tk.W)
        
        self.next_btn = ttk.Button(nav_buttons_frame, text="Suivant ▶", command=self._next_bulletin, state='disabled')
        self.next_btn.grid(row=0, column=2, sticky=tk.E)
        
        # Liste bulletins
        self.bulletin_list = tk.Listbox(nav_frame, height=15)
        self.bulletin_list.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.bulletin_list.bind('<<ListboxSelect>>', self._on_bulletin_select)
        
        # Scrollbar
        list_scrollbar = ttk.Scrollbar(nav_frame, orient=tk.VERTICAL, command=self.bulletin_list.yview)
        list_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.bulletin_list.configure(yscrollcommand=list_scrollbar.set)
    
    def _create_content_area(self, parent, row, column):
        """Crée la zone de contenu"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=row, column=column, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self._create_student_tab()
        self._create_subjects_tab()
        self._create_general_tab()
    
    def _create_student_tab(self):
        """Onglet informations élève"""
        student_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(student_frame, text="👤 Élève")
        
        info_frame = ttk.LabelFrame(student_frame, text="Informations", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        # Nom
        ttk.Label(info_frame, text="Nom:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.nom_label = ttk.Label(info_frame, text="-", relief='sunken', padding="3")
        self.nom_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Prénom
        ttk.Label(info_frame, text="Prénom:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.prenom_label = ttk.Label(info_frame, text="-", relief='sunken', padding="3")
        self.prenom_label.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Classe
        ttk.Label(info_frame, text="Classe:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.classe_label = ttk.Label(info_frame, text="-", relief='sunken', padding="3")
        self.classe_label.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
    
    def _create_subjects_tab(self):
        """Onglet matières"""
        subjects_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(subjects_frame, text="📚 Matières")
        subjects_frame.columnconfigure(0, weight=1)
        subjects_frame.rowconfigure(0, weight=1)
        
        # TreeView matières
        tree_frame = ttk.Frame(subjects_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.subjects_tree = ttk.Treeview(tree_frame, show='headings', height=15)
        self._configure_subjects_columns()
        
        self.subjects_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.subjects_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.subjects_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Zone appréciations (une zone par période, construite dynamiquement)
        self.appreciation_frame = ttk.LabelFrame(subjects_frame, text="Appréciations de la matière sélectionnée", padding="5")
        self.appreciation_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        self.appreciation_frame.columnconfigure(0, weight=1)
        self._build_appreciation_widgets()
        
        self.subjects_tree.bind('<<TreeviewSelect>>', self._on_subject_select)
    
    def _configure_subjects_columns(self):
        """Configure dynamiquement les colonnes du tableau des matières."""
        if not hasattr(self, 'subjects_tree'):
            return
        
        columns = ['matiere']
        headings = {'matiere': 'Matière'}
        widths = {'matiere': 200}
        
        for code in self.period_codes:
            for prefix, label, width in (
                ('moyenne', 'Moy.', 80),
                ('absence', 'Abs.', 80),
                ('retards', 'Ret.', 70),
            ):
                col = f'{prefix}_{code.lower()}'
                columns.append(col)
                headings[col] = f'{label} {code}'
                widths[col] = width
        
        self.subjects_tree_columns = tuple(columns)
        self.subjects_tree.configure(columns=self.subjects_tree_columns)
        for col in columns:
            self.subjects_tree.heading(col, text=headings[col])
            self.subjects_tree.column(col, width=widths[col])
    
    def _build_appreciation_widgets(self):
        """(Re)construit les zones d'appréciation par période (matière sélectionnée)."""
        if not hasattr(self, 'appreciation_frame'):
            return
        for widget in self.appreciation_widgets:
            widget.destroy()
        self.appreciation_widgets.clear()
        self.appreciation_texts = {}
        
        row = 0
        for code in self.editable_codes:
            label = ttk.Label(self.appreciation_frame, text=f"Appréciation {code}:")
            label.grid(row=row, column=0, sticky=tk.W, pady=2)
            self.appreciation_widgets.append(label)
            row += 1
            
            text = tk.Text(self.appreciation_frame, height=3, width=60, wrap=tk.WORD, state='disabled')
            text.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=2)
            self.appreciation_widgets.append(text)
            self.appreciation_texts[code] = text
            row += 1
    
    def _create_general_tab(self):
        """Onglet appréciation générale"""
        general_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(general_frame, text="📋 Appréciation générale")
        general_frame.columnconfigure(0, weight=1)
        
        # Conteneur des zones par période (construites dynamiquement)
        self.general_container = ttk.Frame(general_frame)
        self.general_container.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.general_container.columnconfigure(0, weight=1)
        self._build_general_widgets()
    
        # Boutons pour traitement du bulletin courant uniquement
        current_actions_frame = ttk.LabelFrame(general_frame, text="Actions sur le bulletin courant", padding="5")
        current_actions_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.current_preprocess_btn = ttk.Button(
            current_actions_frame, 
            text="🔄 Prétraiter ce bulletin", 
            command=self._preprocess_current_bulletin,
            state='disabled'
        )
        self.current_preprocess_btn.grid(row=0, column=0, padx=(0, 10), pady=5)
        
        self.current_generate_btn = ttk.Button(
            current_actions_frame, 
            text="✨ Générer appréciation", 
            command=self._generate_current_general,
            state='disabled'
        )
        self.current_generate_btn.grid(row=0, column=1, pady=5)
    
    def _build_general_widgets(self):
        """(Re)construit les zones d'appréciation générale par période."""
        if not hasattr(self, 'general_container'):
            return
        for widget in self.general_widgets:
            widget.destroy()
        self.general_widgets.clear()
        self.general_texts = {}
        
        for row, code in enumerate(self.editable_codes):
            frame = ttk.LabelFrame(self.general_container, text=f"Appréciation générale {code}", padding="5")
            frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            frame.columnconfigure(0, weight=1)
            self.general_widgets.append(frame)
            
            text = tk.Text(frame, height=6, wrap=tk.WORD)
            text.grid(row=0, column=0, sticky=(tk.W, tk.E))
            self.general_texts[code] = text
    
    def _create_action_bar(self, parent, row):
        """Barre d'actions"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Boutons OpenAI
        self.preprocess_btn = ttk.Button(action_frame, text="🔄 Prétraitement", command=self._preprocess_text, state='disabled')
        self.preprocess_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.generate_btn = ttk.Button(action_frame, text="✨ Génération appréciation générale", command=self._generate_general, state='disabled')
        self.generate_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Sauvegarde
        self.save_btn = ttk.Button(action_frame, text="💾 Sauvegarder", command=self._save_changes, state='disabled')
        self.save_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Statut
        self.status_label = ttk.Label(action_frame, text="Prêt")
        self.status_label.grid(row=0, column=3, padx=(20, 0), sticky=tk.E)
    
    def _load_json_file(self):
        """Charge un fichier JSON"""
        file_path = filedialog.askopenfilename(
            title="Charger un fichier JSON de bulletins",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")],
            initialdir=get_documents_dir()
        )
        
        if file_path:
            self._load_bulletins_from_file(file_path)

    def _open_period_links(self):
        """Ouvre la gestion des JSON des autres périodes."""
        if not self.json_file_path or not os.path.exists(self.json_file_path):
            messagebox.showinfo(
                "Information",
                "Chargez d'abord un fichier JSON pour gérer les périodes liées."
            )
            return
        open_period_links_dialog(
            self.root,
            self.json_file_path,
            self._file_period.value,
            on_change=lambda: self._load_bulletins_from_file(self.json_file_path),
        )
    
    def _load_bulletins_from_file(self, file_path: str):
        """Charge les bulletins depuis un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            metadata = {}
            data = raw_data
            if raw_data and isinstance(raw_data[0], dict) and '_metadata' in raw_data[0]:
                metadata = raw_data[0].get('_metadata') or {}
                data = raw_data[1:]
            
            self.metadata = metadata
            # Période du fichier : toujours déduite du JSON (pas du sélecteur d'affichage)
            self._file_period = self._determine_period(metadata, data)
            if self._forced_initial_period is not None:
                # Vue initiale imposée par l'appelant (consommée une fois)
                self.period = self._forced_initial_period
                self._forced_initial_period = None
            else:
                self.period = self._file_period
            
            self.bulletins = []
            for bulletin_data in data:
                bulletin = Bulletin.from_dict(bulletin_data)
                self.bulletins.append(bulletin)
            
            self.json_file_path = file_path
            # Fusionner (lecture seule) les periodes liees pour les colonnes
            self.display_bulletins = self._merge_linked_periods(self.bulletins)
            
            # Adapter les colonnes/sections aux périodes réellement présentes
            self._apply_period_ui_state()
            
            self.current_bulletin_index = 0
            
            self._update_bulletin_list()
            self._update_display()
            self._update_status(f"✅ {len(self.bulletins)} bulletins chargés")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le fichier:\n{str(e)}")
    
    def _update_bulletin_list(self):
        """Met à jour la liste des bulletins"""
        self.bulletin_list.delete(0, tk.END)
        
        for bulletin in self.bulletins:
            self.bulletin_list.insert(tk.END, f"{bulletin.eleve.nom} {bulletin.eleve.prenom}")
        
        if self.bulletins:
            self.bulletin_list.selection_set(self.current_bulletin_index)
            self._update_navigation_buttons()
        
        self._update_position_indicator()
    
    def _update_display(self):
        """Met à jour l'affichage"""
        if not self.bulletins:
            self._clear_display()
            return
        
        bulletin = self.bulletins[self.current_bulletin_index]
        
        # Infos élève
        self.nom_label.config(text=bulletin.eleve.nom)
        self.prenom_label.config(text=bulletin.eleve.prenom)
        self.classe_label.config(text=bulletin.eleve.classe or "Non définie")
        
        # Matières
        self._update_subjects_display(bulletin)
        
        # Appréciations générales
        self._update_general_display(bulletin)
        
        # Activer boutons
        self.save_btn.config(state='normal')
        if bulletin.matieres:
            self.preprocess_btn.config(state='normal')
            self.generate_btn.config(state='normal')
            self.current_preprocess_btn.config(state='normal')
            self.current_generate_btn.config(state='normal')
    
    def _update_subjects_display(self, bulletin):
        """Met à jour l'affichage des matières (colonnes multi-périodes)."""
        for item in self.subjects_tree.get_children():
            self.subjects_tree.delete(item)
        
        # Utiliser la version fusionnée (périodes liées) pour les colonnes
        display_bulletin = bulletin
        if self.display_bulletins and self.current_bulletin_index < len(self.display_bulletins):
            display_bulletin = self.display_bulletins[self.current_bulletin_index]
        
        for nom_matiere, appreciation in display_bulletin.matieres.items():
            values = [nom_matiere]
            for code in self.period_codes:
                periode = appreciation.get_periode(code)
                moyenne = periode.moyenne if periode else None
                absence = periode.heures_absence if periode else None
                retards = periode.retards if periode else None
                values.append(f"{moyenne:.2f}" if isinstance(moyenne, (int, float)) else "-")
                values.append(absence if absence else "-")
                values.append(str(retards) if retards is not None else "-")
            
            self.subjects_tree.insert('', tk.END, values=tuple(values))
        
        # Vider appréciations - l'affichage se fera lors de la sélection d'une matière
        for text in self.appreciation_texts.values():
            text.config(state='normal')
            text.delete('1.0', tk.END)
            text.insert('1.0', "Sélectionnez une matière pour voir les appréciations")
            text.config(state='disabled')
    
    def _update_general_display(self, bulletin):
        """Met à jour les appréciations générales (une zone par période)."""
        for code, text in self.general_texts.items():
            text.delete('1.0', tk.END)
            texte = bulletin.get_appreciation_generale(code)
            if texte:
                text.insert('1.0', texte)
    
    def _clear_display(self):
        """Vide l'affichage"""
        self.nom_label.config(text="-")
        self.prenom_label.config(text="-")
        self.classe_label.config(text="-")
        
        for item in self.subjects_tree.get_children():
            self.subjects_tree.delete(item)
        
        for text in self.general_texts.values():
            text.delete('1.0', tk.END)
        
        self.save_btn.config(state='disabled')
        self.preprocess_btn.config(state='disabled')
        self.generate_btn.config(state='disabled')
        self.current_preprocess_btn.config(state='disabled')
        self.current_generate_btn.config(state='disabled')
    
    def _previous_bulletin(self):
        """Bulletin précédent"""
        if self.current_bulletin_index > 0:
            self.current_bulletin_index -= 1
            self.bulletin_list.selection_clear(0, tk.END)
            self.bulletin_list.selection_set(self.current_bulletin_index)
            self._update_display()
            self._update_navigation_buttons()
            self._update_position_indicator()
    
    def _next_bulletin(self):
        """Bulletin suivant"""
        if self.current_bulletin_index < len(self.bulletins) - 1:
            self.current_bulletin_index += 1
            self.bulletin_list.selection_clear(0, tk.END)
            self.bulletin_list.selection_set(self.current_bulletin_index)
            self._update_display()
            self._update_navigation_buttons()
            self._update_position_indicator()
    
    def _on_bulletin_select(self, event):
        """Sélection bulletin"""
        selection = self.bulletin_list.curselection()
        if selection:
            self.current_bulletin_index = selection[0]
            self._update_display()
            self._update_navigation_buttons()
            self._update_position_indicator()
    
    def _on_subject_select(self, event):
        """Sélection matière"""
        selection = self.subjects_tree.selection()
        if not selection or not self.bulletins:
            return
        
        item = self.subjects_tree.item(selection[0])
        nom_matiere = item['values'][0]
        
        bulletin = self.bulletins[self.current_bulletin_index]
        appreciation = bulletin.get_matiere(nom_matiere)
        
        if appreciation:
            for code, text in self.appreciation_texts.items():
                text.config(state='normal')
                text.delete('1.0', tk.END)
                periode = appreciation.get_periode(code)
                if periode and periode.appreciation:
                    text.insert('1.0', periode.appreciation)
                text.config(state='disabled')
    
    def _update_navigation_buttons(self):
        """Met à jour boutons navigation"""
        if not self.bulletins:
            self.prev_btn.config(state='disabled')
            self.next_btn.config(state='disabled')
            return
        
        self.prev_btn.config(state='normal' if self.current_bulletin_index > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_bulletin_index < len(self.bulletins) - 1 else 'disabled')
    
    def _update_position_indicator(self):
        """Met à jour l'indicateur de position"""
        if not self.bulletins:
            self.position_label.config(text="Aucun bulletin chargé")
        else:
            self.position_label.config(text=f"Bulletin {self.current_bulletin_index + 1} / {len(self.bulletins)}")
    
    def _refresh_display_with_selection(self):
        """Rafraîchit l'affichage en conservant la sélection de matière courante"""
        # Sauvegarder la sélection de matière courante
        selected_matiere = None
        selection = self.subjects_tree.selection()
        if selection:
            item = self.subjects_tree.item(selection[0])
            selected_matiere = item['values'][0] if item['values'] else None
        
        # Rafraîchir l'affichage
        self._update_display()
        
        # Restaurer la sélection de matière si possible
        if selected_matiere:
            for item_id in self.subjects_tree.get_children():
                item = self.subjects_tree.item(item_id)
                if item['values'] and item['values'][0] == selected_matiere:
                    self.subjects_tree.selection_set(item_id)
                    self.subjects_tree.focus(item_id)
                    # Déclencher l'événement de sélection
                    self._on_subject_select(None)
                    break
    
    def _preprocess_text(self):
        """Prétraitement de toutes les appréciations"""
        if not self.bulletins:
            messagebox.showerror("Erreur", "Aucun bulletin chargé")
            return
        
        # Vérifier la configuration du fournisseur IA actif
        try:
            from ..services.openai_service import get_ai_service
        except ImportError:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from services.openai_service import get_ai_service
        
        openai_service = get_ai_service()
        if not openai_service:
            messagebox.showerror("Erreur IA", 
                               "Impossible de se connecter au fournisseur IA actif.\n" + 
                               "Vérifiez votre clé API et le fournisseur sélectionné dans la configuration.")
            return
        
        # Créer une fenêtre de progression
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Prétraitement en cours...")
        progress_window.geometry("400x150")
        progress_window.resizable(False, False)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Prétraitement des appréciations", font=('Arial', 12, 'bold')).pack(pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(pady=10, padx=20, fill=tk.X)
        
        status_label = ttk.Label(progress_window, text="Initialisation...")
        status_label.pack(pady=5)
        
        # Bouton annuler
        cancelled = tk.BooleanVar(value=False)
        def cancel_operation():
            cancelled.set(True)
            
        cancel_btn = ttk.Button(progress_window, text="Annuler", command=cancel_operation)
        cancel_btn.pack(pady=10)
        
        def update_progress(current, total):
            if cancelled.get():
                return
            progress = (current / total) * 100
            progress_var.set(progress)
            status_label.config(text=f"Traitement: {current}/{total}")
            progress_window.update()
        
        # Traitement en thread pour éviter le blocage de l'interface
        import threading
        
        def process_bulletins():
            try:
                if cancelled.get():
                    return
                    
                success_count, error_count = openai_service.preprocess_all_bulletins(
                    self.bulletins, 
                    progress_callback=update_progress
                )
                
                if not cancelled.get():
                    progress_window.destroy()
                    
                    # Sauvegarder automatiquement
                    self._save_changes()
                    
                    # Rafraîchir l'affichage en conservant la sélection
                    self._refresh_display_with_selection()
                    
                    messagebox.showinfo("Prétraitement terminé", 
                                      f"Prétraitement terminé !\n" +
                                      f"Réussites: {success_count}\n" +
                                      f"Erreurs: {error_count}")
                    
            except Exception as e:
                if not cancelled.get():
                    progress_window.destroy()
                    messagebox.showerror("Erreur", f"Erreur pendant le prétraitement:\n{str(e)}")
        
        thread = threading.Thread(target=process_bulletins)
        thread.daemon = True
        thread.start()
    
    def _generate_general(self):
        """Génération d'appréciations générales S2 pour tous les bulletins"""
        if not self.bulletins:
            messagebox.showerror("Erreur", "Aucun bulletin chargé")
            return
        
        # Vérifier la configuration du fournisseur IA actif
        try:
            from ..services.openai_service import get_ai_service
        except ImportError:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from services.openai_service import get_ai_service
        
        openai_service = get_ai_service()
        if not openai_service:
            messagebox.showerror("Erreur IA", 
                               "Impossible de se connecter au fournisseur IA actif.\n" + 
                               "Vérifiez votre clé API et le fournisseur sélectionné dans la configuration.")
            return
        
        # Créer une fenêtre de progression
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Génération d'appréciations générales")
        progress_window.geometry("400x150")
        progress_window.resizable(False, False)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text=f"Génération des appréciations générales ({self._file_period.value})", font=('Arial', 12, 'bold')).pack(pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(pady=10, padx=20, fill=tk.X)
        
        status_label = ttk.Label(progress_window, text="Initialisation...")
        status_label.pack(pady=5)
        
        # Bouton annuler
        cancelled = tk.BooleanVar(value=False)
        def cancel_operation():
            cancelled.set(True)
            
        cancel_btn = ttk.Button(progress_window, text="Annuler", command=cancel_operation)
        cancel_btn.pack(pady=10)
        
        def update_progress(current, total):
            if cancelled.get():
                return
            progress = (current / total) * 100
            progress_var.set(progress)
            status_label.config(text=f"Génération: {current}/{total}")
            progress_window.update()
        
        # Traitement en thread pour éviter le blocage de l'interface
        import threading
        
        def process_bulletins():
            try:
                if cancelled.get():
                    return
                    
                success_count, error_count = openai_service.generate_all_general_appreciations(
                    self.bulletins, 
                    semester=self.semester,
                    progress_callback=update_progress
                )
                
                if not cancelled.get():
                    progress_window.destroy()
                    
                    # Sauvegarder automatiquement en préservant les valeurs générées
                    self._save_changes_preserve_generated()
                    
                    # Rafraîchir l'affichage en conservant la sélection
                    self._refresh_display_with_selection()
                    
                    messagebox.showinfo("Génération terminée", 
                                      f"Génération terminée !\n" +
                                      f"Réussites: {success_count}\n" +
                                      f"Erreurs: {error_count}")
                    
            except Exception as e:
                if not cancelled.get():
                    progress_window.destroy()
                    messagebox.showerror("Erreur", f"Erreur pendant la génération:\n{str(e)}")
        
        thread = threading.Thread(target=process_bulletins)
        thread.daemon = True
        thread.start()
    
    def _preprocess_current_bulletin(self):
        """Prétraitement du bulletin courant uniquement"""
        if not self.bulletins or self.current_bulletin_index >= len(self.bulletins):
            messagebox.showerror("Erreur", "Aucun bulletin sélectionné")
            return
        
        # Vérifier la configuration du fournisseur IA actif
        try:
            from ..services.openai_service import get_ai_service
        except ImportError:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from services.openai_service import get_ai_service
        
        openai_service = get_ai_service()
        if not openai_service:
            messagebox.showerror("Erreur IA", 
                               "Impossible de se connecter au fournisseur IA actif.\n" + 
                               "Vérifiez votre clé API et le fournisseur sélectionné dans la configuration.")
            return
        
        bulletin = self.bulletins[self.current_bulletin_index]
        
        # Créer une fenêtre de progression simple
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Prétraitement en cours...")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text=f"Prétraitement de {bulletin.eleve.nom} {bulletin.eleve.prenom}", 
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill=tk.X)
        progress_bar.start()
        
        # Traitement en thread
        import threading
        
        def process_current_bulletin():
            try:
                success_count = 0
                error_count = 0
                
                for nom_matiere, matiere in bulletin.matieres.items():
                    for code, periode in matiere.periodes.items():
                        if not periode.appreciation:
                            continue
                        try:
                            preprocessed = openai_service.preprocess_appreciation(
                                periode.appreciation,
                                bulletin.eleve.nom,
                                bulletin.eleve.prenom
                            )
                            periode.appreciation = preprocessed
                            success_count += 1
                        except Exception as e:
                            print(f"Erreur prétraitement {code} {nom_matiere}: {e}")
                            error_count += 1
                
                progress_window.destroy()
                
                # Sauvegarder automatiquement
                self._save_changes()
                
                # Rafraîchir l'affichage en conservant la sélection
                self._refresh_display_with_selection()
                
                messagebox.showinfo("Prétraitement terminé", 
                                  f"Prétraitement terminé pour {bulletin.eleve.nom} {bulletin.eleve.prenom} !\n" +
                                  f"Appréciations traitées: {success_count}\n" +
                                  f"Erreurs: {error_count}")
                
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("Erreur", f"Erreur pendant le prétraitement:\n{str(e)}")
        
        thread = threading.Thread(target=process_current_bulletin)
        thread.daemon = True
        thread.start()
    
    def _generate_current_general(self):
        """Génération d'appréciation générale S2 pour le bulletin courant"""
        if not self.bulletins or self.current_bulletin_index >= len(self.bulletins):
            messagebox.showerror("Erreur", "Aucun bulletin sélectionné")
            return
        
        # Vérifier la configuration du fournisseur IA actif
        try:
            from ..services.openai_service import get_ai_service
        except ImportError:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from services.openai_service import get_ai_service
        
        openai_service = get_ai_service()
        if not openai_service:
            messagebox.showerror("Erreur IA", 
                               "Impossible de se connecter au fournisseur IA actif.\n" + 
                               "Vérifiez votre clé API et le fournisseur sélectionné dans la configuration.")
            return
        
        bulletin = self.bulletins[self.current_bulletin_index]
        
        # Collecter les appréciations de la période du fichier par matière
        code = self._file_period.value
        appreciations = {}
        for nom_matiere, matiere in bulletin.matieres.items():
            periode = matiere.get_periode(code)
            appreciation_value = periode.appreciation if periode else None
            if appreciation_value and appreciation_value.strip():
                appreciations[nom_matiere] = appreciation_value
        
        if not appreciations:
            messagebox.showwarning(
                "Attention", 
                f"Aucune appréciation {code} trouvée pour "
                f"{bulletin.eleve.nom} {bulletin.eleve.prenom}.\n"
                "Impossible de générer l'appréciation générale."
            )
            return
        
        # Créer une fenêtre de progression simple
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Génération en cours...")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text=f"Génération pour {bulletin.eleve.nom} {bulletin.eleve.prenom}", 
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill=tk.X)
        progress_bar.start()
        
        # Traitement en thread
        import threading
        
        def process_current_bulletin():
            try:
                general_appreciation = openai_service.generate_general_appreciation(
                    appreciations,
                    bulletin.eleve.nom,
                    bulletin.eleve.prenom,
                    semester=self.semester
                )
                bulletin.set_appreciation_generale(code, general_appreciation)
                
                progress_window.destroy()
                
                # Sauvegarder automatiquement en préservant les valeurs générées
                self._save_changes_preserve_generated()
                
                # Rafraîchir l'affichage en conservant la sélection
                self._refresh_display_with_selection()
                
                messagebox.showinfo(
                    "Génération terminée", 
                    f"Appréciation générale {code} générée pour "
                    f"{bulletin.eleve.nom} {bulletin.eleve.prenom} !"
                )
                
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("Erreur", f"Erreur pendant la génération:\n{str(e)}")
        
        thread = threading.Thread(target=process_current_bulletin)
        thread.daemon = True
        thread.start()
    
    def _save_changes(self, preserve_generated=False):
        """Sauvegarde
        Args:
            preserve_generated: Si True, ne pas écraser les appréciations générales avec le contenu des TextBox
        """
        if not self.bulletins or not self.json_file_path:
            messagebox.showerror("Erreur", "Aucun fichier chargé")
            return
        
        try:
            if not preserve_generated:
                # Sauvegarde normale : synchroniser avec les TextBox (par période)
                bulletin = self.bulletins[self.current_bulletin_index]
                for code, text in self.general_texts.items():
                    contenu = text.get('1.0', tk.END).strip()
                    bulletin.set_appreciation_generale(code, contenu or None)
            
            save_output_json(
                self.bulletins,
                self.json_file_path,
                metadata=self._metadata_for_save(),
            )
            
            self._update_status("✅ Modifications sauvegardées")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder:\n{str(e)}")
    
    def _save_changes_preserve_generated(self):
        """Sauvegarde en préservant les appréciations générales générées"""
        self._save_changes(preserve_generated=True)
    
    def _update_status(self, message: str):
        """Met à jour le statut"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def _return_to_main(self):
        """Retour principal"""
        if self.parent_window:
            self.root.destroy()
        else:
            self._on_closing()
    
    def _on_closing(self):
        """Fermeture"""
        if messagebox.askokcancel("Fermer", "Voulez-vous fermer la fenêtre d'édition?"):
            self.root.destroy()
    
    def run(self):
        """Lance la fenêtre"""
        self.root.mainloop()


def main():
    """Test de la fenêtre"""
    test_files = ["output.json", "output_demo.json", "exemples/output.json"]
    
    json_file = None
    for file_path in test_files:
        if os.path.exists(file_path):
            json_file = file_path
            break
    
    app = EditionWindow(json_file_path=json_file)
    app.run()


if __name__ == "__main__":
    main() 