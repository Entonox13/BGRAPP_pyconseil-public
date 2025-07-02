#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Démonstration de l'affichage HTML dans la fenêtre conseil
Application BGRAPP Pyconseil
"""

import os
import sys
import json
from pathlib import Path

# Ajouter le chemin src au path Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.bulletin import Bulletin, Eleve, AppreciationMatiere
from gui.conseil_window import ConseilWindow


def create_test_data_with_html():
    """Créer des données de test avec balises HTML"""
    
    # Créer des bulletins avec appréciations HTML
    bulletins = []
    
    # Élève 1 - Bon élève
    eleve1 = Eleve(nom="MARTIN", prenom="Alice", classe="3A")
    bulletin1 = Bulletin(
        eleve=eleve1,
        appreciation_generale_s1="Élève <span class=\"positif\">sérieuse et appliquée</span>.",
        appreciation_generale_s2="<span class=\"positif\">Excellent travail</span> cette année, <span class=\"positif\">félicitations</span> !"
    )
    
    # Mathématiques
    math_appr = AppreciationMatiere(
        matiere="Mathématiques",
        moyenne_s1=15.5,
        moyenne_s2=16.2,
        heures_absence_s1=0,
        heures_absence_s2=2,
        appreciation_s1="Élève <span class=\"positif\">très douée</span> en mathématiques.",
        appreciation_s2="<span class=\"positif\">Excellent niveau</span>, continue ainsi !"
    )
    bulletin1.add_matiere(math_appr)
    
    # Français
    francais_appr = AppreciationMatiere(
        matiere="Français",
        moyenne_s1=14.0,
        moyenne_s2=15.5,
        heures_absence_s1=1,
        heures_absence_s2=0,
        appreciation_s1="Bon travail mais <span class=\"negatif\">quelques difficultés en expression écrite</span>.",
        appreciation_s2="<span class=\"positif\">Nette amélioration</span> depuis le premier semestre."
    )
    bulletin1.add_matiere(francais_appr)
    
    bulletins.append(bulletin1)
    
    # Élève 2 - Élève en difficulté
    eleve2 = Eleve(nom="DUPONT", prenom="Paul", classe="3A")
    bulletin2 = Bulletin(
        eleve=eleve2,
        appreciation_generale_s1="Élève qui <span class=\"negatif\">rencontre des difficultés</span> mais <span class=\"positif\">fait des efforts</span>.",
        appreciation_generale_s2="<span class=\"positif\">Progrès encourageants</span> malgré quelques <span class=\"negatif\">lacunes persistantes</span>."
    )
    
    # Mathématiques
    math_appr2 = AppreciationMatiere(
        matiere="Mathématiques",
        moyenne_s1=8.5,
        moyenne_s2=10.2,
        heures_absence_s1=5,
        heures_absence_s2=3,
        appreciation_s1="<span class=\"negatif\">Grandes difficultés</span> en mathématiques, <span class=\"negatif\">trop d'absences</span>.",
        appreciation_s2="<span class=\"positif\">Amélioration notable</span> grâce aux efforts fournis."
    )
    bulletin2.add_matiere(math_appr2)
    
    # Français
    francais_appr2 = AppreciationMatiere(
        matiere="Français",
        moyenne_s1=11.0,
        moyenne_s2=12.5,
        heures_absence_s1=2,
        heures_absence_s2=1,
        appreciation_s1="Travail <span class=\"positif\">régulier</span> mais <span class=\"negatif\">manque de méthode</span>.",
        appreciation_s2="<span class=\"positif\">Bonne progression</span> cette année."
    )
    bulletin2.add_matiere(francais_appr2)
    
    bulletins.append(bulletin2)
    
    return bulletins


def save_test_data(bulletins, filename="output_html_demo.json"):
    """Sauvegarder les données de test au format JSON"""
    json_data = []
    for bulletin in bulletins:
        json_data.append(bulletin.to_dict())
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    return filename


def main():
    """Démonstration de l'affichage HTML dans la fenêtre conseil"""
    print("🎨 Démonstration affichage HTML - Fenêtre Conseil")
    print("=" * 55)
    
    # Créer les données de test avec HTML
    print("📝 Création des données de test avec balises HTML...")
    bulletins = create_test_data_with_html()
    
    # Sauvegarder en JSON
    print("💾 Sauvegarde des données de test...")
    json_file = save_test_data(bulletins)
    print(f"✅ Fichier créé: {json_file}")
    print(f"📊 Taille: {os.path.getsize(json_file) / 1024:.1f} KB")
    
    print("\n🚀 Lancement de la fenêtre conseil...")
    print("🎨 Fonctionnalités HTML disponibles:")
    print("   • Balises <span class=\"positif\"> en vert et gras")
    print("   • Balises <span class=\"negatif\"> en rouge et gras")
    print("   • Affichage dans la vue détaillée ET les appréciations générales")
    print("   • Support dans toutes les appréciations (S1 et S2)")
    
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