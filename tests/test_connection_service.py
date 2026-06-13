#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour le service de test de connexion IA multi-fournisseurs.
"""

import unittest
import sys
from pathlib import Path

# Ajouter le répertoire src/services au PATH (évite les imports lourds du package services)
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "services"))

from ai_config_service import AIProvider
from ai_connection_test_service import AIConnectionTestService, ConnectionTestResult, get_ai_connection_test_service


class TestConnectionTestResult(unittest.TestCase):
    """Tests pour la classe ConnectionTestResult"""
    
    def test_success_result(self):
        """Test d'un résultat de succès"""
        result = ConnectionTestResult(
            success=True, 
            message="Test réussi",
            details={"model": "gpt-5.1-mini"}
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Test réussi")
        self.assertEqual(result.details["model"], "gpt-5.1-mini")
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
    """Tests pour le service de test de connexion OpenAI."""
    
    def setUp(self):
        """Configuration des tests"""
        self.service = AIConnectionTestService()
    
    def test_service_creation(self):
        """Test de création du service"""
        self.assertIsInstance(self.service, AIConnectionTestService)
        self.assertIsNotNone(self.service.logger)
    
    def test_empty_api_key(self):
        """Test avec clé API vide."""
        result = self.service.test_connection(AIProvider.OPENAI, "", "gpt-5-mini")
        self.assertFalse(result.success)
        self.assertIn("manquante", result.message)
        self.assertEqual(result.details["error_type"], "missing_key")
    
    def test_whitespace_api_key(self):
        """Test avec clé API contenant seulement des espaces."""
        result = self.service.test_connection(AIProvider.OPENAI, "   ", "gpt-5-mini")
        self.assertFalse(result.success)
        self.assertEqual(result.details["error_type"], "missing_key")
    
    def test_unsupported_provider(self):
        """Test de fournisseur non supporté (simulation)."""
        class FakeProvider:
            value = "fake"
        result = self.service.test_connection(FakeProvider(), "sk-test", "gpt-5-mini")
        self.assertFalse(result.success)
        self.assertEqual(result.details["error_type"], "unsupported_provider")
    
    def test_openai_without_client(self):
        """Test OpenAI sans client installé."""
        result = self.service.test_connection(AIProvider.OPENAI, "fake-key", "gpt-5-mini")
        self.assertFalse(result.success)
        self.assertIn(result.details["error_type"], ["client_missing", "invalid_key", "openai_error"])
    
    def test_empty_api_key_anthropic(self):
        """Test Anthropic avec clé API vide."""
        result = self.service.test_connection(AIProvider.ANTHROPIC, "", "claude-sonnet-4-6")
        self.assertFalse(result.success)
        self.assertEqual(result.details["error_type"], "missing_key")

    def test_empty_api_key_gemini(self):
        """Test Gemini avec clé API vide."""
        result = self.service.test_connection(AIProvider.GEMINI, "", "gemini-2.5-flash")
        self.assertFalse(result.success)
        self.assertEqual(result.details["error_type"], "missing_key")

    def test_get_connection_requirements(self):
        """Test de récupération des prérequis de connexion (tous fournisseurs)."""
        expected_urls = {
            AIProvider.OPENAI: "platform.openai.com",
            AIProvider.ANTHROPIC: "anthropic.com",
            AIProvider.GEMINI: "google.com",
        }
        for provider, url_fragment in expected_urls.items():
            requirements = self.service.get_connection_requirements(provider)
            self.assertIsInstance(requirements, dict)
            self.assertIn("client_available", requirements)
            self.assertIn("install_command", requirements)
            self.assertIn("api_key_url", requirements)
            self.assertIn(url_fragment, requirements["api_key_url"])


class TestServiceSingleton(unittest.TestCase):
    """Tests pour le pattern singleton du service"""
    
    def test_singleton_pattern(self):
        """Test que get_ai_connection_test_service retourne toujours la même instance"""
        service1 = get_ai_connection_test_service()
        service2 = get_ai_connection_test_service()
        
        self.assertIs(service1, service2)
        self.assertIsInstance(service1, AIConnectionTestService)


class TestConnectionWithFakeKeys(unittest.TestCase):
    """Tests avec de fausses clés API pour vérifier la gestion d'erreurs."""
    
    def setUp(self):
        """Configuration des tests"""
        self.service = get_ai_connection_test_service()
    
    def test_openai_fake_key(self):
        """Test OpenAI avec fausse clé"""
        fake_key = "sk-fake1234567890abcdef"
        result = self.service.test_connection(AIProvider.OPENAI, fake_key, "gpt-5-mini")
        
        self.assertFalse(result.success)
        expected_errors = ["client_missing", "invalid_key", "openai_error"]
        self.assertIn(result.details["error_type"], expected_errors)


if __name__ == "__main__":
    unittest.main() 