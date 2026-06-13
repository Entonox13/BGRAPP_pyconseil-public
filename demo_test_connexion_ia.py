#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Démonstration des tests de connexion IA - BGRAPP Pyconseil
Script pour tester la fonctionnalité de test de connexion aux fournisseurs IA
"""

import logging
import sys
from pathlib import Path

# Ajouter le répertoire src au PATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.ai_config_service import AIProvider, get_ai_config_service
from services.ai_connection_test_service import get_ai_connection_test_service

def setup_logging():
    """Configure le logging pour les tests"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_without_api_keys():
    """Teste les connexions sans clés API configurées"""
    print("=" * 60)
    print("TEST 1: Tests sans clés API configurées")
    print("=" * 60)
    
    test_service = get_ai_connection_test_service()
    
    sample_models = {
        AIProvider.OPENAI: "gpt-5.4-mini",
        AIProvider.ANTHROPIC: "claude-sonnet-4-6",
        AIProvider.GEMINI: "gemini-2.5-flash",
    }
    
    for provider in AIProvider:
        print(f"\n🔧 Test de {provider.value}...")
        
        # Test avec clé vide
        model = sample_models.get(provider, "gpt-5.4-mini")
        result = test_service.test_connection(provider, "", model)
        print(f"   Résultat: {'✅' if result.success else '❌'} {result.message}")
        
        # Afficher les prérequis
        requirements = test_service.get_connection_requirements(provider)
        if requirements:
            print(f"   Client disponible: {'✅' if requirements['client_available'] else '❌'}")
            if not requirements['client_available']:
                print(f"   Installation: {requirements['install_command']}")

def test_with_fake_keys():
    """Teste les connexions avec de fausses clés API"""
    print("\n" + "=" * 60)
    print("TEST 2: Tests avec de fausses clés API")
    print("=" * 60)
    
    test_service = get_ai_connection_test_service()
    config_service = get_ai_config_service()
    
    fake_keys = {
        AIProvider.OPENAI: "sk-fake1234567890abcdef",
        AIProvider.ANTHROPIC: "sk-ant-fake1234567890abcdef", 
        AIProvider.GEMINI: "fake-google-api-key-1234567890"
    }
    
    for provider in AIProvider:
        print(f"\n🔧 Test de {provider.value} avec fausse clé...")
        
        fake_key = fake_keys.get(provider, "fake-key-1234567890")
        model = config_service.get_model(provider)
        
        result = test_service.test_connection(provider, fake_key, model)
        print(f"   Résultat: {'✅' if result.success else '❌'} {result.message}")
        
        if result.details:
            error_type = result.details.get('error_type', 'unknown')
            print(f"   Type d'erreur: {error_type}")

def test_client_availability():
    """Teste la disponibilité des clients IA"""
    print("\n" + "=" * 60)
    print("TEST 3: Disponibilité des clients IA")
    print("=" * 60)
    
    test_service = get_ai_connection_test_service()
    
    for provider in AIProvider:
        requirements = test_service.get_connection_requirements(provider)
        print(f"\n🔧 {provider.value}:")
        print(f"   Client installé: {'✅' if requirements['client_available'] else '❌'}")
        print(f"   URL clé API: {requirements['api_key_url']}")
        print(f"   Commande d'installation: {requirements['install_command']}")

def test_config_integration():
    """Teste l'intégration avec le service de configuration"""
    print("\n" + "=" * 60)
    print("TEST 4: Intégration avec la configuration")
    print("=" * 60)
    
    config_service = get_ai_config_service()
    
    for provider in AIProvider:
        print(f"\n🔧 Configuration {provider.value}:")
        
        api_key = config_service.get_api_key(provider)
        model = config_service.get_model(provider)
        models_available = config_service.get_available_models(provider)
        
        print(f"   Clé API configurée: {'✅' if api_key else '❌'}")
        if api_key:
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            print(f"   Clé (masquée): {masked_key}")
        
        print(f"   Modèle configuré: {model}")
        print(f"   Modèles disponibles: {len(models_available)}")

def interactive_test():
    """Permet de tester interactivement avec de vraies clés"""
    print("\n" + "=" * 60)
    print("TEST 5: Test interactif (optionnel)")
    print("=" * 60)
    
    print("Vous pouvez maintenant tester avec vos vraies clés API.")
    print("Lancez la fenêtre de configuration pour saisir vos clés et tester.")
    
    try:
        from gui.config_window import ConfigWindow
        print("\n🚀 Ouverture de la fenêtre de configuration...")
        
        # Créer et lancer la fenêtre de configuration
        config_window = ConfigWindow()
        config_window.run()
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Assurez-vous que tous les modules sont correctement installés.")
    except Exception as e:
        print(f"❌ Erreur lors de l'ouverture de la fenêtre: {e}")

def main():
    """Point d'entrée principal"""
    setup_logging()
    
    print("🤖 Démonstration des tests de connexion IA - BGRAPP Pyconseil")
    print("================================================================")
    
    try:
        # Tests automatiques
        test_client_availability()
        test_without_api_keys()
        test_with_fake_keys()
        test_config_integration()
        
        # Test interactif
        print("\n" + "=" * 60)
        choice = input("Voulez-vous lancer l'interface graphique pour tester avec vos clés ? (y/N): ")
        if choice.lower() in ['y', 'yes', 'o', 'oui']:
            interactive_test()
        
        print("\n✅ Démonstration terminée avec succès !")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Démonstration interrompue par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ Erreur lors de la démonstration: {e}")
        logging.exception("Erreur détaillée:")

if __name__ == "__main__":
    main() 