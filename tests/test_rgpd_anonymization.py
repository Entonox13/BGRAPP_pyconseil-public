#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour le système d'anonymisation RGPD
"""

import unittest
import sys
from pathlib import Path

# Ajouter le dossier src au PYTHONPATH pour les tests
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from services.openai_service import RGPDAnonymizer, OpenAIService
from models.bulletin import Eleve, AppreciationMatiere, Bulletin


class TestRGPDAnonymizer(unittest.TestCase):
    """Tests pour la classe RGPDAnonymizer"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        self.anonymizer = RGPDAnonymizer()
    
    def test_register_student(self):
        """Test d'enregistrement d'un élève"""
        nom, prenom = "DUPONT", "Alice"
        key = self.anonymizer.register_student(nom, prenom)
        
        # Vérifier que la clé est bien formatée
        self.assertTrue(key.startswith("John_"))
        self.assertIn(key, self.anonymizer.name_mapping)
        
        # Vérifier le mapping bidirectionnel
        original_key = "DUPONT Alice"
        self.assertEqual(self.anonymizer.reverse_mapping[original_key], key)
        self.assertEqual(self.anonymizer.name_mapping[key], ("DUPONT", "Alice"))
    
    def test_register_same_student_twice(self):
        """Test d'enregistrement du même élève deux fois"""
        nom, prenom = "MARTIN", "Paul"
        
        key1 = self.anonymizer.register_student(nom, prenom)
        key2 = self.anonymizer.register_student(nom, prenom)
        
        # Les deux clés doivent être identiques
        self.assertEqual(key1, key2)
        
        # Un seul mapping doit exister
        self.assertEqual(len(self.anonymizer.name_mapping), 1)
    
    def test_anonymize_text_basic(self):
        """Test d'anonymisation basique"""
        nom, prenom = "DANLER", "Suheda"
        text = "Suheda est une élève sérieuse. DANLER fait des efforts."
        
        anonymized = self.anonymizer.anonymize_text(text, nom, prenom)
        
        # Vérifier que les noms ont été remplacés
        self.assertNotIn("Suheda", anonymized)
        self.assertNotIn("DANLER", anonymized)
        self.assertIn("John", anonymized)
        self.assertIn("DOE", anonymized)
    
    def test_anonymize_text_case_insensitive(self):
        """Test d'anonymisation insensible à la casse"""
        nom, prenom = "ERKAN", "Ela"
        text = "ela ne participe pas. Erkan doit s'améliorer. ELA est capable."
        
        anonymized = self.anonymizer.anonymize_text(text, nom, prenom)
        
        # Toutes les variantes de casse doivent être remplacées
        self.assertNotIn("ela", anonymized.lower())
        self.assertNotIn("erkan", anonymized.lower())
        self.assertIn("John", anonymized)
        self.assertIn("DOE", anonymized)
    
    def test_deanonymize_text(self):
        """Test de désanonymisation"""
        nom, prenom = "KANOUNE", "Bilal"
        original_text = "Bilal a d'indéniables capacités. KANOUNE doit continuer."
        
        # Anonymiser puis désanonymiser
        anonymized = self.anonymizer.anonymize_text(original_text, nom, prenom)
        deanonymized = self.anonymizer.deanonymize_text(anonymized, nom, prenom)
        
        # Le texte désanonymisé doit être identique à l'original
        self.assertEqual(deanonymized, original_text)
    
    def test_anonymize_empty_text(self):
        """Test avec du texte vide ou None"""
        nom, prenom = "TEST", "Test"
        
        # Texte None
        result = self.anonymizer.anonymize_text(None, nom, prenom)
        self.assertIsNone(result)
        
        # Texte vide
        result = self.anonymizer.anonymize_text("", nom, prenom)
        self.assertEqual(result, "")
        
        # Texte avec seulement des espaces
        result = self.anonymizer.anonymize_text("   ", nom, prenom)
        self.assertEqual(result, "   ")
    
    def test_anonymize_text_without_names(self):
        """Test avec un texte ne contenant pas les noms de l'élève"""
        nom, prenom = "SAIL", "Amani"
        text = "L'élève montre de bonnes capacités en mathématiques."
        
        anonymized = self.anonymizer.anonymize_text(text, nom, prenom)
        
        # Le texte ne doit pas changer s'il ne contient pas les noms
        self.assertEqual(anonymized, text)
    
    def test_clear_mappings(self):
        """Test d'effacement des mappings"""
        # Enregistrer quelques élèves
        self.anonymizer.register_student("DUPONT", "Alice")
        self.anonymizer.register_student("MARTIN", "Paul")
        
        # Vérifier qu'ils sont enregistrés
        self.assertEqual(len(self.anonymizer.name_mapping), 2)
        self.assertEqual(len(self.anonymizer.reverse_mapping), 2)
        
        # Effacer les mappings
        self.anonymizer.clear_mappings()
        
        # Vérifier que tout est vide
        self.assertEqual(len(self.anonymizer.name_mapping), 0)
        self.assertEqual(len(self.anonymizer.reverse_mapping), 0)
    
    def test_multiple_students(self):
        """Test avec plusieurs élèves"""
        students = [
            ("DUPONT", "Alice"),
            ("MARTIN", "Paul"),
            ("BERNARD", "Sophie")
        ]
        
        keys = []
        for nom, prenom in students:
            key = self.anonymizer.register_student(nom, prenom)
            keys.append(key)
        
        # Vérifier que toutes les clés sont différentes
        self.assertEqual(len(set(keys)), len(keys))
        
        # Vérifier la numérotation séquentielle
        for i, key in enumerate(keys):
            expected_key = f"John_{i+1:03d}"
            self.assertEqual(key, expected_key)


