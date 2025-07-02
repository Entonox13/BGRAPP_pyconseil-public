#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de démonstration de l'interface conseil en mode plein écran 1080p
"""

import os
import sys
import tkinter as tk
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Démonstration de l'interface conseil optimisée pour 1080p"""
    
    print("=== DÉMONSTRATION INTERFACE CONSEIL PLEIN ÉCRAN ===")
    print()
    print("🖥️  Interface optimisée pour écran 1080p")
    print("⛶   Mode plein écran automatique")
    print("📋  Appréciations avec plus d'espace")
    print("🎯  Navigation améliorée")
    print()
    
    # Vérifier si output.json existe
    output_path = "output.json"
    if not os.path.exists(output_path):
        print("❌ Fichier output.json non trouvé")
        print("   Veuillez d'abord créer le fichier JSON via main.py")
        print("   ou utilisez output_demo.json comme exemple")
        
        # Essayer avec output_demo.json
        demo_path = "output_demo.json"
        if os.path.exists(demo_path):
            output_path = demo_path
            print(f"✅ Utilisation de {demo_path} comme fichier de démonstration")
        else:
            print("❌ Aucun fichier JSON de démonstration disponible")
            return
    else:
        print(f"✅ Utilisation de {output_path}")
    
    print()
    print("🚀 Lancement de l'interface conseil plein écran...")
    print()
    print("RACCOURCIS CLAVIER :")
    print("   • Échap ou F11 : Basculer plein écran")
    print("   • Molette souris : Défiler dans les appréciations")
    print()
    print("FONCTIONNALITÉS OPTIMISÉES :")
    print("   • Zones d'appréciations matières ajustées (height=4 ≈ 3.5 lignes)")
    print("   • Zones d'appréciations générales agrandies (height=5 ≈ 4.5 lignes)")
    print("   • Affichage côte à côte S1/S2")
    print("   • Scrollbars individuelles par appréciation")
    print("   • Police agrandie (Arial 11)")
    print("   • Layout compact pour maximiser l'espace")
    print()
    
    try:
        # Import de la fenêtre conseil
        from src.gui.conseil_window import ConseilWindow
        
        # Créer et lancer la fenêtre
        window = ConseilWindow(json_file_path=output_path)
        
        print("✨ Interface lancée en mode plein écran !")
        print("   Fermez la fenêtre pour revenir au terminal.")
        
        window.run()
        
        print("👋 Démonstration terminée")
        
    except ImportError as e:
        print(f"❌ Erreur d'import : {e}")
        print("   Vérifiez que les modules sont correctement installés")
    except Exception as e:
        print(f"❌ Erreur lors du lancement : {e}")
        print("   Vérifiez les logs pour plus de détails")

if __name__ == "__main__":
    main() 