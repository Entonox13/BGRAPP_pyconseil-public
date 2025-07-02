#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Démonstration de la configuration du provider LOCAL
Test du LLM local via l'interface de configuration
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def demo_config_local():
    """Démonstration de la configuration LOCAL"""
    
    print("=" * 60)
    print("🦙 DÉMONSTRATION - Configuration LOCAL")
    print("=" * 60)
    
    try:
        from src.services.ai_config_service import AIProvider, get_ai_config_service
        from src.gui.config_window import ConfigWindow
        
        print("\n📊 État initial de la configuration LOCAL:")
        config_service = get_ai_config_service()
        
        # Afficher les informations LOCAL
        models = config_service.get_available_models(AIProvider.LOCAL)
        print(f"  🤖 Modèles LOCAL disponibles: {models}")
        
        default_model = config_service.get_model(AIProvider.LOCAL)
        print(f"  🎯 Modèle par défaut: {default_model}")
        
        base_url = config_service.get_base_url(AIProvider.LOCAL)
        print(f"  🌐 URL par défaut: {base_url}")
        
        # Vérifier la validation
        validation = config_service.validate_configuration()
        local_available = AIProvider.LOCAL in validation['providers_with_keys']
        print(f"  ✅ LOCAL disponible: {local_available}")
        
        print("\n💡 Instructions pour utiliser LOCAL:")
        print("  1. 🔧 Installez Ollama depuis https://ollama.ai/")
        print("  2. 📥 Téléchargez un modèle: 'ollama pull llama3.2'")
        print("  3. ▶️ Démarrez le modèle: 'ollama run llama3.2'")
        print("  4. 🌐 Vérifiez que le serveur tourne sur http://localhost:11434")
        print("  5. 🖥️ Utilisez l'interface ci-dessous pour configurer et tester")
        
        print("\n🖥️ Lancement de l'interface de configuration...")
        print("   👉 Sélectionnez l'onglet 'LLM Local'")
        print("   👉 Vérifiez l'URL du serveur")
        print("   👉 Sélectionnez le modèle")
        print("   👉 Activez le provider LOCAL")
        print("   👉 Testez la connexion")
        
        def on_config_changed():
            """Callback appelé quand la configuration change"""
            print("\n🔧 Configuration LOCAL mise à jour!")
            new_summary = config_service.get_current_config_summary()
            if new_summary['enabled_provider'] == AIProvider.LOCAL:
                print("  🎯 LOCAL est maintenant le fournisseur actif!")
        
        # Créer et lancer la fenêtre de configuration
        config_window = ConfigWindow(on_config_changed=on_config_changed)
        
        # Mettre l'onglet LOCAL en avant
        print("\n📋 Conseils pour la configuration:")
        print("  • URL Ollama standard: http://localhost:11434")
        print("  • URL LM Studio standard: http://localhost:1234")
        print("  • Pas de clé API nécessaire pour LOCAL")
        print("  • Sélectionnez le modèle que vous avez installé")
        
        config_window.run()
        
        print("\n✅ Démonstration terminée!")
        
        # Afficher l'état final
        final_summary = config_service.get_current_config_summary()
        if final_summary['enabled_provider'] == AIProvider.LOCAL:
            print("🎉 LOCAL configuré avec succès comme fournisseur actif!")
            base_url = final_summary['base_urls'].get(AIProvider.LOCAL, 'Non configuré')
            model = final_summary['models'].get(AIProvider.LOCAL, 'Non configuré')
            print(f"  🌐 URL: {base_url}")
            print(f"  🤖 Modèle: {model}")
        else:
            print("ℹ️ LOCAL n'est pas le fournisseur actif")
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Vérifiez que tous les modules sont installés")
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()


def test_local_quick():
    """Test rapide de la configuration LOCAL"""
    
    print("\n🧪 Test rapide LOCAL...")
    
    try:
        from src.services.ai_config_service import AIProvider, get_ai_config_service
        from src.services.ai_connection_test_service import get_ai_connection_test_service
        
        config_service = get_ai_config_service()
        test_service = get_ai_connection_test_service()
        
        # Configurer LOCAL
        config_service.set_base_url(AIProvider.LOCAL, "http://localhost:11434")
        config_service.set_model(AIProvider.LOCAL, "llama3.2")
        config_service.set_enabled_provider(AIProvider.LOCAL)
        
        print("  ✅ Configuration LOCAL sauvegardée")
        
        # Test de connexion
        print("  🔄 Test de connexion au serveur local...")
        result = test_service.test_connection(
            AIProvider.LOCAL,
            "http://localhost:11434",
            "llama3.2"
        )
        
        if result.success:
            print("  🎉 Connexion réussie au serveur local!")
            print(f"     Détails: {result.message}")
        else:
            print("  ⚠️ Connexion échouée (normal si serveur non démarré)")
            print(f"     Erreur: {result.message}")
        
        return result.success
        
    except Exception as e:
        print(f"  ❌ Erreur test: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Démonstration configuration LOCAL...")
    
    # Test rapide d'abord
    connection_ok = test_local_quick()
    
    if connection_ok:
        print("\n🎉 Serveur local détecté et fonctionnel!")
        print("Vous pouvez utiliser LOCAL directement.")
    else:
        print("\n⚠️ Aucun serveur local détecté.")
        print("La démonstration va vous montrer comment configurer LOCAL.")
    
    # Lancement de l'interface
    demo_config_local() 