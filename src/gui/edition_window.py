#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fenêtre d'édition des bulletins de l'application BGRAPP Pyconseil
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from pathlib import Path
from typing import List, Optional

# Import conditionnel
try:
    from ..models.bulletin import Bulletin, Eleve, AppreciationMatiere
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models.bulletin import Bulletin, Eleve, AppreciationMatiere


class EditionWindow:
    """Fenêtre d'édition des bulletins"""
    
    def __init__(self, parent_window=None, json_file_path: Optional[str] = None):
        self.parent_window = parent_window
        self.json_file_path = json_file_path
        self.bulletins: List[Bulletin] = []
        self.current_bulletin_index: int = 0
        
        # Créer la fenêtre
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.root.title("BGRAPP Pyconseil - Édition des bulletins")
        self.root.geometry("1000x700")
        
        self._setup_styles()
        self._create_interface()
        
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
    
    def _create_toolbar(self, parent, row):
        """Crée la barre d'outils"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        toolbar_frame.columnconfigure(2, weight=1)
        
        # Titre
        ttk.Label(toolbar_frame, text="📝 Édition des bulletins", style='Title.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        # Bouton charger
        self.load_btn = ttk.Button(toolbar_frame, text="📂 Charger JSON", command=self._load_json_file)
        self.load_btn.grid(row=0, column=1, padx=(20, 10))
        
        # Indicateur position
        self.position_label = ttk.Label(toolbar_frame, text="Aucun bulletin chargé", style='Info.TLabel')
        self.position_label.grid(row=0, column=2, sticky=tk.E)
        
        # Bouton retour
        self.back_btn = ttk.Button(toolbar_frame, text="◀ Retour", command=self._return_to_main)
        self.back_btn.grid(row=0, column=3, padx=(10, 0))
    
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
        
        columns = ('matiere', 'moyenne_s1', 'moyenne_s2', 'absence_s1', 'absence_s2')
        self.subjects_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configuration colonnes
        self.subjects_tree.heading('matiere', text='Matière')
        self.subjects_tree.heading('moyenne_s1', text='Moy. S1')
        self.subjects_tree.heading('moyenne_s2', text='Moy. S2')
        self.subjects_tree.heading('absence_s1', text='Abs. S1')
        self.subjects_tree.heading('absence_s2', text='Abs. S2')
        
        self.subjects_tree.column('matiere', width=200)
        self.subjects_tree.column('moyenne_s1', width=80)
        self.subjects_tree.column('moyenne_s2', width=80)
        self.subjects_tree.column('absence_s1', width=80)
        self.subjects_tree.column('absence_s2', width=80)
        
        self.subjects_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.subjects_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.subjects_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Zone appréciations
        appreciation_frame = ttk.LabelFrame(subjects_frame, text="Appréciations de la matière sélectionnée", padding="5")
        appreciation_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        appreciation_frame.columnconfigure(0, weight=1)
        
        ttk.Label(appreciation_frame, text="Semestre 1:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.appreciation_s1_text = tk.Text(appreciation_frame, height=3, width=60, wrap=tk.WORD, state='disabled')
        self.appreciation_s1_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(appreciation_frame, text="Semestre 2:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.appreciation_s2_text = tk.Text(appreciation_frame, height=3, width=60, wrap=tk.WORD, state='disabled')
        self.appreciation_s2_text.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=2)
        
        self.subjects_tree.bind('<<TreeviewSelect>>', self._on_subject_select)
    
    def _create_general_tab(self):
        """Onglet appréciation générale"""
        general_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(general_frame, text="📋 Appréciation générale")
        general_frame.columnconfigure(0, weight=1)
        
        # S1
        s1_frame = ttk.LabelFrame(general_frame, text="Semestre 1", padding="5")
        s1_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        s1_frame.columnconfigure(0, weight=1)
        
        self.general_s1_text = tk.Text(s1_frame, height=6, wrap=tk.WORD)
        self.general_s1_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # S2
        s2_frame = ttk.LabelFrame(general_frame, text="Semestre 2", padding="5")
        s2_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        s2_frame.columnconfigure(0, weight=1)
        
        self.general_s2_text = tk.Text(s2_frame, height=6, wrap=tk.WORD)
        self.general_s2_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
    
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
            text="✨ Générer appréciation S2", 
            command=self._generate_current_general,
            state='disabled'
        )
        self.current_generate_btn.grid(row=0, column=1, pady=5)
    
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
            initialdir=os.getcwd()
        )
        
        if file_path:
            self._load_bulletins_from_file(file_path)
    
    def _load_bulletins_from_file(self, file_path: str):
        """Charge les bulletins depuis un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.bulletins = []
            for bulletin_data in data:
                bulletin = Bulletin.from_dict(bulletin_data)
                self.bulletins.append(bulletin)
            
            self.json_file_path = file_path
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
        """Met à jour l'affichage des matières"""
        for item in self.subjects_tree.get_children():
            self.subjects_tree.delete(item)
        
        for nom_matiere, appreciation in bulletin.matieres.items():
            moyenne_s1 = f"{appreciation.moyenne_s1:.2f}" if appreciation.moyenne_s1 is not None else "-"
            moyenne_s2 = f"{appreciation.moyenne_s2:.2f}" if appreciation.moyenne_s2 is not None else "-"
            absence_s1 = f"{appreciation.heures_absence_s1}h" if appreciation.heures_absence_s1 is not None else "-"
            absence_s2 = f"{appreciation.heures_absence_s2}h" if appreciation.heures_absence_s2 is not None else "-"
            
            self.subjects_tree.insert('', tk.END, values=(nom_matiere, moyenne_s1, moyenne_s2, absence_s1, absence_s2))
        
        # Vider appréciations - l'affichage se fera lors de la sélection d'une matière
        self.appreciation_s1_text.config(state='normal')
        self.appreciation_s1_text.delete('1.0', tk.END)
        self.appreciation_s1_text.insert('1.0', "Sélectionnez une matière pour voir les appréciations")
        self.appreciation_s1_text.config(state='disabled')
        
        self.appreciation_s2_text.config(state='normal')
        self.appreciation_s2_text.delete('1.0', tk.END)
        self.appreciation_s2_text.insert('1.0', "Sélectionnez une matière pour voir les appréciations")
        self.appreciation_s2_text.config(state='disabled')
    
    def _update_general_display(self, bulletin):
        """Met à jour les appréciations générales"""
        self.general_s1_text.delete('1.0', tk.END)
        if bulletin.appreciation_generale_s1:
            self.general_s1_text.insert('1.0', bulletin.appreciation_generale_s1)
        
        self.general_s2_text.delete('1.0', tk.END)
        if bulletin.appreciation_generale_s2:
            self.general_s2_text.insert('1.0', bulletin.appreciation_generale_s2)
    
    def _clear_display(self):
        """Vide l'affichage"""
        self.nom_label.config(text="-")
        self.prenom_label.config(text="-")
        self.classe_label.config(text="-")
        
        for item in self.subjects_tree.get_children():
            self.subjects_tree.delete(item)
        
        self.general_s1_text.delete('1.0', tk.END)
        self.general_s2_text.delete('1.0', tk.END)
        
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
            self.appreciation_s1_text.config(state='normal')
            self.appreciation_s1_text.delete('1.0', tk.END)
            if appreciation.appreciation_s1:
                self.appreciation_s1_text.insert('1.0', appreciation.appreciation_s1)
            self.appreciation_s1_text.config(state='disabled')
            
            self.appreciation_s2_text.config(state='normal')
            self.appreciation_s2_text.delete('1.0', tk.END)
            if appreciation.appreciation_s2:
                self.appreciation_s2_text.insert('1.0', appreciation.appreciation_s2)
            self.appreciation_s2_text.config(state='disabled')
    
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
        
        # Vérifier la configuration OpenAI
        try:
            from ..services.openai_service import get_openai_service
        except ImportError:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from services.openai_service import get_openai_service
        
        openai_service = get_openai_service()
        if not openai_service:
            messagebox.showerror("Erreur OpenAI", 
                               "Impossible de se connecter à OpenAI.\n" + 
                               "Vérifiez votre clé API dans la variable d'environnement OPENAI_API_KEY")
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
        cancelled = tk.BooleanVar(False)
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
        
        # Vérifier la configuration OpenAI
        try:
            from ..services.openai_service import get_openai_service
        except ImportError:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from services.openai_service import get_openai_service
        
        openai_service = get_openai_service()
        if not openai_service:
            messagebox.showerror("Erreur OpenAI", 
                               "Impossible de se connecter à OpenAI.\n" + 
                               "Vérifiez votre clé API dans la variable d'environnement OPENAI_API_KEY")
            return
        
        # Créer une fenêtre de progression
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Génération d'appréciations générales")
        progress_window.geometry("400x150")
        progress_window.resizable(False, False)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Génération des appréciations générales S2", font=('Arial', 12, 'bold')).pack(pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(pady=10, padx=20, fill=tk.X)
        
        status_label = ttk.Label(progress_window, text="Initialisation...")
        status_label.pack(pady=5)
        
        # Bouton annuler
        cancelled = tk.BooleanVar(False)
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
        
        # Vérifier la configuration OpenAI
        try:
            from ..services.openai_service import get_openai_service
        except ImportError:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from services.openai_service import get_openai_service
        
        openai_service = get_openai_service()
        if not openai_service:
            messagebox.showerror("Erreur OpenAI", 
                               "Impossible de se connecter à OpenAI.\n" + 
                               "Vérifiez votre clé API dans la variable d'environnement OPENAI_API_KEY")
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
                    # Prétraitement S1
                    if matiere.appreciation_s1:
                        try:
                            preprocessed = openai_service.preprocess_appreciation(
                                matiere.appreciation_s1,
                                bulletin.eleve.nom,
                                bulletin.eleve.prenom
                            )
                            matiere.appreciation_s1 = preprocessed
                            success_count += 1
                        except Exception as e:
                            print(f"Erreur prétraitement S1 {nom_matiere}: {e}")
                            error_count += 1
                    
                    # Prétraitement S2
                    if matiere.appreciation_s2:
                        try:
                            preprocessed = openai_service.preprocess_appreciation(
                                matiere.appreciation_s2,
                                bulletin.eleve.nom,
                                bulletin.eleve.prenom
                            )
                            matiere.appreciation_s2 = preprocessed
                            success_count += 1
                        except Exception as e:
                            print(f"Erreur prétraitement S2 {nom_matiere}: {e}")
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
        
        # Vérifier la configuration OpenAI
        try:
            from ..services.openai_service import get_openai_service
        except ImportError:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from services.openai_service import get_openai_service
        
        openai_service = get_openai_service()
        if not openai_service:
            messagebox.showerror("Erreur OpenAI", 
                               "Impossible de se connecter à OpenAI.\n" + 
                               "Vérifiez votre clé API dans la variable d'environnement OPENAI_API_KEY")
            return
        
        bulletin = self.bulletins[self.current_bulletin_index]
        
        # Collecter les appréciations S2 par matière
        appreciations_s2 = {}
        for nom_matiere, matiere in bulletin.matieres.items():
            if matiere.appreciation_s2 and matiere.appreciation_s2.strip():
                appreciations_s2[nom_matiere] = matiere.appreciation_s2
        
        if not appreciations_s2:
            messagebox.showwarning("Attention", 
                                 f"Aucune appréciation S2 trouvée pour {bulletin.eleve.nom} {bulletin.eleve.prenom}.\n" +
                                 "Impossible de générer l'appréciation générale.")
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
                    appreciations_s2,
                    bulletin.eleve.nom,
                    bulletin.eleve.prenom
                )
                bulletin.appreciation_generale_s2 = general_appreciation
                
                progress_window.destroy()
                
                # Sauvegarder automatiquement en préservant les valeurs générées
                self._save_changes_preserve_generated()
                
                # Rafraîchir l'affichage en conservant la sélection
                self._refresh_display_with_selection()
                
                messagebox.showinfo("Génération terminée", 
                                  f"Appréciation générale S2 générée pour {bulletin.eleve.nom} {bulletin.eleve.prenom} !")
                
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
                # Sauvegarde normale : synchroniser avec les TextBox
                bulletin = self.bulletins[self.current_bulletin_index]
                bulletin.appreciation_generale_s1 = self.general_s1_text.get('1.0', tk.END).strip()
                bulletin.appreciation_generale_s2 = self.general_s2_text.get('1.0', tk.END).strip()
            
            # Sauvegarder tous les bulletins dans le fichier JSON
            data = [bulletin.to_dict() for bulletin in self.bulletins]
            
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
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