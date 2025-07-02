#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Démonstration de la fenêtre de configuration IA multi-fournisseurs
Test des fonctionnalités de configuration des clés API et modèles
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.gui.config_window import ConfigWindow
from src.services.ai_config_service import AIProvider, get_ai_config_service


def demo_config_ia():
    """Démonstration de la configuration IA"""
    
    print("=" * 60)
    print("🤖 DÉMONSTRATION - Configuration IA Multi-Fournisseurs")
    print("=" * 60)
    
    # Afficher l'état initial de la configuration
    print("\n📊 État initial de la configuration:")
    config_service = get_ai_config_service()
    summary = config_service.get_current_config_summary()
    
    print(f"  🎯 Fournisseur actif: {summary['enabled_provider']}")
    print(f"  🔑 Fournisseurs avec clés: {[p.value for p in summary['providers_with_keys']]}")
    
    for provider in AIProvider:
        is_active = summary['enabled_provider'] == provider
        model = summary['models'].get(provider, "Non configuré")
        status = "🎯" if is_active else "⚪"
        print(f"  {status} {provider.value.title()}: {model}")
    
    # Validation de la configuration
    validation = summary['validation']
    print(f"\n🔍 Validation: {'✅ Valide' if validation['valid'] else '❌ Invalide'}")
    
    if validation['errors']:
        for error in validation['errors']:
            print(f"  ❌ Erreur: {error}")
    
    if validation['warnings']:
        for warning in validation['warnings']:
            print(f"  ⚠️ Avertissement: {warning}")
    
    # Afficher les modèles disponibles pour chaque fournisseur
    print("\n📚 Modèles disponibles par fournisseur:")
    for provider in AIProvider:
        models = config_service.get_available_models(provider)
        print(f"  🔹 {provider.value.title()}:")
        for i, model in enumerate(models[:3]):  # Limiter à 3 pour la démo
            print(f"    • {model}")
        if len(models) > 3:
            print(f"    • ... et {len(models) - 3} autres modèles")
    
    # Lancer l'interface graphique
    print("\n🖥️ Lancement de l'interface de configuration...")
    print("   • Configurez vos clés API")
    print("   • Sélectionnez vos modèles préférés") 
    print("   • Choisissez le fournisseur actif")
    print("   • Testez la connexion")
    print("   • Sauvegardez votre configuration")
    
    def on_config_changed():
        """Callback appelé quand la configuration change"""
        print("\n🔧 Configuration IA mise à jour!")
        
        # Afficher le nouvel état
        new_summary = config_service.get_current_config_summary()
        print(f"  🎯 Nouveau fournisseur actif: {new_summary['enabled_provider']}")
        print(f"  🔑 Fournisseurs configurés: {[p.value for p in new_summary['providers_with_keys']]}")
    
    # Créer et lancer la fenêtre de configuration
    try:
        config_window = ConfigWindow(on_config_changed=on_config_changed)
        config_window.run()
        
        print("\n✅ Démonstration terminée!")
        
        # Afficher l'état final
        final_summary = config_service.get_current_config_summary()
        print(f"\n📊 État final:")
        print(f"  🎯 Fournisseur actif: {final_summary['enabled_provider']}")
        print(f"  🔑 Fournisseurs configurés: {[p.value for p in final_summary['providers_with_keys']]}")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()


def demo_service_config():
    """Démonstration des fonctionnalités du service de configuration"""
    
    print("\n" + "=" * 60)
    print("🔧 DÉMONSTRATION - Service de configuration")
    print("=" * 60)
    
    config_service = get_ai_config_service()
    
    # Test de configuration programmatique
    print("\n🧪 Test de configuration programmatique:")
    
    # Configurer un fournisseur fictif pour la démo
    test_provider = AIProvider.OPENAI
    
    print(f"  📝 Configuration de {test_provider.value}...")
    
    # Sauvegarder l'état actuel
    original_key = config_service.get_api_key(test_provider)
    original_model = config_service.get_model(test_provider)
    
    try:
        # Test de configuration
        config_service.set_api_key(test_provider, "demo-key-123")
        available_models = config_service.get_available_models(test_provider)
        if available_models:
            config_service.set_model(test_provider, available_models[0])
        
        config_service.set_enabled_provider(test_provider)
        
        print(f"  ✅ Clé API: {'*' * 20}...")
        print(f"  ✅ Modèle: {config_service.get_model(test_provider)}")
        print(f"  ✅ Fournisseur actif: {config_service.get_enabled_provider() == test_provider}")
        
        # Validation
        validation = config_service.validate_configuration()
        print(f"  🔍 Configuration valide: {validation['valid']}")
        
    except Exception as e:
        print(f"  ❌ Erreur lors du test: {e}")
    
    finally:
        # Restaurer l'état original
        if original_key:
            config_service.set_api_key(test_provider, original_key)
        if original_model:
            config_service.set_model(test_provider, original_model)
        
        print(f"  🔄 Configuration restaurée")
    
    print("\n📋 Informations sur le fichier .env:")
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        print(f"  📁 Emplacement: {env_path}")
        print(f"  📏 Taille: {env_path.stat().st_size} octets")
        print("  📝 Contenu (masqué pour sécurité):")
        with open(env_path, 'r') as f:
            lines = f.readlines()
            for line in lines[:10]:  # Afficher les 10 premières lignes
                if 'API_KEY' in line and '=' in line:
                    key, value = line.split('=', 1)
                    masked_value = '*' * min(20, len(value.strip())) if value.strip() != 'your-' + key.lower().replace('_', '-') + '-here' else value.strip()
                    print(f"    {key}={masked_value}")
                elif line.strip() and not line.startswith('#'):
                    print(f"    {line.strip()}")
        
        if len(lines) > 10:
            print(f"    ... et {len(lines) - 10} autres lignes")
    else:
        print(f"  ❌ Fichier .env non trouvé à {env_path}")
        print("  💡 Créez le fichier .env pour configurer vos clés API")


if __name__ == "__main__":
    try:
        # Démo du service de configuration
        demo_service_config()
        
        # Démo de l'interface graphique
        demo_config_ia()
        
    except KeyboardInterrupt:
        print("\n\n👋 Démonstration interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc() 