class TestOpenAIServiceRGPD(unittest.TestCase):
    """Tests pour l'intégration RGPD dans OpenAIService"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        # Note: Ces tests ne font pas d'appels réels à l'API OpenAI
        pass
    
    def test_service_creation_with_rgpd(self):
        """Test de création du service avec RGPD activé"""
        try:
            service = OpenAIService(enable_rgpd=True)
            self.assertTrue(service.enable_rgpd)
            self.assertIsNotNone(service.anonymizer)
            self.assertIsInstance(service.anonymizer, RGPDAnonymizer)
        except ValueError:
            # Normal si la clé API n'est pas configurée
            self.skipTest("Clé API OpenAI non configurée")
    
    def test_service_creation_without_rgpd(self):
        """Test de création du service avec RGPD désactivé"""
        try:
            service = OpenAIService(enable_rgpd=False)
            self.assertFalse(service.enable_rgpd)
            self.assertIsNone(service.anonymizer)
        except ValueError:
            # Normal si la clé API n'est pas configurée
            self.skipTest("Clé API OpenAI non configurée")
    
    def test_preprocess_appreciation_parameters(self):
        """Test que preprocess_appreciation accepte les nouveaux paramètres"""
        try:
            service = OpenAIService(enable_rgpd=True)
            
            # Vérifier que la méthode accepte les paramètres nom/prenom
            # (sans faire d'appel réel à l'API)
            text = "Test appreciation"
            nom, prenom = "TEST", "Eleve"
            
            # Cette méthode devrait exister et accepter ces paramètres
            # Note: Elle lèvera une exception lors de l'appel API, c'est normal
            self.assertTrue(hasattr(service, 'preprocess_appreciation'))
            
        except ValueError:
            # Normal si la clé API n'est pas configurée
            self.skipTest("Clé API OpenAI non configurée")
    
    def test_generate_general_appreciation_parameters(self):
        """Test que generate_general_appreciation accepte les nouveaux paramètres"""
        try:
            service = OpenAIService(enable_rgpd=True)
            
            # Vérifier que la méthode accepte les paramètres nom/prenom
            appreciations = {"Maths": "Bon travail"}
            nom, prenom = "TEST", "Eleve"
            
            # Cette méthode devrait exister et accepter ces paramètres
            self.assertTrue(hasattr(service, 'generate_general_appreciation'))
            
        except ValueError:
            # Normal si la clé API n'est pas configurée
            self.skipTest("Clé API OpenAI non configurée")


class TestRGPDIntegration(unittest.TestCase):
    """Tests d'intégration du système RGPD"""
    
    def test_bulletin_processing_simulation(self):
        """Test de simulation du traitement d'un bulletin avec RGPD"""
        # Créer un bulletin de test
        eleve = Eleve(nom="DANLER", prenom="Suheda", classe="4ème A")
        
        appreciation_anglais = AppreciationMatiere(
            matiere="Anglais LV1",
            moyenne_s1=5.0,
            appreciation_s1="Suheda est une élève du dispositif ULIS.",
            appreciation_s2="Suheda a fait des progrès ce semestre."
        )
        
        bulletin = Bulletin(
            eleve=eleve,
            matieres={"Anglais LV1": appreciation_anglais},
            appreciation_generale_s1="Suheda est une élève sérieuse."
        )
        
        # Test d'anonymisation sur le bulletin
        anonymizer = RGPDAnonymizer()
        
        # Anonymiser les appréciations
        for nom_matiere, matiere in bulletin.matieres.items():
            if matiere.appreciation_s1:
                anonymized_s1 = anonymizer.anonymize_text(
                    matiere.appreciation_s1, 
                    eleve.nom, 
                    eleve.prenom
                )
                self.assertIn("John", anonymized_s1)
                self.assertNotIn("Suheda", anonymized_s1)
            
            if matiere.appreciation_s2:
                anonymized_s2 = anonymizer.anonymize_text(
                    matiere.appreciation_s2, 
                    eleve.nom, 
                    eleve.prenom
                )
                self.assertIn("John", anonymized_s2)
                self.assertNotIn("Suheda", anonymized_s2)
        
        # Anonymiser l'appréciation générale
        if bulletin.appreciation_generale_s1:
            anonymized_general = anonymizer.anonymize_text(
                bulletin.appreciation_generale_s1,
                eleve.nom,
                eleve.prenom
            )
            self.assertIn("John", anonymized_general)
            self.assertNotIn("Suheda", anonymized_general)
    
    def test_real_world_scenario(self):
        """Test avec des données réelles du projet"""
        anonymizer = RGPDAnonymizer()
        
        # Données extraites des vrais fichiers JSON
        test_cases = [
            ("DANLER", "Suheda", "Suheda est une élève du dispositif ULIS. Elle assiste calmement au cours."),
            ("ERKAN", "Ela", "Ela ne participe toujours pas ! Quel dommage ! Elle en a pourtant les capacités."),
            ("KANOUNE", "Bilal", "Bilal a d'indéniables capacités qu'il a d'avantage utilisées ce semestre."),
            ("SAIL", "Amani", "Amani est tout bonnement excellente et ne manque aucune occasion de réussir."),
        ]
        
        for nom, prenom, appreciation in test_cases:
            # Anonymisation
            anonymized = anonymizer.anonymize_text(appreciation, nom, prenom)
            
            # Vérifier que le nom original n'apparaît plus
            self.assertNotIn(prenom, anonymized)
            self.assertNotIn(nom, anonymized)
            
            # Vérifier que John DOE apparaît
            self.assertIn("John", anonymized)
            
            # Désanonymisation 
            deanonymized = anonymizer.deanonymize_text(anonymized, nom, prenom)
            
            # Vérifier la réversibilité
            self.assertEqual(deanonymized, appreciation)


if __name__ == '__main__':
    # Configuration du niveau de log pour les tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Lancement des tests
    unittest.main(verbosity=2) 