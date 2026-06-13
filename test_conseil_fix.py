#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple de la correction des boutons conseil
"""

import os
import sys

# Ajouter le chemin source si nécessaire
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_conseil_fix():
    """Test simple du fix des boutons conseil"""
    
    # Vérifier qu'un fichier JSON existe
    json_files = [f for f in os.listdir('.') if f.endswith('.json') and 'output' in f]
    
    if not json_files:
        print("❌ Aucun fichier output.json trouvé dans le répertoire")
        return
    
    json_file = json_files[0]
    print(f"📁 Utilisation du fichier: {json_file}")
    
    try:
        print("🚀 Lancement de la fenêtre conseil...")
        
        from src.gui.conseil_window import ConseilWindow
        
        # Créer la fenêtre conseil directement
        conseil = ConseilWindow(json_file_path=json_file)
        
        print("✅ Fenêtre conseil créée avec succès")
        print("🎯 Testez les boutons 'Retour' et la fermeture (X)")
        print("📝 Les messages de debug apparaîtront dans la console")
        
        # Lancer l'interface
        conseil.run()
        
        print("✅ Test terminé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conseil_fix() 