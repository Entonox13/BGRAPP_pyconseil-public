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
    from ..models.bulletin import Bulletin, Eleve, AppreciationMatiere
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models.bulletin import Bulletin, Eleve, AppreciationMatiere


class ConseilWindow:
    """Fenêtre conseil de classe"""
    
    def __init__(self, parent_window=None, json_file_path: Optional[str] = None):
        self.parent_window = parent_window
        self.json_file_path = json_file_path
        self.bulletins: List[Bulletin] = []
        self.current_bulletin_index: int = 0
        self.conseil_data: Dict[str, Any] = {}
        
        # Créer la fenêtre
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.root.title("BGRAPP Pyconseil - Conseil de Classe")
        
        # Configuration pour écran 1080p - approche plus robuste
        self.is_fullscreen = False
        self._setup_fullscreen_window()
        
        # Raccourcis pour quitter le plein écran (Echap)
        self.root.bind('<Escape>', lambda e: self._toggle_fullscreen())
        self.root.bind('<F11>', lambda e: self._toggle_fullscreen())
        
        self._setup_styles()
        self._create_interface()
        
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
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 11))
        style.configure('Header.TLabel', font=('Arial', 11, 'bold'))
        style.configure('Large.TLabel', font=('Arial', 12))
    
    def _insert_html_text(self, text_widget, html_content):
        """
        Insère du contenu HTML dans un widget Text avec formatage des balises.
        
        Args:
            text_widget: Widget Text tkinter
            html_content: Contenu avec balises HTML à interpréter
        """
        if not html_content:
            return
        
        # Configuration des tags pour les styles (tailles augmentées)
        text_widget.tag_configure("positif", foreground="green", font=('Arial', 11, 'bold'))
        text_widget.tag_configure("negatif", foreground="red", font=('Arial', 11, 'bold'))
        text_widget.tag_configure("normal", foreground="black", font=('Arial', 11))
        
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
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        self._create_toolbar(main_frame, 0)
        
        # Zone principale - layout horizontal optimisé
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        content_frame.columnconfigure(1, weight=3)  # Zone conseil plus large
        content_frame.rowconfigure(0, weight=1)
        
        self._create_navigation_panel(content_frame, 0, 0)
        self._create_conseil_view(content_frame, 0, 1)
        
        self._create_action_bar(main_frame, 2)
    
    def _create_toolbar(self, parent, row):
        """Crée la barre d'outils"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        toolbar_frame.columnconfigure(2, weight=1)
        
        # Titre plus visible
        ttk.Label(toolbar_frame, text="🏛️ Conseil de Classe - Vue Plein Écran", style='Title.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        # Bouton charger
        self.load_btn = ttk.Button(toolbar_frame, text="📂 Charger JSON", command=self._load_json_file)
        self.load_btn.grid(row=0, column=1, padx=(20, 10))
        
        # Indicateur position plus visible
        self.position_label = ttk.Label(toolbar_frame, text="Aucun bulletin chargé", style='Large.TLabel')
        self.position_label.grid(row=0, column=2, sticky=tk.E, padx=(0, 20))
        
        # Raccourcis clavier
        help_label = ttk.Label(toolbar_frame, text="[Échap/F11: Plein écran]", style='Info.TLabel')
        help_label.grid(row=0, column=3, sticky=tk.E, padx=(0, 10))
        
        # Bouton retour
        self.back_btn = ttk.Button(toolbar_frame, text="◀ Retour", command=self._return_to_main)
        self.back_btn.grid(row=0, column=4, padx=(10, 0))
    
    def _create_navigation_panel(self, parent, row, column):
        """Crée le panneau de navigation optimisé"""
        nav_frame = ttk.LabelFrame(parent, text="Navigation", padding="5")
        nav_frame.grid(row=row, column=column, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        nav_frame.columnconfigure(0, weight=1)
        nav_frame.rowconfigure(1, weight=1)
        
        # Configuration de largeur fixe mais optimisée
        nav_frame.configure(width=250)
        
        # Boutons navigation
        nav_buttons_frame = ttk.Frame(nav_frame)
        nav_buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        nav_buttons_frame.columnconfigure(1, weight=1)
        
        self.prev_btn = ttk.Button(nav_buttons_frame, text="◀ Précédent", command=self._previous_bulletin, state='disabled')
        self.prev_btn.grid(row=0, column=0, sticky=tk.W)
        
        self.next_btn = ttk.Button(nav_buttons_frame, text="Suivant ▶", command=self._next_bulletin, state='disabled')
        self.next_btn.grid(row=0, column=2, sticky=tk.E)
        
        # Liste bulletins avec plus de hauteur
        self.bulletin_list = tk.Listbox(nav_frame, height=25, font=('Arial', 10))
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
        conseil_frame.rowconfigure(1, weight=1)
        
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
        self.overview_notebook.add(synthesis_frame, text="📊 Synthèse")
        synthesis_frame.columnconfigure(0, weight=1)
        synthesis_frame.rowconfigure(0, weight=1)
        
        # TreeView pour la synthèse avec hauteur optimisée
        columns = ('matiere', 'moy_s1', 'moy_s2', 'abs_s1', 'abs_s2', 'evolution')
        self.synthesis_tree = ttk.Treeview(synthesis_frame, columns=columns, show='headings', height=20)
        
        # Configuration colonnes
        self.synthesis_tree.heading('matiere', text='Matière')
        self.synthesis_tree.heading('moy_s1', text='Moy. S1')
        self.synthesis_tree.heading('moy_s2', text='Moy. S2')
        self.synthesis_tree.heading('abs_s1', text='Abs. S1')
        self.synthesis_tree.heading('abs_s2', text='Abs. S2')
        self.synthesis_tree.heading('evolution', text='Évolution')
        
        self.synthesis_tree.column('matiere', width=200)
        self.synthesis_tree.column('moy_s1', width=100)
        self.synthesis_tree.column('moy_s2', width=100)
        self.synthesis_tree.column('abs_s1', width=100)
        self.synthesis_tree.column('abs_s2', width=100)
        self.synthesis_tree.column('evolution', width=120)
        
        self.synthesis_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        synthesis_scrollbar = ttk.Scrollbar(synthesis_frame, orient=tk.VERTICAL, command=self.synthesis_tree.yview)
        synthesis_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.synthesis_tree.configure(yscrollcommand=synthesis_scrollbar.set)
    
    def _create_detailed_tab(self):
        """Crée l'onglet vue détaillée optimisé pour les appréciations"""
        detailed_frame = ttk.Frame(self.overview_notebook, padding="5")
        self.overview_notebook.add(detailed_frame, text="📋 Détails des Appréciations")
        detailed_frame.columnconfigure(0, weight=1)
        detailed_frame.rowconfigure(0, weight=1)
        
        # Créer un canvas avec scrollbar pour la vue détaillée
        canvas = tk.Canvas(detailed_frame)
        scrollbar = ttk.Scrollbar(detailed_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Configuration pour utiliser tout l'espace disponible
        self.scrollable_frame.columnconfigure(0, weight=1)
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Binding pour le scroll avec la molette
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Cette zone sera remplie dynamiquement
        self.detailed_widgets = []
    
    def _create_general_appreciation(self, parent, row):
        """Crée la section appréciation générale compacte"""
        general_frame = ttk.LabelFrame(parent, text="Appréciation Générale", padding="3")
        general_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        general_frame.columnconfigure(1, weight=1)
        
        # Layout horizontal pour économiser l'espace vertical
        # S1
        ttk.Label(general_frame, text="S1:", style='Header.TLabel').grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 5))
        self.general_s1_text = tk.Text(general_frame, height=5, wrap=tk.WORD, state='disabled', font=('Arial', 10))
        self.general_s1_text.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(0, 10))
        
        # S2
        ttk.Label(general_frame, text="S2:", style='Header.TLabel').grid(row=0, column=2, sticky=(tk.W, tk.N), padx=(5, 5))
        self.general_s2_text = tk.Text(general_frame, height=5, wrap=tk.WORD, state='disabled', font=('Arial', 10))
        self.general_s2_text.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=2)
        
        # Répartition équitable de l'espace
        general_frame.columnconfigure(1, weight=1)
        general_frame.columnconfigure(3, weight=1)
    
    def _load_json_file(self):
        """Charge un fichier JSON"""
        file_path = filedialog.askopenfilename(
            title="Choisir le fichier JSON",
            filetypes=[("Fichiers JSON", "*.json")],
            initialdir=os.getcwd()
        )
        if file_path:
            self._load_bulletins_from_file(file_path)
    
    def _load_bulletins_from_file(self, file_path: str):
        """Charge les bulletins depuis un fichier JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.bulletins = []
            for bulletin_data in data:
                bulletin = Bulletin.from_dict(bulletin_data)
                self.bulletins.append(bulletin)
            
            self.json_file_path = file_path
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
        """Met à jour la vue synthèse"""
        # Vider le TreeView
        for item in self.synthesis_tree.get_children():
            self.synthesis_tree.delete(item)
        
        # Ajouter les matières
        for matiere_nom, appreciation in bulletin.matieres.items():
            # Calculer l'évolution
            evolution = ""
            if appreciation.moyenne_s1 and appreciation.moyenne_s2:
                try:
                    moy_s1 = float(str(appreciation.moyenne_s1).replace(',', '.'))
                    moy_s2 = float(str(appreciation.moyenne_s2).replace(',', '.'))
                    diff = moy_s2 - moy_s1
                    if diff > 0:
                        evolution = f"+{diff:.2f} ↗️"
                    elif diff < 0:
                        evolution = f"{diff:.2f} ↘️"
                    else:
                        evolution = "= ➡️"
                except (ValueError, TypeError):
                    evolution = "-"
            
            self.synthesis_tree.insert('', 'end', values=(
                appreciation.matiere,
                appreciation.moyenne_s1 or "-",
                appreciation.moyenne_s2 or "-",
                f"{appreciation.heures_absence_s1}h" if appreciation.heures_absence_s1 else "-",
                f"{appreciation.heures_absence_s2}h" if appreciation.heures_absence_s2 else "-",
                evolution
            ))
    
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
            matiere_frame.columnconfigure(1, weight=1)
            self.detailed_widgets.append(matiere_frame)
            
            # Section informations numériques (compacte en haut)
            info_frame = ttk.Frame(matiere_frame)
            info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
            info_frame.columnconfigure(7, weight=1)
            
            # Moyennes et absences en ligne
            ttk.Label(info_frame, text="Moy. S1:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
            ttk.Label(info_frame, text=appreciation.moyenne_s1 or "-", style='Large.TLabel').grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
            
            ttk.Label(info_frame, text="Moy. S2:", style='Header.TLabel').grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
            ttk.Label(info_frame, text=appreciation.moyenne_s2 or "-", style='Large.TLabel').grid(row=0, column=3, sticky=tk.W, padx=(0, 15))
            
            ttk.Label(info_frame, text="Abs. S1:", style='Header.TLabel').grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
            abs_s1_text = f"{appreciation.heures_absence_s1}h" if appreciation.heures_absence_s1 else "-"
            ttk.Label(info_frame, text=abs_s1_text, style='Large.TLabel').grid(row=0, column=5, sticky=tk.W, padx=(0, 15))
            
            ttk.Label(info_frame, text="Abs. S2:", style='Header.TLabel').grid(row=0, column=6, sticky=tk.W, padx=(0, 5))
            abs_s2_text = f"{appreciation.heures_absence_s2}h" if appreciation.heures_absence_s2 else "-"
            ttk.Label(info_frame, text=abs_s2_text, style='Large.TLabel').grid(row=0, column=7, sticky=tk.W)
            
            # Appréciations avec beaucoup plus d'espace
            appreciations_frame = ttk.Frame(matiere_frame)
            appreciations_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
            appreciations_frame.columnconfigure(0, weight=1)
            appreciations_frame.columnconfigure(1, weight=1)
            
            # Appréciation S1 (colonne gauche)
            if appreciation.appreciation_s1:
                s1_frame = ttk.LabelFrame(appreciations_frame, text="Appréciation S1", padding="5")
                s1_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
                s1_frame.columnconfigure(0, weight=1)
                s1_frame.rowconfigure(0, weight=1)
                
                # Zone de texte optimisée pour S1 (3.5 lignes)
                appr_s1_text = tk.Text(s1_frame, height=4, wrap=tk.WORD, state='disabled', font=('Arial', 11))
                appr_s1_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
                
                # Scrollbar pour S1
                s1_scrollbar = ttk.Scrollbar(s1_frame, orient=tk.VERTICAL, command=appr_s1_text.yview)
                s1_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
                appr_s1_text.configure(yscrollcommand=s1_scrollbar.set)
                
                appr_s1_text.configure(state='normal')
                appr_s1_text.delete('1.0', tk.END)
                self._insert_html_text(appr_s1_text, appreciation.appreciation_s1)
                appr_s1_text.configure(state='disabled')
                self.detailed_widgets.append(appr_s1_text)
                self.detailed_widgets.append(s1_frame)
            
            # Appréciation S2 (colonne droite)
            if appreciation.appreciation_s2:
                s2_frame = ttk.LabelFrame(appreciations_frame, text="Appréciation S2", padding="5")
                s2_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
                s2_frame.columnconfigure(0, weight=1)
                s2_frame.rowconfigure(0, weight=1)
                
                # Zone de texte optimisée pour S2 (3.5 lignes)
                appr_s2_text = tk.Text(s2_frame, height=4, wrap=tk.WORD, state='disabled', font=('Arial', 11))
                appr_s2_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
                
                # Scrollbar pour S2
                s2_scrollbar = ttk.Scrollbar(s2_frame, orient=tk.VERTICAL, command=appr_s2_text.yview)
                s2_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
                appr_s2_text.configure(yscrollcommand=s2_scrollbar.set)
                
                appr_s2_text.configure(state='normal')
                appr_s2_text.delete('1.0', tk.END)
                self._insert_html_text(appr_s2_text, appreciation.appreciation_s2)
                appr_s2_text.configure(state='disabled')
                self.detailed_widgets.append(appr_s2_text)
                self.detailed_widgets.append(s2_frame)
            
            # Configuration pour que les appréciations prennent toute la hauteur disponible
            matiere_frame.rowconfigure(1, weight=1)
            appreciations_frame.rowconfigure(0, weight=1)
            
            row += 1
    
    def _update_general_view(self, bulletin):
        """Met à jour la vue appréciation générale"""
        # S1
        self.general_s1_text.configure(state='normal')
        self.general_s1_text.delete('1.0', tk.END)
        if bulletin.appreciation_generale_s1:
            self._insert_html_text(self.general_s1_text, bulletin.appreciation_generale_s1)
        self.general_s1_text.configure(state='disabled')
        
        # S2
        self.general_s2_text.configure(state='normal')
        self.general_s2_text.delete('1.0', tk.END)
        if bulletin.appreciation_generale_s2:
            self._insert_html_text(self.general_s2_text, bulletin.appreciation_generale_s2)
        self.general_s2_text.configure(state='disabled')
    
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
        
        self.general_s1_text.configure(state='normal')
        self.general_s1_text.delete('1.0', tk.END)
        self.general_s1_text.configure(state='disabled')
        
        self.general_s2_text.configure(state='normal')
        self.general_s2_text.delete('1.0', tk.END)
        self.general_s2_text.configure(state='disabled')
    
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
            print(f"❌ Erreur dans _return_to_main: {e}")
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
            print(f"❌ Erreur dans _on_closing: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_action_bar(self, parent, row):
        """Crée la barre d'actions optimisée"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        action_frame.columnconfigure(3, weight=1)
        
        # Boutons d'action plus espacés
        self.export_btn = ttk.Button(action_frame, text="📤 Exporter", command=self._export_conseil, state='disabled')
        self.export_btn.grid(row=0, column=0, padx=(0, 15))
        
        self.print_btn = ttk.Button(action_frame, text="🖨️ Imprimer", command=self._print_conseil, state='disabled')
        self.print_btn.grid(row=0, column=1, padx=(0, 15))
        
        # Bouton plein écran
        self.fullscreen_btn = ttk.Button(action_frame, text="⛶ Basculer plein écran", command=self._toggle_fullscreen)
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