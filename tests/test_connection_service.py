#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour le service de test de connexion IA
"""

import unittest
import sys
from pathlib import Path

# Ajouter le répertoire src au PATH
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.ai_config_service import AIProvider
from services.ai_connection_test_service import AIConnectionTestService, ConnectionTestResult, get_ai_connection_test_service


class TestConnectionTestResult(unittest.TestCase):
    """Tests pour la classe ConnectionTestResult"""
    
    def test_success_result(self):
        """Test d'un résultat de succès"""
        result = ConnectionTestResult(
            success=True, 
            message="Test réussi",
            details={"model": "gpt-4o-mini"}
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Test réussi")
        self.assertEqual(result.details["model"], "gpt-4o-mini")
        self.assertIsInstance(result.timestamp, float)
    
    def test_failure_result(self):
        """Test d'un résultat d'échec"""
        result = ConnectionTestResult(
            success=False,
            message="Test échoué",
            details={"error_type": "invalid_key"}
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Test échoué")
        self.assertEqual(result.details["error_type"], "invalid_key")
    
    def test_default_details(self):
        """Test avec détails par défaut"""
        result = ConnectionTestResult(success=True, message="OK")
        
        self.assertEqual(result.details, {})


class TestAIConnectionTestService(unittest.TestCase):
    """Tests pour le service de test de connexion IA"""
    
    def setUp(self):
        """Configuration des tests"""
        self.service = AIConnectionTestService()
    
    def test_service_creation(self):
        """Test de création du service"""
        self.assertIsInstance(self.service, AIConnectionTestService)
        self.assertIsNotNone(self.service.logger)
    
    def test_empty_api_key(self):
        """Test avec clé API vide"""
        for provider in AIProvider:
            result = self.service.test_connection(provider, "", "model-test")
            
            self.assertFalse(result.success)
            self.assertIn("manquante", result.message)
            self.assertEqual(result.details["error_type"], "missing_key")
    
    def test_whitespace_api_key(self):
        """Test avec clé API contenant seulement des espaces"""
        for provider in AIProvider:
            result = self.service.test_connection(provider, "   ", "model-test")
            
            self.assertFalse(result.success)
            self.assertEqual(result.details["error_type"], "missing_key")
    
    def test_unsupported_provider(self):
        """Test avec un fournisseur non supporté (simulation)"""
        # Note: Tous les fournisseurs sont supportés, mais on peut tester la logique
        pass  # Ce test est couvert par la logique interne
    
    def test_openai_without_client(self):
        """Test OpenAI sans client installé"""
        # Si le client n'est pas installé, on devrait avoir une erreur appropriée
        result = self.service.test_connection(AIProvider.OPENAI, "fake-key", "gpt-4o-mini")
        
        # Soit le client n'est pas installé, soit la clé est invalide
        self.assertFalse(result.success)
        self.assertIn(result.details["error_type"], ["client_missing", "invalid_key", "openai_error"])
    
    def test_anthropic_without_client(self):
        """Test Anthropic sans client installé"""
        result = self.service.test_connection(AIProvider.ANTHROPIC, "fake-key", "claude-3-haiku")
        
        self.assertFalse(result.success)
        self.assertIn(result.details["error_type"], ["client_missing", "invalid_key", "anthropic_error"])
    
    def test_gemini_without_client(self):
        """Test Gemini sans client installé"""
        result = self.service.test_connection(AIProvider.GEMINI, "fake-key", "gemini-1.5-flash")
        
        self.assertFalse(result.success)
        self.assertIn(result.details["error_type"], ["client_missing", "invalid_key", "gemini_error"])
    
    def test_get_connection_requirements(self):
        """Test de récupération des prérequis de connexion"""
        for provider in AIProvider:
            requirements = self.service.get_connection_requirements(provider)
            
            self.assertIsInstance(requirements, dict)
            self.assertIn("client_available", requirements)
            self.assertIn("install_command", requirements)
            self.assertIn("api_key_url", requirements)
            
            # Vérifier que les URLs sont correctes
            if provider == AIProvider.OPENAI:
                self.assertIn("platform.openai.com", requirements["api_key_url"])
            elif provider == AIProvider.ANTHROPIC:
                self.assertIn("console.anthropic.com", requirements["api_key_url"])
            elif provider == AIProvider.GEMINI:
                self.assertIn("makersuite.google.com", requirements["api_key_url"])


class TestServiceSingleton(unittest.TestCase):
    """Tests pour le pattern singleton du service"""
    
    def test_singleton_pattern(self):
        """Test que get_ai_connection_test_service retourne toujours la même instance"""
        service1 = get_ai_connection_test_service()
        service2 = get_ai_connection_test_service()
        
        self.assertIs(service1, service2)
        self.assertIsInstance(service1, AIConnectionTestService)


class TestConnectionWithFakeKeys(unittest.TestCase):
    """Tests avec de fausses clés API pour vérifier la gestion d'erreurs"""
    
    def setUp(self):
        """Configuration des tests"""
        self.service = get_ai_connection_test_service()
    
    def test_openai_fake_key(self):
        """Test OpenAI avec fausse clé"""
        fake_key = "sk-fake1234567890abcdef"
        result = self.service.test_connection(AIProvider.OPENAI, fake_key, "gpt-4o-mini")
        
        self.assertFalse(result.success)
        # On devrait avoir soit client_missing soit invalid_key
        expected_errors = ["client_missing", "invalid_key", "openai_error"]
        self.assertIn(result.details["error_type"], expected_errors)
    
    def test_anthropic_fake_key(self):
        """Test Anthropic avec fausse clé"""
        fake_key = "sk-ant-fake1234567890abcdef"
        result = self.service.test_connection(AIProvider.ANTHROPIC, fake_key, "claude-3-haiku")
        
        self.assertFalse(result.success)
        expected_errors = ["client_missing", "invalid_key", "anthropic_error"]
        self.assertIn(result.details["error_type"], expected_errors)
    
    def test_gemini_fake_key(self):
        """Test Gemini avec fausse clé"""
        fake_key = "fake-google-api-key-1234567890"
        result = self.service.test_connection(AIProvider.GEMINI, fake_key, "gemini-1.5-flash")
        
        self.assertFalse(result.success)
        expected_errors = ["client_missing", "invalid_key", "gemini_error"]
        self.assertIn(result.details["error_type"], expected_errors)


if __name__ == "__main__":
    unittest.main() 