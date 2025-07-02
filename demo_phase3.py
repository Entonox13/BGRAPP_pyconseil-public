#!/usr/bin/env python3
"""
Script de démonstration de la Phase 3 - Moteur de traitement JSON
"""

from src.services.main_processor import process_directory_to_json, get_processing_summary
from src.services.json_generator import load_bulletins_from_json
import json

def demo_phase3():
    """Démonstration complète du moteur de traitement JSON."""
    
    print("🎯 DÉMONSTRATION PHASE 3 - MOTEUR DE TRAITEMENT JSON")
    print("=" * 60)
    
    # 1. Résumé du répertoire d'exemples
    print("\n1. 📋 Analyse du répertoire d'exemples:")
    summary = get_processing_summary("exemples")
    print(f"   ✅ Répertoire valide: {summary['valid_directory']}")
    print(f"   📄 Fichier source.xlsx: {summary['source_file_exists']}")
    print(f"   📊 Fichiers CSV trouvés: {summary['csv_files_count']}")
    print(f"   👥 Bulletins estimés: {summary['estimated_bulletins']}")
    print(f"   📚 Matières détectées: {', '.join(summary['csv_files'])}")
    
    # 2. Traitement complet
    print("\n2. ⚙️ Traitement complet:")
    result = process_directory_to_json("exemples", "output_demo.json")
    
    print(f"   ✅ Succès: {result['success']}")
    print(f"   👥 Bulletins générés: {result['bulletins_count']}")
    print(f"   📚 Matières traitées: {result['matieres_count']}")
    
    if result['warnings']:
        print(f"   ⚠️ Avertissements: {len(result['warnings'])}")
        for warning in result['warnings'][:3]:  # Afficher max 3 avertissements
            print(f"      - {warning}")
    
    # 3. Vérification du fichier généré
    print("\n3. 🔍 Vérification du fichier généré:")
    bulletins = load_bulletins_from_json("output_demo.json")
    print(f"   📄 Bulletins rechargés: {len(bulletins)}")
    
    # Statistiques des matières
    matieres_stats = {}
    for bulletin in bulletins:
        for matiere_name in bulletin.matieres.keys():
            if matiere_name not in matieres_stats:
                matieres_stats[matiere_name] = 0
            matieres_stats[matiere_name] += 1
    
    print(f"   📊 Matières par bulletin:")
    for matiere, count in sorted(matieres_stats.items()):
        print(f"      - {matiere}: {count} bulletins")
    
    # 4. Exemple de bulletin
    print("\n4. 📝 Exemple de bulletin (premier élève):")
    if bulletins:
        premier_bulletin = bulletins[0]
        print(f"   👤 Élève: {premier_bulletin.eleve.nom} {premier_bulletin.eleve.prenom}")
        print(f"   📚 Nombre de matières: {len(premier_bulletin.matieres)}")
        
        # Afficher une matière en détail
        if premier_bulletin.matieres:
            matiere_nom, appreciation = next(iter(premier_bulletin.matieres.items()))
            print(f"   📖 Exemple - {matiere_nom}:")
            if appreciation.moyenne_s1:
                print(f"      • Moyenne S1: {appreciation.moyenne_s1}")
            if appreciation.moyenne_s2:
                print(f"      • Moyenne S2: {appreciation.moyenne_s2}")
            if appreciation.appreciation_s2:
                print(f"      • Appréciation S2: {appreciation.appreciation_s2[:80]}...")
    
    print("\n" + "=" * 60)
    print("✅ PHASE 3 TERMINÉE AVEC SUCCÈS!")
    print(f"📄 Fichier généré: output_demo.json ({len(bulletins)} bulletins)")
    print("🎯 Prêt pour la Phase 4 - Interface graphique")

if __name__ == "__main__":
    demo_phase3() 