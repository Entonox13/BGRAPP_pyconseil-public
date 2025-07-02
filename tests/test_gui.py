#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests pour l'interface graphique - Phase 4
"""

import pytest
import tkinter as tk
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Ajout du dossier src au PYTHONPATH pour les tests
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gui.main_window import MainWindow


class TestMainWindow:
    """Tests pour la fenêtre principale"""
    
    def setup_method(self):
        """Configuration avant chaque test"""
        # Créer une fenêtre de test sans l'afficher
        self.root = tk.Tk()
        self.root.withdraw()  # Cacher la fenêtre pour les tests
    
    def teardown_method(self):
        """Nettoyage après chaque test"""
        try:
            self.root.destroy()
        except tk.TclError:
            pass  # Fenêtre déjà détruite
    
    def test_main_window_creation(self):
        """Test de création de la fenêtre principale"""
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            # Créer la fenêtre
            window = MainWindow()
            
            # Vérifier que les méthodes de configuration ont été appelées
            mock_root.title.assert_called_once()
            mock_root.geometry.assert_called_once_with("800x600")
            mock_root.protocol.assert_called_once()
    
    def test_initial_state(self):
        """Test de l'état initial de l'interface"""
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            window = MainWindow()
            
            # Vérifier l'état initial
            assert window.selected_directory is None
            assert window.output_json_path is None
    
    @patch('gui.main_window.get_processing_summary')
    def test_analyze_directory_valid(self, mock_summary):
        """Test d'analyse d'un dossier valide"""
        # Configuration du mock
        mock_summary.return_value = {
            'valid_directory': True,
            'source_file_exists': True,
            'csv_files_count': 3,
            'csv_files': ['Mathématiques', 'Français', 'Histoire'],
            'estimated_bulletins': 24,
            'estimated_matieres': 3,
            'errors': []
        }
        
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            window = MainWindow()
            window.selected_directory = "/test/directory"
            
            # Mock des éléments GUI
            window.create_json_btn = Mock()
            window._log_message = Mock()
            window._update_directory_info = Mock()
            
            # Appeler la méthode
            window._analyze_directory()
            
            # Vérifications
            mock_summary.assert_called_once_with("/test/directory")
            window.create_json_btn.config.assert_called_with(state='normal')
            window._log_message.assert_called_with("✅ Dossier valide - Traitement possible", "success")
    
    @patch('gui.main_window.get_processing_summary')
    def test_analyze_directory_invalid(self, mock_summary):
        """Test d'analyse d'un dossier invalide"""
        # Configuration du mock
        mock_summary.return_value = {
            'valid_directory': False,
            'source_file_exists': False,
            'csv_files_count': 0,
            'csv_files': [],
            'estimated_bulletins': 0,
            'estimated_matieres': 0,
            'errors': ['Fichier source.xlsx manquant']
        }
        
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            window = MainWindow()
            window.selected_directory = "/test/invalid"
            
            # Mock des éléments GUI
            window.create_json_btn = Mock()
            window._log_message = Mock()
            window._update_directory_info = Mock()
            
            # Appeler la méthode
            window._analyze_directory()
            
            # Vérifications
            window.create_json_btn.config.assert_called_with(state='disabled')
            window._log_message.assert_called_with("❌ Dossier invalide - Vérifiez les fichiers requis", "error")
    
    @patch('gui.main_window.filedialog.askdirectory')
    def test_select_directory(self, mock_dialog):
        """Test de sélection de dossier"""
        mock_dialog.return_value = "/test/selected/directory"
        
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            window = MainWindow()
            
            # Mock des méthodes
            window._update_directory_display = Mock()
            window._analyze_directory = Mock()
            
            # Appeler la méthode
            window._select_directory()
            
            # Vérifications
            assert window.selected_directory == "/test/selected/directory"
            window._update_directory_display.assert_called_once()
            window._analyze_directory.assert_called_once()
    
    @patch('gui.main_window.filedialog.askdirectory')
    def test_select_directory_cancelled(self, mock_dialog):
        """Test d'annulation de sélection de dossier"""
        mock_dialog.return_value = ""  # Dialogue annulé
        
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            window = MainWindow()
            window._update_directory_display = Mock()
            window._analyze_directory = Mock()
            
            # Appeler la méthode
            window._select_directory()
            
            # Vérifications
            assert window.selected_directory is None
            window._update_directory_display.assert_not_called()
            window._analyze_directory.assert_not_called()
    
    @patch('gui.main_window.filedialog.asksaveasfilename')
    @patch('gui.main_window.threading.Thread')
    def test_create_json_process(self, mock_thread, mock_save_dialog):
        """Test du lancement de création JSON"""
        mock_save_dialog.return_value = "/test/output.json"
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            window = MainWindow()
            window.selected_directory = "/test/source"
            
            # Mock des éléments GUI
            window.create_json_btn = Mock()
            window.progress = Mock()
            window._log_message = Mock()
            
            # Appeler la méthode
            window._create_json()
            
            # Vérifications
            assert window.output_json_path == "/test/output.json"
            window.create_json_btn.config.assert_called_with(state='disabled')
            window.progress.start.assert_called_once()
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()
    
    @patch('gui.main_window.messagebox.showinfo')
    def test_open_edition_window_placeholder(self, mock_messagebox):
        """Test d'ouverture de la fenêtre d'édition (placeholder)"""
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            window = MainWindow()
            window._log_message = Mock()
            
            # Appeler la méthode
            window._open_edition_window()
            
            # Vérifications
            window._log_message.assert_called_with("📝 Ouverture de la fenêtre d'édition...")
            mock_messagebox.assert_called_once()
    
    @patch('gui.main_window.messagebox.showinfo')
    def test_open_conseil_window_placeholder(self, mock_messagebox):
        """Test d'ouverture de la fenêtre conseil (placeholder)"""
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            window = MainWindow()
            window._log_message = Mock()
            
            # Appeler la méthode
            window._open_conseil_window()
            
            # Vérifications
            window._log_message.assert_called_with("🎯 Ouverture de la fenêtre conseil...")
            mock_messagebox.assert_called_once()
    
    def test_log_message_formatting(self):
        """Test du formatage des messages de log"""
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            window = MainWindow()
            
            # Mock du widget Text
            window.status_text = Mock()
            
            # Test de log normal
            window._log_message("Test message")
            
            # Vérifier que le widget a été utilisé
            window.status_text.config.assert_called()
            window.status_text.insert.assert_called()
    
    @patch('gui.main_window.messagebox.askokcancel')
    def test_on_closing_confirmed(self, mock_dialog):
        """Test de fermeture confirmée"""
        mock_dialog.return_value = True
        
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            window = MainWindow()
            
            # Appeler la méthode
            window._on_closing()
            
            # Vérifications
            mock_root.quit.assert_called_once()
            mock_root.destroy.assert_called_once()
    
    @patch('gui.main_window.messagebox.askokcancel')
    def test_on_closing_cancelled(self, mock_dialog):
        """Test de fermeture annulée"""
        mock_dialog.return_value = False
        
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            window = MainWindow()
            
            # Appeler la méthode
            window._on_closing()
            
            # Vérifications
            mock_root.quit.assert_not_called()
            mock_root.destroy.assert_not_called()


def test_main_function():
    """Test de la fonction main du module"""
    with patch('gui.main_window.MainWindow') as mock_window:
        mock_app = Mock()
        mock_window.return_value = mock_app
        
        # Importer et appeler main
        from gui.main_window import main
        main()
        
        # Vérifications
        mock_window.assert_called_once()
        mock_app.run.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__]) 