#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour la configuration IA multi-fournisseurs.
"""

import unittest
import sys
from pathlib import Path

# Ajouter src/services au path pour éviter les imports transverses
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'services'))

from ai_config_service import AIProvider, AIConfigService, get_ai_config_service


class TestAIConfigService(unittest.TestCase):
    """Tests pour le service de configuration IA"""
    
    def setUp(self):
        """Préparation des tests"""
        self.config_service = AIConfigService()
    
    def test_provider_enum(self):
        """Test de l'énumération des fournisseurs"""
        providers = list(AIProvider)
        self.assertEqual(len(providers), 3)
        self.assertIn(AIProvider.OPENAI, providers)
        self.assertIn(AIProvider.ANTHROPIC, providers)
        self.assertIn(AIProvider.GEMINI, providers)
    
    def test_available_models(self):
        """Test de la récupération des modèles disponibles"""
        for provider in AIProvider:
            models = self.config_service.get_available_models(provider)
            self.assertIsInstance(models, list)
            self.assertGreater(len(models), 0)
            self.assertIsInstance(models[0], str)

    def test_model_roles(self):
        """Test des deux rôles de modèle (prétraitement / appréciation)"""
        self.assertEqual(set(self.config_service.MODEL_ROLES), {"preprocess", "generation"})
        for provider in AIProvider:
            for role in self.config_service.MODEL_ROLES:
                model = self.config_service.get_model(provider, role=role)
                self.assertIsInstance(model, str)
                self.assertTrue(model)

    def test_set_model_per_role_independent(self):
        """Définir un modèle par rôle ne doit pas affecter l'autre rôle"""
        provider = AIProvider.OPENAI
        models = self.config_service.get_available_models(provider)
        self.assertGreaterEqual(len(models), 2)

        # Sauvegarder pour restaurer (set_model persiste dans .env)
        original = {
            role: self.config_service.get_model(provider, role=role)
            for role in self.config_service.MODEL_ROLES
        }
        try:
            self.config_service.set_model(provider, models[0], role="preprocess")
            self.config_service.set_model(provider, models[1], role="generation")
            self.assertEqual(self.config_service.get_model(provider, role="preprocess"), models[0])
            self.assertEqual(self.config_service.get_model(provider, role="generation"), models[1])
        finally:
            for role, model in original.items():
                self.config_service.set_model(provider, model, role=role)
    
    def test_validation(self):
        """Test de la validation de configuration"""
        validation = self.config_service.validate_configuration()
        
        self.assertIsInstance(validation, dict)
        self.assertIn('valid', validation)
        self.assertIn('errors', validation)
        self.assertIn('warnings', validation)
        self.assertIn('providers_with_keys', validation)
        self.assertIn('enabled_provider', validation)


class TestEnvironmentFile(unittest.TestCase):
    """Tests pour le fichier .env"""
    
    def test_env_file_exists(self):
        """Test de l'existence du fichier .env"""
        repo_root = Path(__file__).parent.parent
        env_path = repo_root / '.env'
        env_example = repo_root / 'env.example'
        self.assertTrue(
            env_path.exists() or env_example.exists(),
            "Ni .env ni env.example n'existent à la racine du projet"
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
