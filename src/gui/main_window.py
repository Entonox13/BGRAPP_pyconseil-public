#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fenêtre principale de l'application BGRAPP Pyconseil
Interface graphique pour la sélection du dossier de travail et le lancement du traitement
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from typing import Optional
import threading

# Import conditionnel pour gérer les imports relatifs
try:
    from ..services.main_processor import (
        process_directory_to_json, 
        get_processing_summary,
        MainProcessorError
    )
    from .config_window import ConfigWindow
    from ..utils.semester import (
        Semester,
        infer_semester_from_bulletins_data,
        semester_from_metadata,
    )
except ImportError:
    # Fallback pour les tests et l'exécution directe
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from services.main_processor import (
        process_directory_to_json, 
        get_processing_summary,
        MainProcessorError
    )
    sys.path.insert(0, str(Path(__file__).parent))
    from config_window import ConfigWindow
    from utils.semester import (
        Semester,
        infer_semester_from_bulletins_data,
        semester_from_metadata,
    )


class MainWindow:
    """
    Fenêtre principale de l'application BGRAPP Pyconseil
    """
    
    def __init__(self):
        """Initialise la fenêtre principale"""
        self.root = tk.Tk()
        self.root.title("BGRAPP Pyconseil - Outil d'aide aux conseils de classe")
        self.root.geometry("800x600")
        
        # Variables d'état
        self.selected_directory: Optional[str] = None
        self.output_json_path: Optional[str] = None
        self._last_semester: Semester = Semester.S2
        
        # Configuration du style
        self._setup_styles()
        
        # Création de l'interface
        self._create_interface()
        
        # Configuration de la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_styles(self):
        """Configure les styles de l'interface"""
        style = ttk.Style()
        
        # Configuration des couleurs et polices
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 10))
        style.configure('Success.TLabel', font=('Arial', 10), foreground='green')
        style.configure('Error.TLabel', font=('Arial', 10), foreground='red')
    
    def _create_interface(self):
        """Crée tous les éléments de l'interface"""
        
        # Frame principal avec padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration des poids pour le redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Titre principal
        title_label = ttk.Label(
            main_frame, 
            text="🎓 BGRAPP Pyconseil", 
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, pady=(0, 5), sticky=tk.W)
        
        subtitle_label = ttk.Label(
            main_frame, 
            text="Outil d'aide à la préparation des conseils de classe", 
            style='Subtitle.TLabel'
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 20), sticky=tk.W)
        
        # Section 1: Sélection du dossier de travail
        self._create_directory_section(main_frame, 2)
        
        # Séparateur 1
        separator1 = ttk.Separator(main_frame, orient='horizontal')
        separator1.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Section 2: Traitement JSON
        self._create_processing_section(main_frame, 6)
        
        # Séparateur 2
        separator2 = ttk.Separator(main_frame, orient='horizontal')
        separator2.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Section 3: Navigation
        self._create_navigation_section(main_frame, 9)
        
        # Séparateur 3
        separator3 = ttk.Separator(main_frame, orient='horizontal')
        separator3.grid(row=11, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Section 4: Messages d'état
        self._create_status_section(main_frame, 12)
    
    def _create_directory_section(self, parent: ttk.Frame, row: int):
        """Crée la section de sélection du dossier"""
        
        # Titre de section
        section_label = ttk.Label(
            parent, 
            text="📁 Sélection du dossier de travail", 
            style='Subtitle.TLabel'
        )
        section_label.grid(row=row, column=0, pady=(10, 5), sticky=tk.W)
        
        # Frame pour le sélecteur
        dir_frame = ttk.Frame(parent)
        dir_frame.grid(row=row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        # Bouton de sélection
        self.select_dir_btn = ttk.Button(
            dir_frame,
            text="Choisir dossier",
            command=self._select_directory
        )
        self.select_dir_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Label pour afficher le dossier sélectionné
        self.dir_label = ttk.Label(
            dir_frame,
            text="Aucun dossier sélectionné",
            style='Info.TLabel',
            relief='sunken',
            padding="5"
        )
        self.dir_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Frame pour la zone d'informations avec scrollbar
        info_frame = ttk.Frame(parent)
        info_frame.grid(row=row+2, column=0, sticky=(tk.W, tk.E), pady=5)
        info_frame.columnconfigure(0, weight=1)
        
        # Zone d'informations sur le contenu
        self.dir_info = tk.Text(
            info_frame,
            height=4,
            width=80,
            state='disabled',
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.dir_info.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Scrollbar pour la zone d'informations
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.dir_info.yview)
        info_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.dir_info.configure(yscrollcommand=info_scrollbar.set)
    
    def _create_processing_section(self, parent: ttk.Frame, row: int):
        """Crée la section de traitement JSON"""
        
        # Titre de section
        section_label = ttk.Label(
            parent, 
            text="⚙️ Traitement des données", 
            style='Subtitle.TLabel'
        )
        section_label.grid(row=row, column=0, pady=(10, 5), sticky=tk.W)
        
        # Frame pour les boutons
        process_frame = ttk.Frame(parent)
        process_frame.grid(row=row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Bouton de création JSON
        self.create_json_btn = ttk.Button(
            process_frame,
            text="🔄 Créer fichier JSON",
            command=self._create_json,
            state='disabled'
        )
        self.create_json_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Bouton de chargement JSON existant
        self.load_json_btn = ttk.Button(
            process_frame,
            text="📂 Charger JSON existant",
            command=self._load_existing_json
        )
        self.load_json_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Barre de progression
        self.progress = ttk.Progressbar(
            process_frame,
            mode='indeterminate',
            length=250
        )
        self.progress.grid(row=0, column=2, padx=(10, 0), sticky=(tk.W, tk.E))
        process_frame.columnconfigure(2, weight=1)
    
    def _create_navigation_section(self, parent: ttk.Frame, row: int):
        """Crée la section de navigation"""
        
        # Titre de section
        section_label = ttk.Label(
            parent, 
            text="🧭 Navigation", 
            style='Subtitle.TLabel'
        )
        section_label.grid(row=row, column=0, pady=(20, 5), sticky=tk.W)
        
        # Frame pour les boutons - Ligne 1
        nav_frame = ttk.Frame(parent)
        nav_frame.grid(row=row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Bouton fenêtre édition
        self.edit_btn = ttk.Button(
            nav_frame,
            text="📝 Fenêtre d'édition",
            command=self._open_edition_window,
            state='disabled'
        )
        self.edit_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Bouton fenêtre conseil
        self.conseil_btn = ttk.Button(
            nav_frame,
            text="🎯 Fenêtre conseil",
            command=self._open_conseil_window,
            state='disabled'
        )
        self.conseil_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Bouton configuration IA
        config_btn = ttk.Button(
            nav_frame,
            text="🤖 Configuration IA",
            command=self._open_config_window
        )
        config_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Bouton quitter
        quit_btn = ttk.Button(
            nav_frame,
            text="❌ Quitter",
            command=self._on_closing
        )
        quit_btn.grid(row=0, column=3)
    
    def _create_status_section(self, parent: ttk.Frame, row: int):
        """Crée la section des messages d'état"""
        
        # Zone de messages
        self.status_text = tk.Text(
            parent,
            height=6,
            width=80,
            state='disabled',
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.status_text.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # Scrollbar pour les messages
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=row, column=1, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
    
    def _select_directory(self):
        """Ouvre le dialog de sélection de dossier"""
        directory = filedialog.askdirectory(
            title="Sélectionner le dossier contenant les fichiers source",
            initialdir=os.getcwd()
        )
        
        if directory:
            self.selected_directory = directory
            self._update_directory_display()
            self._analyze_directory()
    
    def _update_directory_display(self):
        """Met à jour l'affichage du dossier sélectionné"""
        if self.selected_directory:
            # Afficher le chemin (tronqué si trop long)
            display_path = self.selected_directory
            if len(display_path) > 60:
                display_path = "..." + display_path[-57:]
            
            self.dir_label.config(text=display_path)
            self._log_message(f"📁 Dossier sélectionné: {self.selected_directory}")
        else:
            self.dir_label.config(text="Aucun dossier sélectionné")
    
    def _analyze_directory(self):
        """Analyse le contenu du dossier sélectionné"""
        if not self.selected_directory:
            return
        
        try:
            # Obtenir le résumé du traitement
            summary = get_processing_summary(self.selected_directory)
            
            # Mettre à jour l'affichage des informations
            self._update_directory_info(summary)
            
            # Activer/désactiver le bouton de traitement
            if summary['valid_directory'] and summary['source_file_exists']:
                self.create_json_btn.config(state='normal')
                self._log_message("✅ Dossier valide - Traitement possible", "success")
            else:
                self.create_json_btn.config(state='disabled')
                self._log_message("❌ Dossier invalide - Vérifiez les fichiers requis", "error")
                
        except Exception as e:
            self._log_message(f"❌ Erreur lors de l'analyse: {str(e)}", "error")
            self.create_json_btn.config(state='disabled')
    
    def _update_directory_info(self, summary: dict):
        """Met à jour la zone d'informations du dossier"""
        self.dir_info.config(state='normal')
        self.dir_info.delete('1.0', tk.END)
        
        # Informations sur le contenu
        info_text = []
        info_text.append(f"📊 Bulletins estimés: {summary['estimated_bulletins']}")
        info_text.append(f"📚 Matières trouvées: {summary['estimated_matieres']}")
        info_text.append(f"📄 Fichiers CSV: {summary['csv_files_count']}")
        
        if summary['csv_files']:
            matières = ", ".join(summary['csv_files'][:5])  # Limiter à 5 pour l'affichage
            if len(summary['csv_files']) > 5:
                matières += f"... (+{len(summary['csv_files'])-5} autres)"
            info_text.append(f"📝 Matières: {matières}")
        
        if summary['errors']:
            info_text.append("⚠️ Problèmes détectés:")
            for error in summary['errors'][:3]:  # Limiter à 3 erreurs
                info_text.append(f"   • {error}")
        
        self.dir_info.insert('1.0', "\n".join(info_text))
        self.dir_info.config(state='disabled')
    
    def _create_json(self):
        """Lance la création du fichier JSON en arrière-plan"""
        if not self.selected_directory:
            return
        
        # Demander où sauvegarder le fichier
        output_path = filedialog.asksaveasfilename(
            title="Sauvegarder le fichier JSON",
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")],
            initialdir=self.selected_directory,
            initialfile="output.json"
        )
        
        if not output_path:
            return
        
        self.output_json_path = output_path
        
        # Désactiver les boutons et démarrer la progression
        self.create_json_btn.config(state='disabled')
        self.progress.start()
        self._log_message("🔄 Début du traitement JSON...")
        
        # Lancer le traitement en arrière-plan
        thread = threading.Thread(target=self._process_json_thread)
        thread.daemon = True
        thread.start()
    
    def _process_json_thread(self):
        """Traitement JSON en arrière-plan"""
        try:
            # Lancer le traitement
            result = process_directory_to_json(
                self.selected_directory,
                self.output_json_path,
                validate_data=True
            )
            
            # Programmer la mise à jour de l'interface dans le thread principal
            self.root.after(0, self._on_json_success, result)
            
        except MainProcessorError as e:
            self.root.after(0, self._on_json_error, str(e))
        except Exception as e:
            self.root.after(0, self._on_json_error, f"Erreur inattendue: {str(e)}")
    
    def _on_json_success(self, result: dict):
        """Appelé quand le traitement JSON réussit"""
        self.progress.stop()
        self.create_json_btn.config(state='normal')
        
        # Messages de succès
        self._log_message("✅ Traitement JSON terminé avec succès!", "success")
        self._log_message(f"📄 {result['bulletins_count']} bulletins générés", "success")
        self._log_message(f"📚 {result['matieres_count']} matières traitées", "success")
        self._log_message(f"💾 Fichier sauvé: {result['output_file']}", "success")
        detected_semester = self._parse_semester_string(result.get('semester'))
        self._remember_semester(detected_semester)
        
        # Afficher les avertissements s'il y en a
        if result['warnings']:
            self._log_message(f"⚠️ {len(result['warnings'])} avertissement(s):")
            for warning in result['warnings']:
                self._log_message(f"   • {warning}", "warning")
        
        # Activer les boutons de navigation
        self.edit_btn.config(state='normal')
        self.conseil_btn.config(state='normal')
        
        # Message de confirmation
        messagebox.showinfo(
            "Traitement terminé",
            f"Le fichier JSON a été créé avec succès!\n\n"
            f"📄 {result['bulletins_count']} bulletins générés\n"
            f"📚 {result['matieres_count']} matières traitées\n"
            f"💾 Fichier: {os.path.basename(result['output_file'])}"
        )
    
    def _on_json_error(self, error_message: str):
        """Appelé quand le traitement JSON échoue"""
        self.progress.stop()
        self.create_json_btn.config(state='normal')
        
        self._log_message(f"❌ Erreur lors du traitement: {error_message}", "error")
        
        messagebox.showerror(
            "Erreur de traitement",
            f"Une erreur s'est produite lors du traitement:\n\n{error_message}"
        )
    
    def _load_existing_json(self):
        """Charge un fichier JSON existant"""
        json_path = filedialog.askopenfilename(
            title="Sélectionner un fichier JSON",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")],
            initialdir=os.getcwd()
        )
        
        if not json_path:
            return
        
        try:
            # Valider que le fichier JSON est bien formaté et contient des bulletins
            import json
            with open(json_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            metadata = {}
            data = raw_data
            if raw_data and isinstance(raw_data[0], dict) and '_metadata' in raw_data[0]:
                metadata = raw_data[0].get('_metadata') or {}
                data = raw_data[1:]
            
            # Vérifier la structure basique
            if not isinstance(data, list):
                raise ValueError("Le fichier JSON doit contenir une liste de bulletins")
            
            if len(data) == 0:
                raise ValueError("Le fichier JSON ne contient aucun bulletin")
            
            # Vérifier qu'au moins le premier élément ressemble à un bulletin
            first_bulletin = data[0]
            required_fields = ['Nom', 'Prenom', 'Matieres']
            for field in required_fields:
                if field not in first_bulletin:
                    raise ValueError(f"Structure invalide: champ '{field}' manquant")
            
            detected_semester = semester_from_metadata(metadata) or infer_semester_from_bulletins_data(data)
            self._remember_semester(detected_semester)
            
            # Si tout est OK, enregistrer le chemin et activer les boutons
            self.output_json_path = json_path
            self.edit_btn.config(state='normal')
            self.conseil_btn.config(state='normal')
            
            # Messages de succès
            self._log_message("✅ Fichier JSON chargé avec succès!", "success")
            self._log_message(f"📄 {len(data)} bulletin(s) trouvé(s)", "success")
            self._log_message(f"📂 Fichier: {os.path.basename(json_path)}", "success")
            
            # Analyser la distribution des matières
            matieres_counts = [len(bulletin.get('Matieres', {})) for bulletin in data]
            min_matieres = min(matieres_counts)
            max_matieres = max(matieres_counts)
            moyenne_matieres = sum(matieres_counts) / len(matieres_counts)
            
            if min_matieres == max_matieres:
                self._log_message(f"📚 {min_matieres} matière(s) par bulletin", "success")
            else:
                self._log_message(f"📚 {min_matieres}-{max_matieres} matières par bulletin (moy: {moyenne_matieres:.1f})", "success")
            
            # Compter les matières uniques
            toutes_matieres = set()
            for bulletin in data:
                toutes_matieres.update(bulletin.get('Matieres', {}).keys())
            
            if len(toutes_matieres) > 0:
                self._log_message(f"🎓 {len(toutes_matieres)} matière(s) différente(s) disponible(s)", "success")
            
            # Préparer le message de confirmation
            if min_matieres == max_matieres:
                matieres_msg = f"📚 {min_matieres} matière(s) par bulletin"
            else:
                matieres_msg = f"📚 {min_matieres}-{max_matieres} matières par bulletin"
            
            messagebox.showinfo(
                "Chargement réussi",
                f"Fichier JSON chargé avec succès!\n\n"
                f"📄 {len(data)} bulletin(s) trouvé(s)\n"
                f"{matieres_msg}\n"
                f"🎓 {len(toutes_matieres)} matière(s) différente(s)\n"
                f"📂 Fichier: {os.path.basename(json_path)}\n\n"
                f"Vous pouvez maintenant accéder aux fenêtres d'édition et de conseil."
            )
            
        except json.JSONDecodeError as e:
            error_msg = f"Fichier JSON invalide: {str(e)}"
            self._log_message(f"❌ {error_msg}", "error")
            messagebox.showerror("Erreur de format", error_msg)
            
        except ValueError as e:
            error_msg = f"Structure de données invalide: {str(e)}"
            self._log_message(f"❌ {error_msg}", "error")
            messagebox.showerror("Erreur de structure", error_msg)
            
        except Exception as e:
            error_msg = f"Erreur lors du chargement: {str(e)}"
            self._log_message(f"❌ {error_msg}", "error")
            messagebox.showerror("Erreur", error_msg)
    
    def _open_edition_window(self):
        """Ouvre la fenêtre d'édition"""
        self._log_message("📝 Ouverture de la fenêtre d'édition...")
        
        # Vérifier qu'un fichier JSON existe
        if not self.output_json_path or not os.path.exists(self.output_json_path):
            messagebox.showerror(
                "Fichier manquant",
                "Aucun fichier JSON trouvé.\n"
                "Veuillez d'abord créer un fichier JSON via le traitement des données\n"
                "ou charger un fichier JSON existant."
            )
            return
        
        try:
            # Import conditionnel pour éviter les erreurs circulaires
            try:
                from .edition_window import EditionWindow
            except ImportError:
                from src.gui.edition_window import EditionWindow
            
            # Créer et lancer la fenêtre d'édition
            edition_window = EditionWindow(
                parent_window=self,
                json_file_path=self.output_json_path,
                initial_semester=self._last_semester
            )
            self._log_message("✅ Fenêtre d'édition ouverte", "success")
            
        except Exception as e:
            self._log_message(f"❌ Erreur lors de l'ouverture: {str(e)}", "error")
            messagebox.showerror(
                "Erreur",
                f"Impossible d'ouvrir la fenêtre d'édition:\n{str(e)}"
            )
    
    def _open_conseil_window(self):
        """Ouvre la fenêtre conseil"""
        self._log_message("🎯 Ouverture de la fenêtre conseil...")
        
        # Vérifier qu'un fichier JSON existe
        if not self.output_json_path or not os.path.exists(self.output_json_path):
            messagebox.showerror(
                "Fichier manquant",
                "Aucun fichier JSON trouvé.\n"
                "Veuillez d'abord créer un fichier JSON via le traitement des données\n"
                "ou charger un fichier JSON existant."
            )
            return
        
        try:
            # Import conditionnel pour éviter les erreurs circulaires
            try:
                from .conseil_window import ConseilWindow
            except ImportError:
                from src.gui.conseil_window import ConseilWindow
            
            # Créer et lancer la fenêtre conseil
            conseil_window = ConseilWindow(
                parent_window=self,
                json_file_path=self.output_json_path,
                initial_semester=self._last_semester
            )
            self._log_message("✅ Fenêtre conseil ouverte", "success")
            
        except Exception as e:
            self._log_message(f"❌ Erreur lors de l'ouverture: {str(e)}", "error")
            messagebox.showerror(
                "Erreur",
                f"Impossible d'ouvrir la fenêtre conseil:\n{str(e)}"
            )

    def _parse_semester_string(self, semester_value: Optional[str]) -> Semester:
        """Convertit une chaîne (S1/S2) en enum Semester."""
        if isinstance(semester_value, str):
            normalized = semester_value.strip().upper()
            if normalized in Semester.__members__:
                return Semester[normalized]
        return Semester.S2

    def _remember_semester(self, semester: Semester, log: bool = True):
        """Stocke le semestre détecté pour les sous-fenêtres."""
        self._last_semester = semester
        if log:
            self._log_message(f"🗂️ Semestre détecté: {semester.label}", "info")
    
    def _open_config_window(self):
        """Ouvre la fenêtre de configuration IA"""
        self._log_message("🤖 Ouverture de la fenêtre de configuration IA...")
        
        try:
            # Créer et lancer la fenêtre de configuration
            config_window = ConfigWindow(
                parent_window=self,
                on_config_changed=self._on_ai_config_changed
            )
            
            self._log_message("✅ Fenêtre de configuration IA ouverte", "success")
            
        except Exception as e:
            self._log_message(f"❌ Erreur lors de l'ouverture de la configuration IA: {e}", "error")
            messagebox.showerror(
                "Erreur", 
                f"Erreur lors de l'ouverture de la configuration IA:\n{str(e)}"
            )
    
    def _on_ai_config_changed(self):
        """Callback appelé quand la configuration IA change"""
        self._log_message("🔧 Configuration IA mise à jour", "success")
    
    def _log_message(self, message: str, level: str = "info"):
        """Ajoute un message dans la zone de statut"""
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.status_text.config(state='normal')
        
        # Couleurs selon le niveau
        if level == "success":
            self.status_text.insert(tk.END, formatted_message, "success")
        elif level == "error":
            self.status_text.insert(tk.END, formatted_message, "error")
        elif level == "warning":
            self.status_text.insert(tk.END, formatted_message, "warning")
        else:
            self.status_text.insert(tk.END, formatted_message)
        
        # Configuration des tags de couleur
        self.status_text.tag_config("success", foreground="green")
        self.status_text.tag_config("error", foreground="red")
        self.status_text.tag_config("warning", foreground="orange")
        
        # Faire défiler vers le bas
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
    
    def _on_closing(self):
        """Gère la fermeture de l'application"""
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application?"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Lance l'application"""
        self._log_message("🚀 Application BGRAPP Pyconseil démarrée")
        self._log_message("📁 Sélectionnez un dossier contenant les fichiers source pour commencer")
        self.root.mainloop()


def main():
    """Point d'entrée pour tester la fenêtre principale"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()