#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour la fonctionnalité de chargement JSON dans la fenêtre principale
"""

import unittest
import tempfile
import json
import os
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


class TestMainWindowLoadJSON(unittest.TestCase):
    """Tests pour la fonctionnalité de chargement JSON"""
    
    def setUp(self):
        """Configuration des tests"""
        if not TKINTER_AVAILABLE:
            self.skipTest("tkinter n'est pas disponible")
        
        # Mock des modules tkinter pour éviter l'affichage GUI
        self.tk_patch = patch('tkinter.Tk')
        self.mock_tk = self.tk_patch.start()
        
        # Mock de la fenêtre racine
        self.mock_root = MagicMock()
        self.mock_tk.return_value = self.mock_root
        
        # Import après le mock
        from gui.main_window import MainWindow
        self.MainWindow = MainWindow
    
    def tearDown(self):
        """Nettoyage après les tests"""
        if hasattr(self, 'tk_patch'):
            self.tk_patch.stop()
    
    def create_valid_json_file(self):
        """Crée un fichier JSON valide pour les tests"""
        valid_data = [
            {
                "Nom": "DUPONT",
                "Prenom": "Jean",
                "AppreciationGeneraleS1": "Bon trimestre",
                "Matieres": {
                    "mathematiques": {
                        "AppreciationS1": "Bon travail",
                        "AppreciationS2": "Très bon travail",
                        "MoyenneS1": 14.5,
                        "MoyenneS2": 15.2,
                        "HeuresAbsenceS1": 0,
                        "HeuresAbsenceS2": 0
                    }
                }
            }
        ]
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(valid_data, temp_file, ensure_ascii=False, indent=2)
        temp_file.close()
        return temp_file.name
    
    def create_invalid_json_file(self):
        """Crée un fichier JSON invalide pour les tests"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write("{ invalid json content")
        temp_file.close()
        return temp_file.name
    
    def create_empty_json_file(self):
        """Crée un fichier JSON vide pour les tests"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump([], temp_file)
        temp_file.close()
        return temp_file.name
    
    @patch('tkinter.filedialog.askopenfilename')
    @patch('tkinter.messagebox.showinfo')
    def test_load_valid_json_success(self, mock_showinfo, mock_filedialog):
        """Test du chargement réussi d'un JSON valide"""
        # Créer un fichier JSON valide
        json_file = self.create_valid_json_file()
        
        try:
            # Configuration des mocks
            mock_filedialog.return_value = json_file
            
            # Créer l'instance
            window = self.MainWindow()
            
            # Simuler l'appel à la méthode
            window._load_existing_json()
            
            # Vérifications
            self.assertEqual(window.output_json_path, json_file)
            mock_showinfo.assert_called_once()
            
            # Vérifier le message de succès
            call_args = mock_showinfo.call_args
            self.assertIn("Chargement réussi", call_args[0][0])
            self.assertIn("1 bulletin(s) trouvé(s)", call_args[0][1])
            
        finally:
            # Nettoyage
            os.unlink(json_file)
    
    @patch('tkinter.filedialog.askopenfilename')
    @patch('tkinter.messagebox.showerror')
    def test_load_invalid_json_error(self, mock_showerror, mock_filedialog):
        """Test du chargement d'un JSON invalide"""
        # Créer un fichier JSON invalide
        json_file = self.create_invalid_json_file()
        
        try:
            # Configuration des mocks
            mock_filedialog.return_value = json_file
            
            # Créer l'instance
            window = self.MainWindow()
            
            # Simuler l'appel à la méthode
            window._load_existing_json()
            
            # Vérifications
            self.assertIsNone(window.output_json_path)
            mock_showerror.assert_called_once()
            
            # Vérifier le message d'erreur
            call_args = mock_showerror.call_args
            self.assertIn("Erreur de format", call_args[0][0])
            
        finally:
            # Nettoyage
            os.unlink(json_file)
    
    @patch('tkinter.filedialog.askopenfilename')
    @patch('tkinter.messagebox.showerror')
    def test_load_empty_json_error(self, mock_showerror, mock_filedialog):
        """Test du chargement d'un JSON vide"""
        # Créer un fichier JSON vide
        json_file = self.create_empty_json_file()
        
        try:
            # Configuration des mocks
            mock_filedialog.return_value = json_file
            
            # Créer l'instance
            window = self.MainWindow()
            
            # Simuler l'appel à la méthode
            window._load_existing_json()
            
            # Vérifications
            self.assertIsNone(window.output_json_path)
            mock_showerror.assert_called_once()
            
            # Vérifier le message d'erreur
            call_args = mock_showerror.call_args
            self.assertIn("Erreur de structure", call_args[0][0])
            self.assertIn("ne contient aucun bulletin", call_args[0][1])
            
        finally:
            # Nettoyage
            os.unlink(json_file)
    
    @patch('tkinter.filedialog.askopenfilename')
    def test_load_json_cancelled(self, mock_filedialog):
        """Test de l'annulation du dialog de sélection"""
        # Configuration du mock pour retourner None (annulation)
        mock_filedialog.return_value = None
        
        # Créer l'instance
        window = self.MainWindow()
        original_path = window.output_json_path
        
        # Simuler l'appel à la méthode
        window._load_existing_json()
        
        # Vérifications - l'état ne doit pas changer
        self.assertEqual(window.output_json_path, original_path)
    
    def test_button_exists_in_processing_section(self):
        """Test que le bouton de chargement existe dans l'interface"""
        # Créer l'instance
        window = self.MainWindow()
        
        # Vérifier que l'attribut load_json_btn existe
        self.assertTrue(hasattr(window, 'load_json_btn'))
        
        # Vérifier que c'est bien un bouton
        self.assertIsNotNone(window.load_json_btn)


if __name__ == '__main__':
    unittest.main() 