#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fenêtre de configuration IA de l'application BGRAPP Pyconseil
Interface pour configurer les clés API et modèles des fournisseurs IA
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, Callable
import logging
import threading

# Import conditionnel
try:
    from ..services.ai_config_service import AIConfigService, AIProvider, get_ai_config_service
    from ..services.ai_connection_test_service import get_ai_connection_test_service
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from services.ai_config_service import AIConfigService, AIProvider, get_ai_config_service
    from services.ai_connection_test_service import get_ai_connection_test_service


class ConfigWindow:
    """Fenêtre de configuration des fournisseurs IA"""
    
    def __init__(self, parent_window=None, on_config_changed: Optional[Callable] = None):
        self.parent_window = parent_window
        self.on_config_changed = on_config_changed
        self.logger = logging.getLogger(__name__)
        
        # Services
        self.config_service = get_ai_config_service()
        self.test_service = get_ai_connection_test_service()
        
        # Variables tkinter pour les widgets (initialisées après création de la fenêtre)
        self.api_key_vars: Dict[AIProvider, tk.StringVar] = {}
        self.model_vars: Dict[AIProvider, tk.StringVar] = {}
        self.active_provider_var = None
        
        # État du test de connexion
        self.test_in_progress = False
        
        # Widgets pour accès direct
        self.model_combos: Dict[AIProvider, ttk.Combobox] = {}
        self.api_key_entries: Dict[AIProvider, ttk.Entry] = {}
        self.enabled_radiobuttons: Dict[AIProvider, ttk.Radiobutton] = {}
        self.test_button = None  # Référence au bouton de test
        
        # Créer la fenêtre
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.root.title("Configuration IA - BGRAPP Pyconseil")
        self.root.geometry("700x600")
        if parent_window:
            self.root.transient(parent_window.root if hasattr(parent_window, 'root') else parent_window)
            self.root.grab_set()  # Fenêtre modale
        
        self._setup_styles()
        self._init_variables()
        self._create_interface()
        self._load_current_config()
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_styles(self):
        """Configure les styles de l'interface"""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 10))
        style.configure('Success.TLabel', font=('Arial', 10), foreground='green')
        style.configure('Error.TLabel', font=('Arial', 10), foreground='red')
        style.configure('Warning.TLabel', font=('Arial', 10), foreground='orange')
    
    def _init_variables(self):
        """Initialise les variables tkinter"""
        for provider in AIProvider:
            self.api_key_vars[provider] = tk.StringVar(self.root)
            self.model_vars[provider] = tk.StringVar(self.root)
        
        self.active_provider_var = tk.StringVar(self.root)
        self.active_provider_var.set("openai")  # Valeur par défaut
    
    def _create_interface(self):
        """Crée l'interface de configuration"""
        # Frame principal avec scrollbar
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Titre
        title_label = ttk.Label(
            main_frame,
            text="🤖 Configuration des fournisseurs IA",
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)
        
        # Frame à onglets pour chaque fournisseur
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        main_frame.rowconfigure(1, weight=1)
        
        # Créer un onglet pour chaque fournisseur
        self.provider_frames = {}
        for provider in AIProvider:
            frame = self._create_provider_tab(provider)
            self.provider_frames[provider] = frame
            self.notebook.add(frame, text=self._get_provider_display_name(provider))
        
        # Section de statut
        self._create_status_section(main_frame, 2)
        
        # Boutons d'action
        self._create_action_buttons(main_frame, 3)
    
    def _create_provider_tab(self, provider: AIProvider) -> ttk.Frame:
        """Crée l'onglet de configuration pour un fournisseur"""
        frame = ttk.Frame(self.notebook, padding="10")
        frame.columnconfigure(1, weight=1)
        
        # Bouton radio d'activation (seul un fournisseur peut être actif)
        enabled_frame = ttk.Frame(frame)
        enabled_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.enabled_radiobuttons[provider] = ttk.Radiobutton(
            enabled_frame,
            text=f"Utiliser {self._get_provider_display_name(provider)}",
            variable=self.active_provider_var,
            value=provider.value,
            command=lambda p=provider: self._on_provider_selected(p)
        )
        self.enabled_radiobuttons[provider].grid(row=0, column=0, sticky=tk.W)
        
        # Configuration spécifique selon le provider
        if provider == AIProvider.LOCAL:
            # URL de base pour les LLMs locaux
            ttk.Label(frame, text="URL du serveur local:", style='Subtitle.TLabel').grid(
                row=1, column=0, sticky=tk.W, pady=(10, 5)
            )
            
            self.api_key_entries[provider] = ttk.Entry(
                frame,
                textvariable=self.api_key_vars[provider],
                width=50
                # Pas de masquage pour les URLs
            )
            self.api_key_entries[provider].grid(
                row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
            )
            
            # Info pour LOCAL
            local_info = ttk.Label(
                frame,
                text="Exemples: http://localhost:11434 (Ollama), http://localhost:1234 (LM Studio)",
                foreground="gray"
            )
            local_info.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        else:
            # Clé API pour les autres providers
            ttk.Label(frame, text="Clé API:", style='Subtitle.TLabel').grid(
                row=1, column=0, sticky=tk.W, pady=(10, 5)
            )
            
            self.api_key_entries[provider] = ttk.Entry(
                frame,
                textvariable=self.api_key_vars[provider],
                width=50,
                show="*"  # Masquer la clé API
            )
            self.api_key_entries[provider].grid(
                row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
            )
            
            # Bouton pour afficher/masquer la clé
            show_hide_btn = ttk.Button(
                frame,
                text="👁 Afficher",
                command=lambda p=provider: self._toggle_api_key_visibility(p)
            )
            show_hide_btn.grid(row=3, column=0, sticky=tk.W, pady=(0, 15))
        
        # Modèle
        ttk.Label(frame, text="Modèle:", style='Subtitle.TLabel').grid(
            row=4, column=0, sticky=tk.W, pady=(10, 5)
        )
        
        self.model_combos[provider] = ttk.Combobox(
            frame,
            textvariable=self.model_vars[provider],
            values=self.config_service.get_available_models(provider),
            state="readonly",
            width=40
        )
        self.model_combos[provider].grid(
            row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        
        # Informations sur le fournisseur
        info_label = ttk.Label(
            frame,
            text=self._get_provider_info(provider),
            style='Info.TLabel',
            wraplength=600
        )
        info_label.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        
        return frame
    

    
    def _create_status_section(self, parent: ttk.Frame, row: int):
        """Crée la section d'état de la configuration"""
        # Frame pour le statut
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=15)
        status_frame.columnconfigure(0, weight=1)
        
        ttk.Label(
            status_frame,
            text="📊 État de la configuration",
            style='Subtitle.TLabel'
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Zone de texte pour le statut
        self.status_text = tk.Text(
            status_frame,
            height=4,
            width=70,
            state='disabled',
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.status_text.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Scrollbar
        status_scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        status_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
    
    def _create_action_buttons(self, parent: ttk.Frame, row: int):
        """Crée les boutons d'action"""
        # Frame pour les boutons
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=15)
        
        # Bouton Test de connexion
        self.test_button = ttk.Button(
            button_frame,
            text="🔧 Tester la connexion",
            command=self._test_connection
        )
        self.test_button.grid(row=0, column=0, padx=(0, 10))
        
        # Bouton Sauvegarder
        save_btn = ttk.Button(
            button_frame,
            text="💾 Sauvegarder",
            command=self._save_configuration
        )
        save_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Bouton Annuler
        cancel_btn = ttk.Button(
            button_frame,
            text="❌ Annuler",
            command=self._on_closing
        )
        cancel_btn.grid(row=0, column=2, padx=(0, 20))
        
        # Bouton Aide
        help_btn = ttk.Button(
            button_frame,
            text="❓ Aide",
            command=self._show_help
        )
        help_btn.grid(row=0, column=3)
    
    def _get_provider_display_name(self, provider: AIProvider) -> str:
        """Récupère le nom d'affichage d'un fournisseur"""
        names = {
            AIProvider.OPENAI: "OpenAI",
            AIProvider.ANTHROPIC: "Anthropic Claude", 
            AIProvider.GEMINI: "Google Gemini",
            AIProvider.LOCAL: "LLM Local"
        }
        return names.get(provider, provider.value)
    
    def _get_provider_info(self, provider: AIProvider) -> str:
        """Récupère les informations d'un fournisseur"""
        infos = {
            AIProvider.OPENAI: "OpenAI GPT - Modèles polyvalents pour génération de texte et conversation. Recommandé : gpt-4o-mini pour un bon équilibre performance/coût.",
            AIProvider.ANTHROPIC: "Anthropic Claude - Modèles axés sur la sécurité et l'utilité. Excellent pour les tâches d'analyse et de rédaction longue.",
            AIProvider.GEMINI: "Google Gemini - Modèles multimodaux de Google. Bonne performance pour l'analyse de texte et la génération créative.",
            AIProvider.LOCAL: "LLM Local - Modèles locaux via Ollama, LM Studio, etc. Avantages : confidentialité, pas de coûts API, contrôle total. URL par défaut : http://localhost:11434"
        }
        return infos.get(provider, "")
    
    def _load_current_config(self):
        """Charge la configuration actuelle dans l'interface"""
        for provider in AIProvider:
            if provider == AIProvider.LOCAL:
                # Pour LOCAL, charger l'URL de base
                base_url = self.config_service.get_base_url(provider)
                if base_url:
                    self.api_key_vars[provider].set(base_url)
                else:
                    # URL par défaut pour LOCAL
                    self.api_key_vars[provider].set("http://localhost:11434")
            else:
                # Pour les autres, charger les clés API
                api_key = self.config_service.get_api_key(provider)
                if api_key:
                    self.api_key_vars[provider].set(api_key)
            
            # Charger les modèles
            model = self.config_service.get_model(provider)
            self.model_vars[provider].set(model)
        
        # Charger le fournisseur actif (pour sélectionner le bon bouton radio)
        active_provider = self.config_service.get_enabled_provider()
        if active_provider:
            self.active_provider_var.set(active_provider.value)
        
        # Mettre à jour le statut
        self._update_status()
    
    def _update_status(self):
        """Met à jour l'affichage du statut"""
        validation = self.config_service.validate_configuration()
        
        self.status_text.config(state='normal')
        self.status_text.delete(1.0, tk.END)
        
        # État général
        if validation['valid']:
            self.status_text.insert(tk.END, "✅ Configuration valide\n", "success")
        else:
            self.status_text.insert(tk.END, "❌ Configuration invalide\n", "error")
        
        # Fournisseurs avec clés
        providers_with_keys = validation['providers_with_keys']
        if providers_with_keys:
            names = [self._get_provider_display_name(p) for p in providers_with_keys]
            self.status_text.insert(tk.END, f"🔑 Clés configurées: {', '.join(names)}\n")
        
        # Fournisseur actif
        enabled_provider = validation['enabled_provider']
        if enabled_provider:
            name = self._get_provider_display_name(enabled_provider)
            self.status_text.insert(tk.END, f"🎯 Fournisseur actif: {name}\n")
        
        # Erreurs et avertissements
        for error in validation['errors']:
            self.status_text.insert(tk.END, f"❌ Erreur: {error}\n", "error")
        
        for warning in validation['warnings']:
            self.status_text.insert(tk.END, f"⚠️ Avertissement: {warning}\n", "warning")
        
        # Configuration des tags de couleur
        self.status_text.tag_config("success", foreground="green")
        self.status_text.tag_config("error", foreground="red")
        self.status_text.tag_config("warning", foreground="orange")
        
        self.status_text.config(state='disabled')
    
    def _toggle_api_key_visibility(self, provider: AIProvider):
        """Basculer la visibilité de la clé API"""
        entry = self.api_key_entries[provider]
        current_show = entry.cget('show')
        
        if current_show == '*':
            entry.config(show='')
        else:
            entry.config(show='*')
    
    def _on_provider_selected(self, provider: AIProvider):
        """Gère la sélection d'un fournisseur comme fournisseur actif"""
        try:
            # Le fournisseur sélectionné devient automatiquement le fournisseur actif
            self.config_service.set_enabled_provider(provider)
            self._update_status()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sélection du fournisseur: {e}")
    

    
    def _test_connection(self):
        """Teste la connexion avec le fournisseur actif"""
        if self.test_in_progress:
            return
        
        active_provider_str = self.active_provider_var.get()
        try:
            active_provider = AIProvider(active_provider_str)
        except ValueError:
            messagebox.showerror("Erreur", "Aucun fournisseur actif sélectionné")
            return
        
        # Vérifier la configuration selon le provider
        if active_provider == AIProvider.LOCAL:
            # Pour LOCAL, vérifier l'URL de base
            base_url = self.api_key_vars[active_provider].get().strip()
            if not base_url:
                messagebox.showerror(
                    "Erreur", 
                    f"Aucune URL configurée pour {self._get_provider_display_name(active_provider)}"
                )
                return
            api_key = ""  # Pas de clé API nécessaire pour LOCAL
        else:
            # Pour les autres providers, vérifier la clé API
            api_key = self.api_key_vars[active_provider].get().strip()
            if not api_key:
                messagebox.showerror(
                    "Erreur", 
                    f"Aucune clé API configurée pour {self._get_provider_display_name(active_provider)}"
                )
                return
        
        # Obtenir le modèle sélectionné
        model = self.model_vars[active_provider].get()
        if not model:
            messagebox.showerror("Erreur", f"Aucun modèle sélectionné pour {self._get_provider_display_name(active_provider)}")
            return
        
        # Lancer le test en arrière-plan
        self._start_connection_test(active_provider, api_key, model)
    
    def _start_connection_test(self, provider: AIProvider, api_key: str, model: str):
        """Lance le test de connexion en arrière-plan"""
        self.test_in_progress = True
        
        # Désactiver le bouton et changer le texte
        if self.test_button:
            self.test_button.config(state='disabled', text="🔄 Test en cours...")
        
        # Mettre à jour le statut
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, f"🔄 Test de connexion {self._get_provider_display_name(provider)} en cours...\n")
        self.status_text.config(state='disabled')
        self.status_text.see(tk.END)
        
        # Lancer le test dans un thread séparé
        def test_thread():
            try:
                result = self.test_service.test_connection(provider, api_key, model)
                # Programmer la mise à jour de l'interface dans le thread principal
                self.root.after(0, lambda: self._on_test_completed(result))
            except Exception as e:
                self.logger.error(f"Erreur dans le thread de test: {e}")
                self.root.after(0, lambda: self._on_test_error(str(e)))
        
        thread = threading.Thread(target=test_thread, daemon=True)
        thread.start()
    
    def _on_test_completed(self, result):
        """Gère la fin du test de connexion"""
        self.test_in_progress = False
        
        # Réactiver le bouton
        if self.test_button:
            self.test_button.config(state='normal', text="🔧 Tester la connexion")
        
        # Mettre à jour le statut
        self.status_text.config(state='normal')
        if result.success:
            self.status_text.insert(tk.END, f"{result.message}\n", "success")
            # Afficher les détails si disponibles
            if result.details and result.details.get('usage'):
                usage = result.details['usage']
                if isinstance(usage, dict):
                    if 'input_tokens' in usage:  # Anthropic
                        self.status_text.insert(tk.END, f"   📊 Tokens: {usage.get('input_tokens', 0)} entrée, {usage.get('output_tokens', 0)} sortie\n", "success")
                    elif 'prompt_token_count' in usage:  # Gemini
                        self.status_text.insert(tk.END, f"   📊 Tokens: {usage.get('prompt_token_count', 0)} prompt\n", "success")
                    elif 'total_tokens' in usage:  # OpenAI
                        self.status_text.insert(tk.END, f"   📊 Tokens: {usage.get('total_tokens', 0)} total\n", "success")
        else:
            self.status_text.insert(tk.END, f"{result.message}\n", "error")
            
            # Afficher des conseils selon le type d'erreur
            error_type = result.details.get('error_type', '')
            if error_type == 'client_missing':
                requirements = self.test_service.get_connection_requirements(AIProvider(self.active_provider_var.get()))
                if requirements:
                    self.status_text.insert(tk.END, f"   💡 Commande: {requirements.get('install_command', '')}\n", "warning")
            elif error_type == 'invalid_key':
                requirements = self.test_service.get_connection_requirements(AIProvider(self.active_provider_var.get()))
                if requirements:
                    self.status_text.insert(tk.END, f"   💡 Obtenez votre clé: {requirements.get('api_key_url', '')}\n", "warning")
        
        self.status_text.config(state='disabled')
        self.status_text.see(tk.END)
        
        # Afficher une messagebox avec le résultat
        if result.success:
            messagebox.showinfo("Test réussi", result.message)
        else:
            messagebox.showerror("Test échoué", result.message)
    
    def _on_test_error(self, error_message: str):
        """Gère les erreurs du test de connexion"""
        self.test_in_progress = False
        
        # Réactiver le bouton
        if self.test_button:
            self.test_button.config(state='normal', text="🔧 Tester la connexion")
        
        # Mettre à jour le statut
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, f"❌ Erreur lors du test: {error_message}\n", "error")
        self.status_text.config(state='disabled')
        self.status_text.see(tk.END)
        
        messagebox.showerror("Erreur de test", f"Erreur lors du test de connexion:\n{error_message}")
    
    def _save_configuration(self):
        """Sauvegarde la configuration"""
        try:
            # Sauvegarder les clés API/URLs et modèles
            for provider in AIProvider:
                value = self.api_key_vars[provider].get().strip()
                model = self.model_vars[provider].get()
                
                if provider == AIProvider.LOCAL:
                    # Pour LOCAL, sauvegarder l'URL de base
                    if value:
                        self.config_service.set_base_url(provider, value)
                else:
                    # Pour les autres, sauvegarder la clé API
                    self.config_service.set_api_key(provider, value)
                
                # Sauvegarder le modèle
                if model:
                    self.config_service.set_model(provider, model)
            
            # Sauvegarder le fournisseur actif (celui sélectionné par le bouton radio)
            active_provider_str = self.active_provider_var.get()
            if active_provider_str:
                try:
                    active_provider = AIProvider(active_provider_str)
                    # Vérifier la configuration selon le provider
                    if active_provider == AIProvider.LOCAL:
                        # LOCAL est toujours disponible s'il a une URL
                        base_url = self.config_service.get_base_url(active_provider)
                        if base_url:
                            self.config_service.set_enabled_provider(active_provider)
                        else:
                            messagebox.showwarning(
                                "Avertissement",
                                f"Impossible de définir {self._get_provider_display_name(active_provider)} "
                                f"comme fournisseur actif : aucune URL configurée"
                            )
                    else:
                        # Vérifier qu'il a une clé API pour les autres providers
                        if self.config_service.get_api_key(active_provider):
                            self.config_service.set_enabled_provider(active_provider)
                        else:
                            messagebox.showwarning(
                                "Avertissement",
                                f"Impossible de définir {self._get_provider_display_name(active_provider)} "
                                f"comme fournisseur actif : aucune clé API configurée"
                            )
                except ValueError:
                    pass
            
            # Mettre à jour le statut
            self._update_status()
            
            # Notifier le parent si callback fourni
            if self.on_config_changed:
                self.on_config_changed()
            
            messagebox.showinfo("Succès", "Configuration sauvegardée avec succès!")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def _show_help(self):
        """Affiche l'aide de configuration"""
        help_text = """
🤖 Aide - Configuration des fournisseurs IA

📋 Configuration des clés API:
• OpenAI: Obtenez votre clé sur https://platform.openai.com/api-keys
• Anthropic: Obtenez votre clé sur https://console.anthropic.com/
• Google Gemini: Obtenez votre clé sur https://makersuite.google.com/app/apikey

🎯 Sélection du modèle:
• Choisissez le modèle selon vos besoins de performance et coût
• Les modèles "mini" sont généralement plus économiques
• Les modèles plus grands offrent de meilleures performances

⚙️ Configuration:
1. Renseignez les clés API pour les fournisseurs souhaités
2. Sélectionnez les modèles préférés
3. Choisissez le fournisseur actif (boutons radio)
4. Testez la connexion
5. Sauvegardez

🔒 Sécurité:
• Les clés API sont stockées localement dans le fichier .env
• Elles ne sont jamais partagées ni transmises ailleurs
        """
        
        # Créer une fenêtre d'aide
        help_window = tk.Toplevel(self.root)
        help_window.title("Aide - Configuration IA")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Texte d'aide avec scrollbar
        text_frame = ttk.Frame(help_window, padding="10")
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        help_window.columnconfigure(0, weight=1)
        help_window.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        help_text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('Arial', 10),
            state='normal'
        )
        help_text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=help_text_widget.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        help_text_widget.configure(yscrollcommand=scrollbar.set)
        
        help_text_widget.insert(1.0, help_text)
        help_text_widget.config(state='disabled')
        
        # Bouton fermer
        close_btn = ttk.Button(
            text_frame,
            text="Fermer",
            command=help_window.destroy
        )
        close_btn.grid(row=1, column=0, pady=(10, 0))
    
    def _on_closing(self):
        """Gère la fermeture de la fenêtre"""
        self.root.destroy()
    
    def run(self):
        """Lance la fenêtre de configuration"""
        self.root.mainloop()


def main():
    """Point d'entrée pour les tests"""
    window = ConfigWindow()
    window.run()


if __name__ == "__main__":
    main() 