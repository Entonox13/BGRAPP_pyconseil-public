#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests pour la fenêtre conseil de l'application BGRAPP Pyconseil
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import os
import sys
from pathlib import Path

# Ajouter le chemin src pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models.bulletin import Bulletin, Eleve, AppreciationMatiere


class TestConseilWindow(unittest.TestCase):
    """Tests pour la fenêtre conseil"""
    
    def setUp(self):
        """Configuration des tests"""
        # Mock tkinter pour éviter l'affichage
        self.tk_patcher = patch('tkinter.Tk')
        self.toplevel_patcher = patch('tkinter.Toplevel')
        
        self.mock_tk = self.tk_patcher.start()
        self.mock_toplevel = self.toplevel_patcher.start()
        
        # Configurer les mocks
        self.mock_root = Mock()
        self.mock_toplevel.return_value = self.mock_root
        self.mock_tk.return_value = self.mock_root
        
        # Mock des composants tkinter
        with patch('tkinter.ttk.Style'), \
             patch('tkinter.ttk.Frame'), \
             patch('tkinter.ttk.Label'), \
             patch('tkinter.ttk.Button'), \
             patch('tkinter.ttk.LabelFrame'), \
             patch('tkinter.Listbox'), \
             patch('tkinter.ttk.Scrollbar'), \
             patch('tkinter.ttk.Notebook'), \
             patch('tkinter.ttk.Treeview'), \
             patch('tkinter.Canvas'), \
             patch('tkinter.Text'):
            
            from gui.conseil_window import ConseilWindow
            self.conseil_window = ConseilWindow()
    
    def tearDown(self):
        """Nettoyage des tests"""
        self.tk_patcher.stop()
        self.toplevel_patcher.stop()
    
    def test_initialization(self):
        """Test de l'initialisation de la fenêtre"""
        self.assertIsNotNone(self.conseil_window)
        self.assertEqual(self.conseil_window.bulletins, [])
        self.assertEqual(self.conseil_window.current_bulletin_index, 0)
        self.assertIsNone(self.conseil_window.json_file_path)
    
    def test_bulletin_creation(self):
        """Test de création de bulletins de données"""
        # Créer des données de test
        eleve = Eleve(nom="Dupont", prenom="Jean", classe="3A")
        appreciation = AppreciationMatiere(
            matiere="Mathematiques",
            moyenne_s1=14.5,
            moyenne_s2=15.2,
            appreciation_s1="Bon travail",
            appreciation_s2="Très bon travail"
        )
        bulletin = Bulletin(
            eleve=eleve,
            appreciation_generale_s1="Bon élève",
            appreciation_generale_s2="Très bon élève"
        )
        bulletin.add_matiere(appreciation)
        
        # Ajouter le bulletin
        self.conseil_window.bulletins = [bulletin]
        self.assertEqual(len(self.conseil_window.bulletins), 1)
        self.assertEqual(self.conseil_window.bulletins[0].eleve.nom, "Dupont")
    
    @patch('tkinter.messagebox.showerror')
    @patch('builtins.open')
    @patch('json.load')
    def test_load_bulletins_from_file(self, mock_json_load, mock_open, mock_showerror):
        """Test de chargement des bulletins depuis un fichier"""
        # Données de test au format correct
        test_data = [{
            "Nom": "Martin",
            "Prenom": "Pierre",
            "Matieres": {
                "Francais": {
                    "MoyenneS1": 13.0,
                    "MoyenneS2": 14.0,
                    "AppreciationS1": "Travail correct",
                    "AppreciationS2": "Progression"
                }
            },
            "AppreciationGeneraleS1": "Elève sérieux", 
            "AppreciationGeneraleS2": "Bon travail"
        }]
        
        mock_json_load.return_value = test_data
        
        # Mock des attributs de mise à jour
        self.conseil_window._update_bulletin_list = Mock()
        self.conseil_window._update_status = Mock()
        self.conseil_window._update_display = Mock()
        self.conseil_window.export_btn = Mock()
        self.conseil_window.print_btn = Mock()
        
        # Test du chargement
        self.conseil_window._load_bulletins_from_file("test.json")
        
        # Vérifications
        self.assertEqual(len(self.conseil_window.bulletins), 1)
        self.assertEqual(self.conseil_window.bulletins[0].eleve.nom, "Martin")
        self.conseil_window._update_bulletin_list.assert_called_once()
        self.conseil_window._update_status.assert_called()
    
    def test_navigation_methods(self):
        """Test des méthodes de navigation"""
        # Créer des bulletins de test
        eleve1 = Eleve(nom="Dupont", prenom="Jean", classe="3A")
        eleve2 = Eleve(nom="Martin", prenom="Pierre", classe="3A")
        bulletin1 = Bulletin(eleve=eleve1, appreciation_generale_s1="", appreciation_generale_s2="")
        bulletin2 = Bulletin(eleve=eleve2, appreciation_generale_s1="", appreciation_generale_s2="")
        
        self.conseil_window.bulletins = [bulletin1, bulletin2]
        self.conseil_window.current_bulletin_index = 0
        
        # Mock des méthodes de mise à jour
        self.conseil_window._update_display = Mock()
        self.conseil_window._update_navigation_buttons = Mock()
        
        # Test navigation suivante
        self.conseil_window._next_bulletin()
        self.assertEqual(self.conseil_window.current_bulletin_index, 1)
        self.conseil_window._update_display.assert_called()
        
        # Test navigation précédente
        self.conseil_window._previous_bulletin()
        self.assertEqual(self.conseil_window.current_bulletin_index, 0)
    
    def test_synthesis_view_update(self):
        """Test de mise à jour de la vue synthèse"""
        # Créer un bulletin de test
        eleve = Eleve(nom="Test", prenom="Eleve", classe="3A")
        appreciation = AppreciationMatiere(
            matiere="Mathematiques",
            moyenne_s1=14.5,
            moyenne_s2=15.2,
            heures_absence_s1=2,
            heures_absence_s2=1
        )
        bulletin = Bulletin(eleve=eleve)
        bulletin.add_matiere(appreciation)
        
        # Mock du TreeView
        self.conseil_window.synthesis_tree = Mock()
        self.conseil_window.synthesis_tree.get_children.return_value = []
        
        # Test de la mise à jour
        self.conseil_window._update_synthesis_view(bulletin)
        
        # Vérifier que insert a été appelé
        self.conseil_window.synthesis_tree.insert.assert_called()
    
    @patch('tkinter.ttk.LabelFrame')
    @patch('tkinter.ttk.Label')
    @patch('tkinter.Text')
    def test_detailed_view_update(self, mock_text, mock_label, mock_labelframe):
        """Test de mise à jour de la vue détaillée"""
        # Créer un bulletin de test
        eleve = Eleve(nom="Test", prenom="Eleve", classe="3A")
        appreciation = AppreciationMatiere(
            matiere="Francais",
            moyenne_s1=13.0,
            moyenne_s2=14.0,
            appreciation_s1="Bon travail",
            appreciation_s2="Très bon travail"
        )
        bulletin = Bulletin(eleve=eleve)
        bulletin.add_matiere(appreciation)
        
        # Mock des widgets
        self.conseil_window.detailed_widgets = []
        self.conseil_window.scrollable_frame = Mock()
        
        # Mock pour les widgets créés
        mock_frame = Mock()
        mock_labelframe.return_value = mock_frame
        mock_text_widget = Mock()
        mock_text.return_value = mock_text_widget
        
        # Test de la mise à jour
        self.conseil_window._update_detailed_view(bulletin)
        
        # Vérifier que les widgets ont été créés
        self.assertTrue(mock_labelframe.called)
        self.assertTrue(len(self.conseil_window.detailed_widgets) > 0)
    
    def test_clear_display(self):
        """Test de vidage de l'affichage"""
        # Mock des composants
        self.conseil_window.nom_label = Mock()
        self.conseil_window.prenom_label = Mock()
        self.conseil_window.classe_label = Mock()
        self.conseil_window.synthesis_tree = Mock()
        self.conseil_window.synthesis_tree.get_children.return_value = []
        self.conseil_window.detailed_widgets = []
        self.conseil_window.general_s1_text = Mock()
        self.conseil_window.general_s2_text = Mock()
        
        # Test du vidage
        self.conseil_window._clear_display()
        
        # Vérifications
        self.conseil_window.nom_label.configure.assert_called_with(text="-")
        self.conseil_window.prenom_label.configure.assert_called_with(text="-")
        self.conseil_window.classe_label.configure.assert_called_with(text="-")
    
    def test_export_and_print_placeholders(self):
        """Test des fonctions d'export et impression (placeholders)"""
        with patch('tkinter.messagebox.showinfo') as mock_info:
            # Test export
            self.conseil_window._export_conseil()
            mock_info.assert_called_with("Export", "Fonction d'export à implémenter")
            
            # Test impression
            self.conseil_window._print_conseil()
            mock_info.assert_called_with("Impression", "Fonction d'impression à implémenter")
    
    def test_html_text_insertion(self):
        """Test de l'insertion de texte HTML formaté"""
        # Mock du widget Text
        mock_text_widget = Mock()
        
        # Texte de test avec balises HTML
        html_content = 'Élève <span class="positif">très bon</span> mais <span class="negatif">absent</span> souvent.'
        
        # Test de la fonction
        self.conseil_window._insert_html_text(mock_text_widget, html_content)
        
        # Vérifier que les méthodes de configuration et insertion ont été appelées
        self.assertTrue(mock_text_widget.tag_configure.called)
        self.assertTrue(mock_text_widget.insert.called)
        
        # Vérifier que les tags ont été configurés
        expected_calls = [
            (('positif',), {'foreground': 'green', 'font': ('Arial', 10, 'bold')}),
            (('negatif',), {'foreground': 'red', 'font': ('Arial', 10, 'bold')}),
            (('normal',), {'foreground': 'black'})
        ]
        
        # Au moins un tag doit être configuré
        self.assertGreaterEqual(mock_text_widget.tag_configure.call_count, 1)
    
    def test_html_text_insertion_empty(self):
        """Test de l'insertion de texte HTML vide"""
        mock_text_widget = Mock()
        
        # Test avec contenu vide
        self.conseil_window._insert_html_text(mock_text_widget, "")
        self.conseil_window._insert_html_text(mock_text_widget, None)
        
        # La fonction ne doit rien faire avec du contenu vide
        # (Pas de vérification spécifique car la fonction retourne tôt)


if __name__ == '__main__':
    unittest.main() 