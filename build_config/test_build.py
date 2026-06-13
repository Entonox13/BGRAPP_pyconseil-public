#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier la configuration avant le build
Vérifie que tous les modules nécessaires peuvent être importés
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier src au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

def test_imports():
    """Teste l'importation de tous les modules principaux"""
    print("🧪 Test des imports pour la configuration de build...")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Tests des modules Python standard
    standard_modules = [
        ("tkinter", "Interface graphique Tkinter"),
        ("tkinter.ttk", "Widgets TTK"),
        ("tkinter.filedialog", "Dialogues de fichiers"),
        ("tkinter.messagebox", "Boîtes de message"),
        ("json", "Manipulation JSON"),
        ("pathlib", "Gestion des chemins"),
        ("threading", "Threading"),
        ("queue", "Files d'attente"),
    ]
    
    for module, description in standard_modules:
        tests_total += 1
        try:
            __import__(module)
            print(f"✅ {module:<25} - {description}")
            tests_passed += 1
        except ImportError as e:
            print(f"❌ {module:<25} - ERREUR: {e}")
    
    # Tests des modules IA
    print("\n📡 Modules IA:")
    ai_modules = [
        ("openai", "Client OpenAI"),
        ("anthropic", "Client Anthropic"),
        ("google.genai", "Client Google Gemini"),
    ]
    
    for module, description in ai_modules:
        tests_total += 1
        try:
            __import__(module)
            print(f"✅ {module:<25} - {description}")
            tests_passed += 1
        except ImportError as e:
            print(f"⚠️  {module:<25} - Optionnel: {e}")
    
    # Tests des modules du projet
    print("\n🏠 Modules du projet:")
    project_modules = [
        ("gui.main_window", "Fenêtre principale"),
        ("gui.config_window", "Fenêtre de configuration"),
        ("services.main_processor", "Processeur principal"),
        ("services.ai_config_service", "Service configuration IA"),
        ("models.bulletin", "Modèle bulletin"),
    ]
    
    for module, description in project_modules:
        tests_total += 1
        try:
            __import__(module)
            print(f"✅ {module:<25} - {description}")
            tests_passed += 1
        except ImportError as e:
            print(f"❌ {module:<25} - ERREUR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Résultat: {tests_passed}/{tests_total} modules importés avec succès")
    
    if tests_passed == tests_total:
        print("🎉 Tous les tests réussis ! Le build devrait fonctionner.")
        return True
    else:
        print("⚠️  Certains modules manquent. Vérifiez les dépendances.")
        return False

def check_main_entry():
    """Vérifie que le point d'entrée principal fonctionne"""
    print("\n🚪 Test du point d'entrée principal...")
    
    try:
        main_file = project_root / "main.py"
        if not main_file.exists():
            print(f"❌ Fichier main.py introuvable: {main_file}")
            return False
        
        print(f"✅ Fichier main.py trouvé: {main_file}")
        
        # Test d'importation du module principal
        sys.path.insert(0, str(project_root))
        spec = __import__("main")
        print("✅ Module main.py importable")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test du point d'entrée: {e}")
        return False

def check_build_files():
    """Vérifie que tous les fichiers de build sont présents"""
    print("\n📁 Vérification des fichiers de build...")
    
    required_files = [
        "requirements_build.txt",
        "pyconseil.spec",
        "build_windows.bat",
        "build_linux.sh",
        "README_BUILD.md"
    ]
    
    all_present = True
    build_dir = Path(__file__).parent
    
    for filename in required_files:
        file_path = build_dir / filename
        if file_path.exists():
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename} - MANQUANT")
            all_present = False
    
    return all_present

def main():
    """Fonction principale de test"""
    print("🔧 BGRAPP Pyconseil - Test de Configuration Build")
    print("=" * 60)
    
    # Tests
    imports_ok = test_imports()
    entry_ok = check_main_entry()
    files_ok = check_build_files()
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ FINAL:")
    print(f"   🔗 Imports des modules: {'✅ OK' if imports_ok else '❌ ERREUR'}")
    print(f"   🚪 Point d'entrée:     {'✅ OK' if entry_ok else '❌ ERREUR'}")
    print(f"   📁 Fichiers de build:  {'✅ OK' if files_ok else '❌ ERREUR'}")
    
    if imports_ok and entry_ok and files_ok:
        print("\n🎯 Configuration prête pour le build !")
        print("   Vous pouvez maintenant exécuter:")
        print("   - Windows: build_windows.bat")
        print("   - Linux:   ./build_linux.sh")
    else:
        print("\n⚠️  Configuration incomplète. Résolvez les erreurs ci-dessus avant le build.")
    
    return imports_ok and entry_ok and files_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 