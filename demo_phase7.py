#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Démonstration de la Phase 7 - Fenêtre Conseil
Application BGRAPP Pyconseil
"""

import os
import sys
from pathlib import Path

# Ajouter le chemin src au path Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from gui.conseil_window import ConseilWindow


def main():
    """Démonstration de la fenêtre conseil"""
    print("🎯 Démonstration Phase 7 - Fenêtre Conseil")
    print("=" * 50)
    
    # Vérifier la présence du fichier JSON
    json_file = "output.json"
    if os.path.exists(json_file):
        print(f"✅ Fichier JSON trouvé: {json_file}")
        print(f"📊 Taille: {os.path.getsize(json_file) / 1024:.1f} KB")
    else:
        print(f"❌ Fichier JSON non trouvé: {json_file}")
        print("💡 Lancez d'abord la fenêtre principale pour générer le fichier JSON.")
        return
    
    print("\n🚀 Lancement de la fenêtre conseil...")
    print("📋 Fonctionnalités disponibles:")
    print("   • Navigation entre les bulletins")
    print("   • Vue synthèse avec moyennes et évolution")
    print("   • Vue détaillée par matière")
    print("   • Affichage des appréciations générales")
    print("   • Placeholders pour export et impression")
    
    try:
        # Créer et lancer la fenêtre conseil
        conseil_window = ConseilWindow(json_file_path=json_file)
        conseil_window.run()
        
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 