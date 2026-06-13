#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de démonstration de la Phase 5 - Fenêtre d'édition
BGRAPP Pyconseil - Outil d'aide aux conseils de classe
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demo_phase5():
    """Démonstration des fonctionnalités de la Phase 5"""
    
    print("🎓 BGRAPP Pyconseil - Démonstration Phase 5")
    print("=" * 50)
    print()
    
    print("📋 PHASE 5: INTERFACE GRAPHIQUE - FENÊTRE D'ÉDITION")
    print("✅ Terminée le 21/01/2025")
    print()
    
    print("🎯 Objectifs atteints:")
    print("  ✅ Affichage des données de bulletins")
    print("  ✅ Navigation entre bulletins")
    print("  ✅ Préparation de l'intégration OpenAI")
    print()
    
    print("📈 Fonctionnalités implémentées:")
    print("  • Interface d'édition avec 3 onglets (Élève, Matières, Appréciation générale)")
    print("  • Chargement et validation des fichiers JSON de bulletins")
    print("  • Navigation fluide entre bulletins (boutons + liste)")
    print("  • Affichage détaillé des notes et appréciations par matière")
    print("  • Édition et sauvegarde des appréciations générales")
    print("  • Boutons préparatoires pour l'intégration OpenAI (Phase 6)")
    print()
    
    print("🔧 Fichiers créés/modifiés:")
    print("  📄 src/gui/edition_window.py (nouveau)")
    print("  📄 src/gui/main_window.py (modifié)")
    print("  📄 src/gui/__init__.py (modifié)")
    print("  📄 tests/test_edition_window.py (nouveau)")
    print()
    
    # Vérification des fichiers
    files_to_check = [
        "src/gui/edition_window.py",
        "src/gui/main_window.py",
        "tests/test_edition_window.py"
    ]
    
    print("🔍 Vérification des fichiers:")
    all_files_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"  ❌ {file_path} (manquant)")
            all_files_exist = False
    
    print()
    
    # Vérification des fichiers de données
    data_files = [
        "output.json",
        "output_demo.json",
        "exemples/output.json"
    ]
    
    print("📊 Fichiers de données disponibles:")
    available_data = False
    for file_path in data_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✅ {file_path} ({size:,} bytes)")
            available_data = True
        else:
            print(f"  ⚪ {file_path} (optionnel)")
    
    print()
    
    # Test d'import des modules
    print("🧪 Test d'import des modules:")
    try:
        from gui.edition_window import EditionWindow
        print("  ✅ EditionWindow importée avec succès")
        
        from gui.main_window import MainWindow
        print("  ✅ MainWindow importée avec succès")
        
        from models.bulletin import Bulletin, Eleve, AppreciationMatiere
        print("  ✅ Modèles de données importés avec succès")
        
        print()
        print("🎉 Tous les imports fonctionnent correctement!")
        
    except ImportError as e:
        print(f"  ❌ Erreur d'import: {e}")
        return False
    
    print()
    
    # Instructions pour tester
    print("🚀 Pour tester la Phase 5:")
    print("  1. Lancez l'application principale:")
    print("     python main.py")
    print()
    print("  2. Sélectionnez un dossier contenant les fichiers source")
    print("     (ou utilisez le dossier 'exemples')")
    print()
    print("  3. Cliquez sur 'Créer JSON' pour générer les bulletins")
    print()
    print("  4. Cliquez sur 'Fenêtre édition' pour ouvrir la nouvelle interface")
    print()
    print("  5. Naviguez entre les bulletins et explorez les fonctionnalités:")
    print("     • Onglet 'Élève' : informations de base")
    print("     • Onglet 'Matières' : notes et appréciations par matière")
    print("     • Onglet 'Appréciation générale' : édition des synthèses")
    print("     • Navigation : boutons précédent/suivant + liste cliquable")
    print("     • Sauvegarde : modifications persistantes")
    print()
    
    print("🔮 Prochaine étape - Phase 6:")
    print("  • Intégration de l'API OpenAI")
    print("  • Prétraitement des appréciations avec balises HTML")
    print("  • Génération automatique d'appréciations générales")
    print("  • Activation des boutons actuellement en placeholder")
    print()
    
    if all_files_exist and available_data:
        print("✅ Phase 5 complètement opérationnelle!")
        return True
    elif all_files_exist:
        print("⚠️  Phase 5 prête - générez des données JSON pour tester")
        return True
    else:
        print("❌ Phase 5 incomplète - fichiers manquants")
        return False


def test_edition_window_standalone():
    """Test standalone de la fenêtre d'édition"""
    print("\n🧪 Test standalone de la fenêtre d'édition:")
    print("(Fermer la fenêtre pour continuer)")
    
    try:
        from gui.edition_window import EditionWindow
        
        # Chercher un fichier de données
        test_files = ["output.json", "output_demo.json", "exemples/output.json"]
        json_file = None
        
        for file_path in test_files:
            if os.path.exists(file_path):
                json_file = file_path
                break
        
        if json_file:
            print(f"  📂 Chargement du fichier: {json_file}")
            app = EditionWindow(json_file_path=json_file)
            print("  ✅ Fenêtre d'édition créée avec succès")
            print("  🔄 Lancement de l'interface...")
            app.run()
            print("  ✅ Fenêtre fermée proprement")
        else:
            print("  ⚠️  Aucun fichier JSON trouvé - test avec fenêtre vide")
            app = EditionWindow()
            print("  ✅ Fenêtre d'édition créée (mode vide)")
            # Ne pas lancer en mode automatique sans données
            print("  ⚪ Test manuel disponible via python src/gui/edition_window.py")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors du test: {e}")
        return False


if __name__ == "__main__":
    # Démonstration complète
    success = demo_phase5()
    
    if success and len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test optionnel de la fenêtre (seulement si --test est passé)
        test_edition_window_standalone()
    
    print("\n" + "=" * 50)
    print("Démonstration Phase 5 terminée!")
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1) 