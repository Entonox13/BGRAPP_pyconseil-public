#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de démonstration pour tester différents modèles OpenAI
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Démonstration du changement de modèle OpenAI"""
    
    print("=== DÉMONSTRATION CHANGEMENT MODÈLE OPENAI ===")
    print()
    print("📝 Comment changer le modèle utilisé :")
    print()
    print("1️⃣ MÉTHODE 1 : Modifier la variable DEFAULT_OPENAI_MODEL")
    print("   📁 Fichier : src/services/openai_service.py")
    print("   🔧 Ligne 15 : DEFAULT_OPENAI_MODEL = \"votre-modèle\"")
    print()
    print("2️⃣ MÉTHODE 2 : Passer le modèle en paramètre")
    print("   🐍 Code : service = OpenAIService(model=\"votre-modèle\")")
    print("   🏭 Ou : service = get_openai_service(model=\"votre-modèle\")")
    print()
    
    # Vérifier si la clé API est configurée
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Clé API OpenAI non configurée")
        print("   Configurez OPENAI_API_KEY dans le fichier .env pour tester")
        print()
    
    print("🤖 MODÈLES DISPONIBLES :")
    models = [
        ("gpt-5.5", "Qualité maximale / reasoning", "🧠"),
        ("gpt-5.4", "Très bon équilibre", "🚀"),
        ("gpt-5.4-mini", "Équilibre performance/coût (défaut)", "⚖️"),
        ("gpt-5.4-nano", "Ultra rapide / budget serré", "⚡"),
    ]
    
    for model, description, emoji in models:
        print(f"   {emoji} {model:<20} - {description}")
    
    print()
    print("💡 CONSEILS D'UTILISATION :")
    print("   • gpt-5.4-mini : Modèle polyvalent recommandé par défaut")  
    print("   • gpt-5.5 : À privilégier pour les bilans les plus importants (coût supérieur)")
    print("   • gpt-5.4-nano : Parfait pour les tests rapides ou budgets serrés")
    print()
    
    # Test de connexion si possible
    if os.getenv('OPENAI_API_KEY'):
        print("🔍 TEST DE CONNEXION...")
        try:
            from src.services.openai_service import get_openai_service, DEFAULT_OPENAI_MODEL
            
            print(f"   Modèle actuellement configuré : {DEFAULT_OPENAI_MODEL}")
            
            service = get_openai_service()
            if service:
                print("   ✅ Connexion réussie avec le modèle par défaut")
                
                # Test avec un autre modèle si souhaité
                print()
                print("   🧪 Test avec gpt-5.4-mini...")
                try:
                    service_alt = get_openai_service(model="gpt-5.4-mini")
                    if service_alt:
                        print("   ✅ gpt-5.4-mini disponible")
                    else:
                        print("   ❌ gpt-5.4-mini non disponible")
                except Exception as e:
                    print(f"   ❌ Erreur avec gpt-5.4-mini : {e}")
                    
            else:
                print("   ❌ Échec de la connexion")
                
        except Exception as e:
            print(f"   ❌ Erreur lors du test : {e}")
    
    print()
    print("📖 EXEMPLE D'UTILISATION DANS LE CODE :")
    print("""
    # Dans votre code Python :
    from src.services.openai_service import get_openai_service
    
    # Utiliser le modèle par défaut
    service = get_openai_service()
    
    # Ou spécifier un modèle
    service = get_openai_service(model="gpt-5.4-mini")
    
    # Test et utilisation
    if service:
        result = service.preprocess_appreciation("Excellent travail!")
        print(result)
    """)
    
    print()
    print("🔧 Pour changer le modèle par défaut de façon permanente :")
    print("   1. Ouvrir src/services/openai_service.py")
    print("   2. Modifier la ligne 15 :")
    print('      DEFAULT_OPENAI_MODEL = "gpt-5.4-mini"  # ou votre modèle préféré')
    print("   3. Sauvegarder le fichier")
    print("   4. Le nouveau modèle sera utilisé partout dans l'application")


if __name__ == "__main__":
    main() 