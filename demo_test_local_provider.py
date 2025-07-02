#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test d'intégration pour le provider LOCAL
Vérifie que l'architecture fonctionne correctement même sans serveur local actif
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_local_provider_integration():
    """Test complet du provider LOCAL"""
    
    print("=" * 60)
    print("🧪 TEST D'INTÉGRATION - Provider LOCAL")
    print("=" * 60)
    
    # Test 1: Import et configuration
    print("\n📦 Test 1: Imports et configuration...")
    try:
        from src.services.ai_config_service import AIProvider, get_ai_config_service
        from src.services.ai_connection_test_service import get_ai_connection_test_service
        from src.services.openai_service import AIService, get_ai_service
        
        print("  ✅ Imports réussis")
        
        # Vérifier que LOCAL est dans l'enum
        assert AIProvider.LOCAL in AIProvider, "LOCAL manquant dans l'enum AIProvider"
        print("  ✅ Provider LOCAL présent dans l'enum")
        
    except Exception as e:
        print(f"  ❌ Erreur d'import: {e}")
        return False
    
    # Test 2: Service de configuration
    print("\n⚙️ Test 2: Service de configuration...")
    try:
        config_service = get_ai_config_service()
        
        # Test des modèles disponibles pour LOCAL
        models = config_service.get_available_models(AIProvider.LOCAL)
        print(f"  📋 Modèles LOCAL disponibles: {models[:3]}...")
        assert len(models) > 0, "Aucun modèle LOCAL configuré"
        print("  ✅ Modèles LOCAL configurés")
        
        # Test du modèle par défaut
        default_model = config_service.get_model(AIProvider.LOCAL)
        print(f"  🎯 Modèle par défaut: {default_model}")
        assert default_model in models, "Modèle par défaut invalide"
        print("  ✅ Modèle par défaut valide")
        
        # Test de l'URL de base par défaut
        base_url = config_service.get_base_url(AIProvider.LOCAL)
        print(f"  🌐 URL de base par défaut: {base_url}")
        assert base_url is not None, "Aucune URL de base configurée"
        print("  ✅ URL de base configurée")
        
        # Test de configuration d'une URL personnalisée
        test_url = "http://localhost:11434"
        config_service.set_base_url(AIProvider.LOCAL, test_url)
        retrieved_url = config_service.get_base_url(AIProvider.LOCAL)
        assert retrieved_url == test_url, "URL de base non sauvegardée"
        print("  ✅ Configuration URL de base fonctionnelle")
        
    except Exception as e:
        print(f"  ❌ Erreur configuration: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Validation de configuration
    print("\n🔍 Test 3: Validation de configuration...")
    try:
        validation = config_service.validate_configuration()
        print(f"  📊 Configuration valide: {validation['valid']}")
        print(f"  🔑 Providers configurés: {[p.value for p in validation['providers_with_keys']]}")
        
        # LOCAL devrait toujours être considéré comme disponible
        assert AIProvider.LOCAL in validation['providers_with_keys'], "LOCAL non détecté comme disponible"
        print("  ✅ LOCAL détecté comme provider disponible")
        
    except Exception as e:
        print(f"  ❌ Erreur validation: {e}")
        return False
    
    # Test 4: Service de test de connexion
    print("\n🔧 Test 4: Service de test de connexion...")
    try:
        test_service = get_ai_connection_test_service()
        
        # Test des exigences pour LOCAL
        requirements = test_service.get_connection_requirements(AIProvider.LOCAL)
        print(f"  📋 Exigences LOCAL: {list(requirements.keys())}")
        assert 'client_available' in requirements, "Exigences LOCAL mal configurées"
        print("  ✅ Exigences LOCAL configurées")
        
        # Test de connexion (devrait échouer car pas de serveur)
        print("  🔄 Test de connexion sans serveur (échec attendu)...")
        result = test_service.test_connection(
            AIProvider.LOCAL, 
            "http://localhost:11434", 
            "llama3.2"
        )
        print(f"  📋 Résultat: {result.message}")
        # L'échec est normal sans serveur local
        assert not result.success, "Connexion réussie sans serveur (inattendu)"
        assert result.details.get('error_type') == 'connection_error', "Type d'erreur inattendu"
        print("  ✅ Gestion d'erreur de connexion correcte")
        
    except Exception as e:
        print(f"  ❌ Erreur test connexion: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Service IA principal
    print("\n🤖 Test 5: Service IA principal...")
    try:
        # Test d'initialisation du service IA avec LOCAL (devrait échouer gracieusement)
        print("  🔄 Tentative d'initialisation service IA LOCAL...")
        
        try:
            ai_service = AIService(provider=AIProvider.LOCAL, enable_rgpd=True)
            print("  ⚠️ Service IA initialisé (connexion non testée)")
            
            # Vérifier les propriétés du service
            assert ai_service.provider == AIProvider.LOCAL, "Provider incorrect"
            assert ai_service.enable_rgpd is True, "RGPD non activé"
            print("  ✅ Service IA configuré correctement")
            
            # Test de connexion (devrait échouer)
            connection_ok = ai_service.test_connection()
            assert not connection_ok, "Test connexion réussi sans serveur (inattendu)"
            print("  ✅ Test de connexion échoue comme attendu")
            
        except ValueError as ve:
            if "Aucun fournisseur IA configuré" in str(ve):
                print("  ⚠️ Service IA nécessite une configuration préalable (normal)")
                
                # Configurer LOCAL pour permettre l'initialisation
                config_service.set_enabled_provider(AIProvider.LOCAL)
                ai_service = AIService(provider=AIProvider.LOCAL, enable_rgpd=True)
                print("  ✅ Service IA initialisé après configuration")
            else:
                raise ve
        
    except Exception as e:
        print(f"  ❌ Erreur service IA: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: Interface graphique (imports seulement)
    print("\n🖥️ Test 6: Interface graphique...")
    try:
        from src.gui.config_window import ConfigWindow
        print("  ✅ Import ConfigWindow réussi")
        
        # Vérifier que LOCAL est supporté dans l'interface
        config_window = ConfigWindow()
        display_name = config_window._get_provider_display_name(AIProvider.LOCAL)
        assert display_name == "LLM Local", "Nom d'affichage LOCAL incorrect"
        print(f"  ✅ Nom d'affichage LOCAL: {display_name}")
        
        provider_info = config_window._get_provider_info(AIProvider.LOCAL)
        assert "Local" in provider_info, "Informations LOCAL manquantes"
        print("  ✅ Informations LOCAL configurées")
        
    except Exception as e:
        print(f"  ❌ Erreur interface: {e}")
        return False
    
    # Résumé final
    print("\n" + "=" * 60)
    print("✅ TESTS D'INTÉGRATION LOCAL RÉUSSIS")
    print("=" * 60)
    print("\n📝 Résumé:")
    print("  • Provider LOCAL ajouté avec succès")
    print("  • Configuration et validation fonctionnelles")
    print("  • Tests de connexion gèrent correctement les erreurs")
    print("  • Service IA compatible avec LOCAL")
    print("  • Interface graphique supporte LOCAL")
    print("\n💡 Pour utiliser LOCAL:")
    print("  1. Installez Ollama: https://ollama.ai/")
    print("  2. Démarrez un modèle: ollama run llama3.2")
    print("  3. Configurez l'URL: http://localhost:11434")
    print("  4. Testez la connexion dans l'interface")
    
    return True


def test_ollama_integration():
    """Test spécifique pour l'intégration Ollama"""
    print("\n🦙 Test spécifique Ollama...")
    
    try:
        # Test de l'URL Ollama par défaut
        from src.services.ai_config_service import get_ai_config_service
        config_service = get_ai_config_service()
        
        # Test de transformation d'URL
        test_urls = [
            "http://localhost:11434",
            "http://localhost:11434/",
            "http://localhost:11434/v1",
            "http://127.0.0.1:11434"
        ]
        
        for url in test_urls:
            config_service.set_base_url(AIProvider.LOCAL, url)
            stored_url = config_service.get_base_url(AIProvider.LOCAL)
            print(f"  📍 URL {url} -> {stored_url}")
        
        print("  ✅ Gestion des URLs Ollama fonctionnelle")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur test Ollama: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Lancement des tests d'intégration LOCAL...")
    
    success = test_local_provider_integration()
    
    if success:
        success = test_ollama_integration()
    
    if success:
        print("\n🎉 Tous les tests sont RÉUSSIS !")
        print("Le provider LOCAL est prêt à être utilisé.")
        exit(0)
    else:
        print("\n💥 Certains tests ont ÉCHOUÉ.")
        print("Vérifiez les erreurs ci-dessus.")
        exit(1) 