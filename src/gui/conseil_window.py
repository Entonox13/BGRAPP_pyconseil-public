#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fenêtre conseil de classe de l'application BGRAPP Pyconseil
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any

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
    from ..services.period_history import (
        resolve_period_links,
        load_history_bulletins,
        build_display_bulletins,
    )
    from .period_links_panel import open_period_links_dialog
    from ..utils.paths import get_documents_dir
    from . import theme
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
    from services.period_history import (
        resolve_period_links,
        load_history_bulletins,
        build_display_bulletins,
    )
    sys.path.insert(0, str(Path(__file__).parent))
    from period_links_panel import open_period_links_dialog
    from utils.paths import get_documents_dir
    from gui import theme


class ConseilWindow:
    """Fenêtre conseil de classe"""
    
    def __init__(self, parent_window=None, json_file_path: Optional[str] = None,
                 initial_semester: Optional[Period] = None):
        self.parent_window = parent_window
        self.json_file_path = json_file_path
        self.bulletins: List[Bulletin] = []
        self.current_bulletin_index: int = 0
        self.conseil_data: Dict[str, Any] = {}
        self.period: Period = initial_semester or Period.S2
        # Période imposée par l'appelant (sélection manuelle dans la fenêtre
        # principale) : prioritaire sur la détection automatique au 1er chargement.
        self._forced_initial_period: Optional[Period] = initial_semester
        self.period_codes: List[str] = self._default_period_codes()
        self.metadata: Dict[str, Any] = {}
        self.general_widgets: List[Any] = []
        
        # Créer la fenêtre
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.root.title("BGRAPP Pyconseil - Conseil de Classe")
        
        # Configuration pour écran 1080p - approche plus robuste
        self.is_fullscreen = False
        self._setup_fullscreen_window()
        theme.setup_root_scaling(self.root)
        
        # Raccourcis pour quitter le plein écran (Echap)
        self.root.bind('<Escape>', lambda e: self._toggle_fullscreen())
        self.root.bind('<F11>', lambda e: self._toggle_fullscreen())
        
        self._setup_styles()
        self._create_interface()
        self._apply_period_ui_state()
        
        if json_file_path and os.path.exists(json_file_path):
            self._load_bulletins_from_file(json_file_path)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_fullscreen_window(self):
        """Configure la fenêtre pour le mode plein écran de manière robuste"""
        try:
            # Obtenir la taille de l'écran
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Mode plein écran par défaut
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            
            # Tenter le mode plein écran natif
            try:
                self.root.attributes('-fullscreen', True)
                self.is_fullscreen = True
            except tk.TclError:
                # Si fullscreen ne fonctionne pas, maximiser la fenêtre
                try:
                    self.root.state('zoomed')  # Windows
                except tk.TclError:
                    # Fallback pour Linux : géométrie maximale sans décoration
                    self.root.overrideredirect(True)  # Enlever les décorations de fenêtre
                    self.root.geometry(f"{screen_width}x{screen_height}+0+0")
                    self.is_fullscreen = True
                    
        except Exception as e:
            # Fallback ultime : taille 1080p standard
            self.root.geometry("1920x1080")
            print(f"Mode plein écran non disponible, utilisation de la taille 1920x1080: {e}")
    
    def _toggle_fullscreen(self):
        """Bascule entre plein écran et mode fenêtré de manière robuste"""
        try:
            if self.is_fullscreen:
                # Sortir du plein écran
                self.root.attributes('-fullscreen', False)
                self.root.overrideredirect(False)  # Remettre les décorations
                self.root.geometry("1600x900+160+90")  # Taille réduite centrée
                self.is_fullscreen = False
            else:
                # Entrer en plein écran
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                
                try:
                    self.root.attributes('-fullscreen', True)
                except tk.TclError:
                    self.root.overrideredirect(True)
                    self.root.geometry(f"{screen_width}x{screen_height}+0+0")
                
                self.is_fullscreen = True
                
        except Exception as e:
            print(f"Erreur lors du basculement plein écran: {e}")
            # Fallback : juste redimensionner
            if self.is_fullscreen:
                self.root.geometry("1600x900")
                self.is_fullscreen = False
            else:
                self.root.geometry("1920x1080")
                self.is_fullscreen = True
    
    def _setup_styles(self):
        """Configure les styles de l'interface"""
        style = ttk.Style()
        theme.apply_theme(style, conseil=True)
    
    def _insert_html_text(self, text_widget, html_content):
        """
        Insère du contenu HTML dans un widget Text avec formatage des balises.
        
        Args:
            text_widget: Widget Text tkinter
            html_content: Contenu avec balises HTML à interpréter
        """
        if not html_content:
            return
        
        # Configuration des tags pour les styles
        text_widget.tag_configure(
            "positif",
            foreground=theme.html_tag_foreground("positif"),
            font=theme.font_html_tag("positif"),
        )
        text_widget.tag_configure(
            "negatif",
            foreground=theme.html_tag_foreground("negatif"),
            font=theme.font_html_tag("negatif"),
        )
        text_widget.tag_configure(
            "normal",
            foreground=theme.html_tag_foreground("normal"),
            font=theme.font_html_tag("normal"),
        )
        
        # Pattern pour extraire les balises span avec classes
        span_pattern = r'<span class="([^"]+)">([^<]+)</span>'
        
        # Diviser le texte en segments avec et sans balises
        last_end = 0
        for match in re.finditer(span_pattern, html_content):
            # Ajouter le texte avant la balise (sans formatage)
            if match.start() > last_end:
                plain_text = html_content[last_end:match.start()]
                text_widget.insert(tk.END, plain_text, "normal")
            
            # Ajouter le texte avec formatage selon la classe
            class_name = match.group(1)
            content = match.group(2)
            
            if class_name == "positif":
                text_widget.insert(tk.END, content, "positif")
            elif class_name == "negatif":
                text_widget.insert(tk.END, content, "negatif")
            else:
                text_widget.insert(tk.END, content, "normal")
            
            last_end = match.end()
        
        # Ajouter le texte restant après la dernière balise
        if last_end < len(html_content):
            remaining_text = html_content[last_end:]
            text_widget.insert(tk.END, remaining_text, "normal")
    
    def _create_interface(self):
        """Crée l'interface optimisée pour 1080p"""
        # Frame principal avec padding réduit pour maximiser l'espace
        main_frame = ttk.Frame(self.root, padding=theme.PADDING_COMPACT)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        self._create_toolbar(main_frame, 0)
        
        # Zone principale - layout horizontal optimisé
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        content_frame.columnconfigure(1, weight=4)  # Zone conseil plus large
        content_frame.rowconfigure(0, weight=1)
        
        self._create_navigation_panel(content_frame, 0, 0)
        self._create_conseil_view(content_frame, 0, 1)
        
        self._create_action_bar(main_frame, 2)

    @property
    def semester(self) -> Period:
        """Alias rétro-compatible de la période courante."""
        return self.period

    @semester.setter
    def semester(self, value: Period) -> None:
        self.period = value

    def _default_period_codes(self) -> List[str]:
        """Codes de période par défaut selon le système courant."""
        system = self.period.system if hasattr(self, 'period') else PeriodSystem.SEMESTRE
        return [p.value for p in periods_for_system(system)]

    def _determine_period(self, metadata: Optional[Dict[str, Any]], data: List[Dict[str, Any]]) -> Period:
        """Détermine la période active à partir des métadonnées ou du contenu du JSON."""
        period = period_from_metadata(metadata)
        if period:
            return period
        return infer_period_from_bulletins_data(data)

    def _merge_linked_periods(self, current_bulletins: List[Bulletin]) -> List[Bulletin]:
        """
        Fusionne (lecture seule) les bulletins des périodes liées dans une copie
        des bulletins courants pour reconstruire la vue multi-périodes.
        """
        if not self.json_file_path:
            return current_bulletins
        try:
            links = resolve_period_links(self.json_file_path, self.metadata, self.period.value)
            if not links:
                return current_bulletins
            history = load_history_bulletins(links)
            return build_display_bulletins(current_bulletins, history, self.period.value)
        except Exception:
            return current_bulletins

    def _compute_period_codes(self) -> List[str]:
        """
        Calcule les codes de période à afficher : toutes les périodes
        réellement présentes dans les bulletins (ordre canonique).

        On affiche toute période présente, quel que soit son système, afin
        de ne jamais masquer de données (ex: des données S1 mélangées à une
        structure trimestre ne doivent pas disparaître).
        """
        present = set()
        for bulletin in self.bulletins:
            for appreciation in bulletin.matieres.values():
                present.update(appreciation.periodes.keys())
            for code, texte in bulletin.appreciations_generales.items():
                if texte and code in PERIOD_CODES:
                    present.add(code)
        present.add(self.period.value)

        system = period_system_from_metadata(self.metadata) or self.period.system
        if system == PeriodSystem.TRIMESTRE:
            present.discard("S1")
            present.discard("S2")
        
        if present:
            return [c for c in PERIOD_CODES if c in present]
        
        # Aucune donnée : colonnes par défaut du système (métadonnées/période)
        system = period_system_from_metadata(self.metadata) or self.period.system
        return [p.value for p in periods_for_system(system)]

    def _apply_period_ui_state(self):
        """Reconstruit les colonnes/sections selon les périodes présentes."""
        if not hasattr(self, 'synthesis_tree'):
            return
        
        self.period_codes = self._compute_period_codes()
        self._configure_synthesis_columns()
        if hasattr(self, 'general_frame'):
            self._build_general_appreciation_widgets()
        self._refresh_period_selector()
    
    def _create_toolbar(self, parent, row):
        """Crée la barre d'outils"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        toolbar_frame.columnconfigure(3, weight=1)
        
        # Titre plus visible
        ttk.Label(toolbar_frame, text=theme.TITLE_CONSEIL, style='Title.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        # Bouton charger
        self.load_btn = ttk.Button(toolbar_frame, text=theme.BTN_LOAD_JSON, command=self._load_json_file)
        self.load_btn.grid(row=0, column=1, padx=(20, 10))

        # Bouton périodes liées (autres JSON)
        self.period_links_btn = ttk.Button(toolbar_frame, text=theme.BTN_PERIOD_LINKS, command=self._open_period_links)
        self.period_links_btn.grid(row=0, column=6, padx=(10, 10))
        
        # Sélecteur manuel de période (trimestre/semestre)
        self._build_period_selector(toolbar_frame, 2)
        
        # Indicateur position plus visible
        self.position_label = ttk.Label(toolbar_frame, text="Aucun bulletin chargé", style='Large.TLabel')
        self.position_label.grid(row=0, column=3, sticky=tk.E, padx=(0, 20))
        
        # Raccourcis clavier
        help_label = ttk.Label(toolbar_frame, text="[Échap/F11: Plein écran]", style='Info.TLabel')
        help_label.grid(row=0, column=4, sticky=tk.E, padx=(0, 10))
        
        # Bouton retour
        self.back_btn = ttk.Button(toolbar_frame, text=theme.BTN_BACK, command=self._return_to_main)
        self.back_btn.grid(row=0, column=5, padx=(10, 0))

    def _build_period_selector(self, parent, column):
        """Crée le sélecteur manuel de période courante."""
        selector_frame = ttk.Frame(parent)
        selector_frame.grid(row=0, column=column, padx=(0, 15))
        ttk.Label(selector_frame, text="Période :", style='Info.TLabel').grid(
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
        """Synchronise le sélecteur avec les périodes disponibles."""
        if not hasattr(self, 'period_combo'):
            return
        codes = list(self.period_codes) if self.period_codes else [self.period.value]
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
        """Applique la période choisie manuellement par l'utilisateur."""
        index = self.period_combo.current()
        codes = getattr(self, '_period_choice_codes', [])
        if index < 0 or index >= len(codes):
            return
        selected = Period.from_code(codes[index])
        if not selected or selected == self.period:
            return
        self.period = selected
        self._apply_period_ui_state()
        self._update_display()
    
    def _create_navigation_panel(self, parent, row, column):
        """Crée le panneau de navigation optimisé"""
        nav_frame = ttk.LabelFrame(parent, text="Navigation", padding="5")
        nav_frame.grid(row=row, column=column, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        nav_frame.columnconfigure(0, weight=1)
        nav_frame.rowconfigure(1, weight=1)
        
        # Configuration de largeur fixe mais optimisée
        nav_frame.configure(width=theme.NAV_PANEL_WIDTH)
        
        # Boutons navigation
        nav_buttons_frame = ttk.Frame(nav_frame)
        nav_buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        nav_buttons_frame.columnconfigure(1, weight=1)
        
        self.prev_btn = ttk.Button(nav_buttons_frame, text=theme.BTN_PREV, command=self._previous_bulletin, state='disabled')
        self.prev_btn.grid(row=0, column=0, sticky=tk.W)
        
        self.next_btn = ttk.Button(nav_buttons_frame, text=theme.BTN_NEXT, command=self._next_bulletin, state='disabled')
        self.next_btn.grid(row=0, column=2, sticky=tk.E)
        
        # Liste bulletins avec plus de hauteur
        self.bulletin_list = tk.Listbox(nav_frame, height=25, font=theme.font_body())
        self.bulletin_list.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.bulletin_list.bind('<<ListboxSelect>>', self._on_bulletin_select)
        
        # Scrollbar
        list_scrollbar = ttk.Scrollbar(nav_frame, orient=tk.VERTICAL, command=self.bulletin_list.yview)
        list_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.bulletin_list.configure(yscrollcommand=list_scrollbar.set)
    
    def _create_conseil_view(self, parent, row, column):
        """Crée la vue conseil optimisée pour l'espace"""
        conseil_frame = ttk.LabelFrame(parent, text="Vue Conseil de Classe", padding="5")
        conseil_frame.grid(row=row, column=column, sticky=(tk.W, tk.E, tk.N, tk.S))
        conseil_frame.columnconfigure(0, weight=1)
        conseil_frame.rowconfigure(1, weight=3)
        conseil_frame.rowconfigure(2, weight=1)
        
        # Informations élève en haut (plus compactes)
        self._create_student_info(conseil_frame, 0)
        
        # Vue d'ensemble des matières (zone principale)
        self._create_subjects_overview(conseil_frame, 1)
        
        # Appréciation générale en bas (plus compacte)
        self._create_general_appreciation(conseil_frame, 2)
    
    def _create_student_info(self, parent, row):
        """Crée la section informations élève compacte"""
        info_frame = ttk.LabelFrame(parent, text="Informations Élève", padding="3")
        info_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        info_frame.columnconfigure(5, weight=1)
        
        # Layout horizontal compact
        ttk.Label(info_frame, text="Nom:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.nom_label = ttk.Label(info_frame, text="-", style='Large.TLabel')
        self.nom_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(info_frame, text="Prénom:", style='Header.TLabel').grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.prenom_label = ttk.Label(info_frame, text="-", style='Large.TLabel')
        self.prenom_label.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(info_frame, text="Classe:", style='Header.TLabel').grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.classe_label = ttk.Label(info_frame, text="-", style='Large.TLabel')
        self.classe_label.grid(row=0, column=5, sticky=tk.W)
    
    def _create_subjects_overview(self, parent, row):
        """Crée la vue d'ensemble des matières optimisée"""
        subjects_frame = ttk.LabelFrame(parent, text="Vue d'Ensemble des Matières", padding="5")
        subjects_frame.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        subjects_frame.columnconfigure(0, weight=1)
        subjects_frame.rowconfigure(0, weight=1)
        
        # Notebook pour organiser les vues
        self.overview_notebook = ttk.Notebook(subjects_frame)
        self.overview_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Onglet vue synthèse
        self._create_synthesis_tab()
        
        # Onglet vue détaillée (optimisée pour les appréciations)
        self._create_detailed_tab()
    
    def _create_synthesis_tab(self):
        """Crée l'onglet vue synthèse"""
        synthesis_frame = ttk.Frame(self.overview_notebook, padding="5")
        self.overview_notebook.add(synthesis_frame, text=theme.TAB_SYNTHESIS)
        synthesis_frame.columnconfigure(0, weight=1)
        synthesis_frame.rowconfigure(0, weight=1)
        
        # TreeView pour la synthèse : colonnes configurées dynamiquement
        # selon les périodes présentes (S1/S2 ou T1/T2/T3).
        self.synthesis_tree = ttk.Treeview(synthesis_frame, show='headings', height=20)
        self._configure_synthesis_columns()
        
        self.synthesis_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        synthesis_scrollbar = ttk.Scrollbar(synthesis_frame, orient=tk.VERTICAL, command=self.synthesis_tree.yview)
        synthesis_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.synthesis_tree.configure(yscrollcommand=synthesis_scrollbar.set)
    
    def _configure_synthesis_columns(self):
        """Configure dynamiquement les colonnes du tableau de synthèse."""
        if not hasattr(self, 'synthesis_tree'):
            return
        
        columns = ['matiere']
        headings = {'matiere': 'Matière'}
        widths = {'matiere': 240}
        
        for code in self.period_codes:
            for prefix, label, width in (
                ('moy', 'Moy.', 108),
                ('abs', 'Abs.', 96),
                ('ret', 'Ret.', 84),
            ):
                col = f'{prefix}_{code.lower()}'
                columns.append(col)
                headings[col] = f'{label} {code}'
                widths[col] = width
        
        # Colonne évolution si au moins deux périodes
        if len(self.period_codes) >= 2:
            columns.append('evolution')
            headings['evolution'] = 'Évolution'
            widths['evolution'] = 144
        
        self.synthesis_tree_columns = tuple(columns)
        self.synthesis_tree.configure(columns=self.synthesis_tree_columns)
        stretch_cols = {'matiere'}
        if 'evolution' in columns:
            stretch_cols.add('evolution')
        for col in columns:
            self.synthesis_tree.heading(col, text=headings[col])
            self.synthesis_tree.column(col, width=widths[col], stretch=col in stretch_cols)
    
    def _create_detailed_tab(self):
        """Crée l'onglet vue détaillée optimisé pour les appréciations"""
        detailed_frame = ttk.Frame(self.overview_notebook, padding="5")
        self.overview_notebook.add(detailed_frame, text=theme.TAB_DETAILS)
        detailed_frame.columnconfigure(0, weight=1)
        detailed_frame.rowconfigure(0, weight=1)
        
        # Créer un canvas avec scrollbar pour la vue détaillée
        self.detailed_canvas = tk.Canvas(detailed_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(detailed_frame, orient="vertical", command=self.detailed_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.detailed_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.detailed_canvas.configure(scrollregion=self.detailed_canvas.bbox("all"))
        )
        
        self.detailed_canvas_window = self.detailed_canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.detailed_canvas.configure(yscrollcommand=scrollbar.set)
        self.detailed_canvas.bind("<Configure>", self._sync_detailed_canvas_width)
        
        # Configuration pour utiliser tout l'espace disponible
        self.scrollable_frame.columnconfigure(0, weight=1)
        
        self.detailed_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Binding pour le scroll avec la molette
        self.detailed_canvas.bind(
            "<MouseWheel>", lambda e: self.detailed_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )
        
        # Cette zone sera remplie dynamiquement
        self.detailed_widgets = []
    
    def _sync_detailed_canvas_width(self, event=None):
        """Adapte la largeur du contenu défilant à celle du canvas."""
        if not hasattr(self, "detailed_canvas"):
            return
        canvas_width = self.detailed_canvas.winfo_width()
        if canvas_width > 1:
            self.detailed_canvas.itemconfigure(self.detailed_canvas_window, width=canvas_width)
    
    def _create_general_appreciation(self, parent, row):
        """Crée la section appréciation générale (une zone par période)."""
        self.general_frame = ttk.LabelFrame(parent, text="Appréciation Générale", padding="3")
        self.general_frame.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        self.general_frame.columnconfigure(0, weight=1)
        
        # Les zones de texte par période sont construites dynamiquement
        self.general_texts: Dict[str, tk.Text] = {}
        self._build_general_appreciation_widgets()
    
    def _build_general_appreciation_widgets(self):
        """(Re)construit les zones d'appréciation générale selon les périodes."""
        for widget in self.general_widgets:
            widget.destroy()
        self.general_widgets.clear()
        self.general_texts = {}
        
        col = 0
        for code in self.period_codes:
            label = ttk.Label(self.general_frame, text=f"{code}:", style='Header.TLabel')
            label.grid(row=0, column=col, sticky=(tk.W, tk.N), padx=(5, 5))
            self.general_widgets.append(label)
            col += 1
            
            text = tk.Text(
                self.general_frame,
                height=7,
                wrap=tk.WORD,
                state='disabled',
                font=theme.font_body(),
            )
            text.grid(row=0, column=col, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2, padx=(0, 10))
            self.general_frame.columnconfigure(col, weight=1)
            self.general_widgets.append(text)
            self.general_texts[code] = text
            col += 1
    
    def _load_json_file(self):
        """Charge un fichier JSON"""
        file_path = filedialog.askopenfilename(
            title="Choisir le fichier JSON",
            filetypes=[("Fichiers JSON", "*.json")],
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
            self.period.value,
            on_change=lambda: self._load_bulletins_from_file(self.json_file_path),
        )
    
    def _load_bulletins_from_file(self, file_path: str):
        """Charge les bulletins depuis un fichier JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            metadata = {}
            data = raw_data
            if raw_data and isinstance(raw_data[0], dict) and '_metadata' in raw_data[0]:
                metadata = raw_data[0].get('_metadata') or {}
                data = raw_data[1:]
            
            self.metadata = metadata
            if self._forced_initial_period is not None:
                # Respecter la période choisie manuellement (consommée une fois)
                self.period = self._forced_initial_period
                self._forced_initial_period = None
            else:
                self.period = self._determine_period(metadata, data)
            
            current_bulletins = []
            for bulletin_data in data:
                bulletin = Bulletin.from_dict(bulletin_data)
                current_bulletins.append(bulletin)

            self.json_file_path = file_path
            # Fusionner (lecture seule) les periodes liees pour la vue d'ensemble
            self.bulletins = self._merge_linked_periods(current_bulletins)
            
            # Adapter les colonnes/sections aux périodes réellement présentes
            self._apply_period_ui_state()
            
            self._update_bulletin_list()
            self._update_status(f"Chargé {len(self.bulletins)} bulletins depuis {os.path.basename(file_path)}")
            
            # Activer les boutons
            self.export_btn.configure(state='normal')
            self.print_btn.configure(state='normal')
            
            if self.bulletins:
                self.current_bulletin_index = 0
                self._update_display()
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement du fichier:\n{str(e)}")
            self._update_status("Erreur de chargement")
    
    def _update_bulletin_list(self):
        """Met à jour la liste des bulletins"""
        self.bulletin_list.delete(0, tk.END)
        for i, bulletin in enumerate(self.bulletins):
            self.bulletin_list.insert(tk.END, f"{bulletin.eleve.nom} {bulletin.eleve.prenom}")
        
        self._update_navigation_buttons()
        self._update_position_indicator()
    
    def _update_display(self):
        """Met à jour l'affichage"""
        if not self.bulletins or self.current_bulletin_index >= len(self.bulletins):
            self._clear_display()
            return
        
        bulletin = self.bulletins[self.current_bulletin_index]
        
        # Mettre à jour les informations élève
        self.nom_label.configure(text=bulletin.eleve.nom)
        self.prenom_label.configure(text=bulletin.eleve.prenom)
        self.classe_label.configure(text=bulletin.eleve.classe)
        
        # Mettre à jour la vue synthèse
        self._update_synthesis_view(bulletin)
        
        # Mettre à jour la vue détaillée
        self._update_detailed_view(bulletin)
        
        # Mettre à jour l'appréciation générale
        self._update_general_view(bulletin)
        
        # Mettre à jour la sélection dans la liste
        self.bulletin_list.selection_clear(0, tk.END)
        self.bulletin_list.selection_set(self.current_bulletin_index)
        self.bulletin_list.see(self.current_bulletin_index)
        
        self._update_position_indicator()
    
    def _update_synthesis_view(self, bulletin):
        """Met à jour la vue synthèse (colonnes dynamiques par période)."""
        # Vider le TreeView
        for item in self.synthesis_tree.get_children():
            self.synthesis_tree.delete(item)
        
        for matiere_nom, appreciation in bulletin.matieres.items():
            values = [appreciation.matiere]
            for code in self.period_codes:
                periode = appreciation.get_periode(code)
                moyenne = periode.moyenne if periode else None
                absence = periode.heures_absence if periode else None
                retards = periode.retards if periode else None
                values.append(f"{moyenne:.2f}" if isinstance(moyenne, (int, float)) else (moyenne or "-"))
                values.append(absence if absence else "-")
                values.append(str(retards) if retards is not None else "-")
            
            if len(self.period_codes) >= 2:
                values.append(self._compute_evolution(appreciation))
            
            self.synthesis_tree.insert('', 'end', values=tuple(values))
    
    def _compute_evolution(self, appreciation) -> str:
        """Calcule l'évolution entre les deux dernières périodes disponibles."""
        moyennes = []
        for code in self.period_codes:
            periode = appreciation.get_periode(code)
            if periode and periode.moyenne is not None:
                moyennes.append(periode.moyenne)
        if len(moyennes) < 2:
            return "-"
        try:
            diff = float(moyennes[-1]) - float(moyennes[-2])
            if diff > 0:
                return f"+{diff:.2f} \u2191"
            elif diff < 0:
                return f"{diff:.2f} \u2193"
            return "= \u2192"
        except (ValueError, TypeError):
            return "-"
    
    def _update_detailed_view(self, bulletin):
        """Met à jour la vue détaillée optimisée pour les appréciations"""
        # Nettoyer la vue précédente
        for widget in self.detailed_widgets:
            widget.destroy()
        self.detailed_widgets.clear()
        
        # Créer une vue détaillée pour chaque matière avec mise en page optimisée
        row = 0
        for matiere_nom, appreciation in bulletin.matieres.items():
            # Frame pour la matière avec plus d'espace
            matiere_frame = ttk.LabelFrame(self.scrollable_frame, text=appreciation.matiere, padding="8")
            matiere_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=8, padx=5)
            self.detailed_widgets.append(matiere_frame)
            
            # Statistiques par période : une colonne par trimestre/semestre
            info_frame = ttk.Frame(matiere_frame)
            info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            for period_idx, code in enumerate(self.period_codes):
                info_frame.columnconfigure(period_idx, weight=1, uniform="period_stats")
                periode = appreciation.get_periode(code)
                moyenne = periode.moyenne if periode else None
                absence = periode.heures_absence if periode else None
                retards = periode.retards if periode else None
                moy_text = f"{moyenne:.2f}" if isinstance(moyenne, (int, float)) else (moyenne or "-")
                
                period_info = ttk.Frame(info_frame, padding=(0, 0, 4, 0))
                period_info.grid(row=0, column=period_idx, sticky=(tk.W, tk.E))
                ttk.Label(period_info, text=code, style='Header.TLabel').grid(
                    row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 2)
                )
                ttk.Label(period_info, text="Moy.:", style='Info.TLabel').grid(row=1, column=0, sticky=tk.W)
                ttk.Label(period_info, text=moy_text, style='Large.TLabel').grid(row=1, column=1, sticky=tk.W, padx=(4, 0))
                ttk.Label(period_info, text="Abs.:", style='Info.TLabel').grid(row=2, column=0, sticky=tk.W)
                ttk.Label(period_info, text=absence if absence else "-", style='Large.TLabel').grid(
                    row=2, column=1, sticky=tk.W, padx=(4, 0)
                )
                ttk.Label(period_info, text="Ret.:", style='Info.TLabel').grid(row=3, column=0, sticky=tk.W)
                ttk.Label(period_info, text=str(retards) if retards is not None else "-", style='Large.TLabel').grid(
                    row=3, column=1, sticky=tk.W, padx=(4, 0)
                )
            
            # Appréciations par période : colonnes de largeur égale
            appreciations_frame = ttk.Frame(matiere_frame)
            appreciations_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
            matiere_frame.columnconfigure(0, weight=1)
            
            periods_with_text = []
            for code in self.period_codes:
                periode = appreciation.get_periode(code)
                texte = periode.appreciation if periode else None
                if texte:
                    periods_with_text.append((code, texte))
            
            for appr_col, (code, texte) in enumerate(periods_with_text):
                appreciations_frame.columnconfigure(appr_col, weight=1, uniform="period_appr")
                periode_frame = ttk.LabelFrame(
                    appreciations_frame, text=f"Appréciation {code}", padding="4"
                )
                periode_frame.grid(
                    row=0, column=appr_col, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(2, 2)
                )
                periode_frame.columnconfigure(0, weight=1)
                periode_frame.rowconfigure(0, weight=1)
                
                appr_text = tk.Text(
                    periode_frame,
                    height=8,
                    wrap=tk.WORD,
                    state='disabled',
                    font=theme.font_body(),
                )
                appr_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
                
                appr_scrollbar = ttk.Scrollbar(periode_frame, orient=tk.VERTICAL, command=appr_text.yview)
                appr_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
                appr_text.configure(yscrollcommand=appr_scrollbar.set)
                
                appr_text.configure(state='normal')
                appr_text.delete('1.0', tk.END)
                self._insert_html_text(appr_text, texte)
                appr_text.configure(state='disabled')
                self.detailed_widgets.append(appr_text)
                self.detailed_widgets.append(periode_frame)
            
            # Configuration pour que les appréciations prennent toute la hauteur disponible
            matiere_frame.rowconfigure(1, weight=1)
            appreciations_frame.rowconfigure(0, weight=1)
            
            row += 1
        
        self.root.after_idle(self._sync_detailed_canvas_width)
    
    def _update_general_view(self, bulletin):
        """Met à jour la vue appréciation générale (une zone par période)."""
        for code, text_widget in self.general_texts.items():
            text_widget.configure(state='normal')
            text_widget.delete('1.0', tk.END)
            texte = bulletin.get_appreciation_generale(code)
            if texte:
                self._insert_html_text(text_widget, texte)
            text_widget.configure(state='disabled')
    
    def _clear_display(self):
        """Vide l'affichage"""
        self.nom_label.configure(text="-")
        self.prenom_label.configure(text="-")
        self.classe_label.configure(text="-")
        
        # Vider les vues
        for item in self.synthesis_tree.get_children():
            self.synthesis_tree.delete(item)
        
        for widget in self.detailed_widgets:
            widget.destroy()
        self.detailed_widgets.clear()
        
        for text_widget in self.general_texts.values():
            text_widget.configure(state='normal')
            text_widget.delete('1.0', tk.END)
            text_widget.configure(state='disabled')
    
    def _previous_bulletin(self):
        """Bulletin précédent"""
        if self.current_bulletin_index > 0:
            self.current_bulletin_index -= 1
            self._update_display()
            self._update_navigation_buttons()
    
    def _next_bulletin(self):
        """Bulletin suivant"""
        if self.current_bulletin_index < len(self.bulletins) - 1:
            self.current_bulletin_index += 1
            self._update_display()
            self._update_navigation_buttons()
    
    def _on_bulletin_select(self, event):
        """Gestion de la sélection d'un bulletin dans la liste"""
        selection = self.bulletin_list.curselection()
        if selection:
            self.current_bulletin_index = selection[0]
            self._update_display()
            self._update_navigation_buttons()
    
    def _update_navigation_buttons(self):
        """Met à jour l'état des boutons de navigation"""
        if not self.bulletins:
            self.prev_btn.configure(state='disabled')
            self.next_btn.configure(state='disabled')
        else:
            self.prev_btn.configure(state='normal' if self.current_bulletin_index > 0 else 'disabled')
            self.next_btn.configure(state='normal' if self.current_bulletin_index < len(self.bulletins) - 1 else 'disabled')
    
    def _update_position_indicator(self):
        """Met à jour l'indicateur de position"""
        if self.bulletins:
            self.position_label.configure(text=f"Bulletin {self.current_bulletin_index + 1} / {len(self.bulletins)}")
        else:
            self.position_label.configure(text="Aucun bulletin chargé")
    
    def _export_conseil(self):
        """Exporte les données de conseil"""
        messagebox.showinfo("Export", "Fonction d'export à implémenter")
    
    def _print_conseil(self):
        """Imprime les données de conseil"""
        messagebox.showinfo("Impression", "Fonction d'impression à implémenter")
    
    def _update_status(self, message: str):
        """Met à jour le statut"""
        self.status_label.configure(text=message)
    
    def _return_to_main(self):
        """Retour à la fenêtre principale"""
        try:
            # Logique simplifiée comme dans EditionWindow
            if self.parent_window:
                self.root.destroy()
            else:
                self._on_closing()
                
        except Exception as e:
            print(f"{theme.LOG_ERR} Erreur dans _return_to_main: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_closing(self):
        """Gestion de la fermeture"""
        try:
            # Logique simplifiée comme dans EditionWindow
            from tkinter import messagebox
            if messagebox.askokcancel("Fermer", "Voulez-vous fermer la fenêtre de conseil?"):
                self.root.destroy()
                
        except Exception as e:
            print(f"{theme.LOG_ERR} Erreur dans _on_closing: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_action_bar(self, parent, row):
        """Crée la barre d'actions optimisée"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        action_frame.columnconfigure(3, weight=1)
        
        # Boutons d'action plus espacés
        self.export_btn = ttk.Button(action_frame, text=theme.BTN_EXPORT, command=self._export_conseil, state='disabled')
        self.export_btn.grid(row=0, column=0, padx=(0, 15))
        
        self.print_btn = ttk.Button(action_frame, text=theme.BTN_PRINT, command=self._print_conseil, state='disabled')
        self.print_btn.grid(row=0, column=1, padx=(0, 15))
        
        # Bouton plein écran
        self.fullscreen_btn = ttk.Button(action_frame, text=theme.BTN_FULLSCREEN, command=self._toggle_fullscreen)
        self.fullscreen_btn.grid(row=0, column=2, padx=(0, 15))
        
        # Statut plus visible
        self.status_label = ttk.Label(action_frame, text="Prêt", style='Large.TLabel')
        self.status_label.grid(row=0, column=3, sticky=tk.E)
    
    def run(self):
        """Lance l'interface"""
        self.root.mainloop()


def main():
    """Point d'entrée pour les tests"""
    window = ConseilWindow()
    window.run()


if __name__ == "__main__":
    main() 