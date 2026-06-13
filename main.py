#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BGRAPP Pyconseil - Outil d'aide à la préparation des conseils de classe
Application principale
"""

import sys
import os
from pathlib import Path

# Ajout du dossier src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """
    Point d'entrée principal de l'application
    """
    print("🎓 BGRAPP Pyconseil - Outil d'aide aux conseils de classe")
    print("=" * 55)
    print("Lancement de l'interface graphique...")
    
    try:
        # Initialiser l'interface graphique principale
        from gui.main_window import MainWindow
        app = MainWindow()
        app.run()
    except ImportError as e:
        print(f"❌ Erreur d'importation: {e}")
        print("Vérifiez que tous les modules sont présents dans le dossier src/")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        print("Environnement Python:", sys.version)
        print("Répertoire de travail:", os.getcwd())

if __name__ == "__main__":
    main() 