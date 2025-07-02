#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour la fenêtre de configuration IA
Test des fonctionnalités de configuration multi-fournisseurs
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Ajouter le dossier src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.services.ai_config_service import AIProvider, AIConfigService, get_ai_config_service


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
        env_path = Path(__file__).parent.parent / '.env'
        self.assertTrue(env_path.exists(), "Le fichier .env n'existe pas")


if __name__ == '__main__':
    unittest.main(verbosity=2)
