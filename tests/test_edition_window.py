#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour la fenêtre d'édition
"""

import unittest
import tempfile
import json
import os
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Import du module à tester
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.gui.edition_window import EditionWindow
from src.models.bulletin import Bulletin, Eleve, AppreciationMatiere


class TestEditionWindow(unittest.TestCase):
    """Tests pour la fenêtre d'édition"""
    
    def setUp(self):
        """Initialisation des tests"""
        self.test_bulletins_data = [
            {
                "Nom": "DUPONT",
                "Prenom": "Alice",
                "AppreciationGeneraleS1": "Bon travail",
                "AppreciationGeneraleS2": "Continue ainsi",
                "Matieres": {
                    "Mathématiques": {
                        "MoyenneS1": 15.5,
                        "MoyenneS2": 16.0,
                        "HeuresAbsenceS1": 2,
                        "HeuresAbsenceS2": 1,
                        "AppreciationS1": "Bon niveau",
                        "AppreciationS2": "Très bon travail"
                    }
                }
            }
        ]
        
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False, encoding='utf-8'
        )
        json.dump(self.test_bulletins_data, self.temp_file, ensure_ascii=False, indent=2)
        self.temp_file.close()
    
    def tearDown(self):
        """Nettoyage après les tests"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    @patch('tkinter.Tk')
    def test_edition_window_creation(self, mock_tk):
        """Test de création de la fenêtre d'édition"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        window = EditionWindow()
        
        self.assertIsNotNone(window)
        self.assertEqual(window.bulletins, [])
        self.assertEqual(window.current_bulletin_index, 0)
    
    @patch('tkinter.Tk')
    def test_load_bulletins_from_file(self, mock_tk):
        """Test du chargement des bulletins"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        window = EditionWindow()
        window._update_bulletin_list = Mock()
        window._update_display = Mock()
        window._update_status = Mock()
        
        window._load_bulletins_from_file(self.temp_file.name)
        
        self.assertEqual(len(window.bulletins), 1)
        self.assertEqual(window.bulletins[0].eleve.nom, "DUPONT")
        self.assertEqual(window.bulletins[0].eleve.prenom, "Alice")
    
    @patch('tkinter.Tk')
    def test_bulletin_navigation(self, mock_tk):
        """Test de la navigation entre bulletins"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        window = EditionWindow()
        window._update_display = Mock()
        window._update_navigation_buttons = Mock()
        window._update_position_indicator = Mock()
        window.bulletin_list = Mock()
        
        # Charger 2 bulletins
        bulletins_data = self.test_bulletins_data + [
            {
                "Nom": "MARTIN",
                "Prenom": "Pierre",
                "AppreciationGeneraleS1": "Élève sérieux",
                "Matieres": {}
            }
        ]
        
        window.bulletins = [Bulletin.from_dict(data) for data in bulletins_data]
        window.current_bulletin_index = 0
        
        # Test navigation suivante
        window._next_bulletin()
        self.assertEqual(window.current_bulletin_index, 1)
        
        # Test navigation précédente
        window._previous_bulletin()
        self.assertEqual(window.current_bulletin_index, 0)
    
    @patch('tkinter.Tk')
    def test_save_changes(self, mock_tk):
        """Test de la sauvegarde"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        window = EditionWindow()
        window.json_file_path = self.temp_file.name
        window._update_status = Mock()
        
        # Mock les zones de texte
        window.general_s1_text = Mock()
        window.general_s1_text.get.return_value = "Nouvelle appréciation S1\n"
        window.general_s2_text = Mock()
        window.general_s2_text.get.return_value = "Nouvelle appréciation S2\n"
        
        window.bulletins = [Bulletin.from_dict(self.test_bulletins_data[0])]
        window.current_bulletin_index = 0
        
        window._save_changes()
        
        # Vérifier la sauvegarde
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data[0]["AppreciationGeneraleS1"], "Nouvelle appréciation S1")
        self.assertEqual(saved_data[0]["AppreciationGeneraleS2"], "Nouvelle appréciation S2")
    
    @patch('tkinter.Tk')
    def test_placeholder_methods(self, mock_tk):
        """Test des méthodes placeholder pour OpenAI"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        window = EditionWindow()
        
        with patch('src.gui.edition_window.messagebox') as mock_messagebox:
            window._preprocess_text()
            mock_messagebox.showinfo.assert_called_with("Prétraitement", "Fonction à implémenter en Phase 6")
            
            window._generate_general()
            mock_messagebox.showinfo.assert_called_with("Génération", "Fonction à implémenter en Phase 6")


if __name__ == '__main__':
    unittest.main(verbosity=2) 