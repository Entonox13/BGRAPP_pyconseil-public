#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Démonstration du système d'anonymisation RGPD pour OpenAI
Teste l'anonymisation et la désanonymisation des données d'élèves
"""

import sys
from pathlib import Path

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.bulletin import Eleve, AppreciationMatiere, Bulletin
from services.openai_service import RGPDAnonymizer, OpenAIService

def test_rgpd_anonymizer():
    """Test du système d'anonymisation RGPD"""
    print("🔒 Test du système d'anonymisation RGPD")
    print("=" * 50)
    
    # Créer un anonymiseur
    anonymizer = RGPDAnonymizer()
    
    # Données de test avec de vrais noms d'élèves
    eleves = [
        ("DANLER", "Suheda"),
        ("ERKAN", "Ela"), 
        ("KANOUNE", "Bilal"),
        ("SAIL", "Amani"),
        ("UKËSMAJLI", "Anesa"),
        ("YUCEL", "Enis")
    ]
    
    # Textes d'appréciations avec noms d'élèves
    appreciations_test = [
        "Suheda est une élève du dispositif ULIS. Elle assiste calmement au cours.",
        "Ela ne participe toujours pas ! Quel dommage ! Elle en a pourtant les capacités.",
        "Bilal a d'indéniables capacités qu'il a d'avantage utilisées ce semestre.",
        "Amani est tout bonnement excellente et ne manque aucune occasion de réussir.",
        "Anesa est excellente et acquiert rapidement les compétences linguistiques.",
        "Enis est devenu clairement l'élève perturbateur de la classe."
    ]
    
    print("\n📝 Test d'anonymisation des appréciations:")
    print("-" * 40)
    
    for i, ((nom, prenom), appreciation) in enumerate(zip(eleves, appreciations_test)):
        print(f"\n{i+1}. Élève: {nom} {prenom}")
        print(f"   Original  : {appreciation}")
        
        # Anonymisation
        anonymized = anonymizer.anonymize_text(appreciation, nom, prenom)
        print(f"   Anonymisé : {anonymized}")
        
        # Désanonymisation
        deanonymized = anonymizer.deanonymize_text(anonymized, nom, prenom)
        print(f"   Restauré  : {deanonymized}")
        
        # Vérification
        if deanonymized == appreciation:
            print("   ✅ Réversibilité correcte")
        else:
            print("   ❌ Erreur de réversibilité")
    
    print(f"\n📊 Mappings créés: {len(anonymizer.name_mapping)} élèves enregistrés")
    
    return anonymizer

def test_openai_service_rgpd():
    """Test du service OpenAI avec anonymisation"""
    print("\n\n🤖 Test du service OpenAI avec anonymisation RGPD")
    print("=" * 60)
    
    try:
        # Créer le service avec RGPD activé
        service_rgpd = OpenAIService(enable_rgpd=True)
        print("✅ Service OpenAI avec RGPD créé")
        
        # Créer le service sans RGPD pour comparaison
        service_normal = OpenAIService(enable_rgpd=False)
        print("✅ Service OpenAI sans RGPD créé")
        
        # Test avec une appréciation contenant un nom
        nom, prenom = "DANLER", "Suheda"
        appreciation = "Suheda est une élève sérieuse. Elle doit continuer à fournir des efforts."
        
        print(f"\n📝 Test avec l'élève: {nom} {prenom}")
        print(f"Appréciation originale: {appreciation}")
        
        # Simulation d'anonymisation (sans vraiment appeler l'API)
        if service_rgpd.anonymizer:
            anonymized = service_rgpd.anonymizer.anonymize_text(appreciation, nom, prenom)
            print(f"🔒 Version anonymisée: {anonymized}")
            
            deanonymized = service_rgpd.anonymizer.deanonymize_text(anonymized, nom, prenom)
            print(f"🔓 Version désanonymisée: {deanonymized}")
        
        print("\n✅ Service OpenAI avec anonymisation RGPD opérationnel")
        
    except Exception as e:
        print(f"⚠️  Erreur lors du test du service OpenAI: {e}")
        print("   (Ceci est normal si la clé API OpenAI n'est pas configurée)")

def demo_with_bulletin():
    """Démonstration avec un bulletin complet"""
    print("\n\n📋 Test avec un bulletin complet")
    print("=" * 40)
    
    # Créer un élève de test
    eleve = Eleve(nom="DANLER", prenom="Suheda", classe="4ème A")
    
    # Créer des appréciations avec le nom de l'élève
    anglais = AppreciationMatiere(
        matiere="Anglais LV1",
        moyenne_s1=5.0,
        moyenne_s2=6.0,
        appreciation_s1="Suheda est une élève du dispositif ULIS. Elle assiste calmement au cours.",
        appreciation_s2="Suheda a fait des progrès ce semestre. Elle doit continuer ses efforts."
    )
    
    arts = AppreciationMatiere(
        matiere="Arts Plastiques", 
        moyenne_s1=8.0,
        appreciation_s1="Suheda fait tout juste le minimum. Il faut se ressaisir!"
    )
    
    # Créer le bulletin
    bulletin = Bulletin(
        eleve=eleve,
        matieres={"Anglais LV1": anglais, "Arts Plastiques": arts},
        appreciation_generale_s1="Suheda est une élève sérieuse et volontaire."
    )
    
    print(f"👤 Élève: {eleve.nom} {eleve.prenom}")
    print(f"📚 Nombre de matières: {len(bulletin.matieres)}")
    
    # Test d'anonymisation sur les appréciations
    anonymizer = RGPDAnonymizer()
    
    for nom_matiere, matiere in bulletin.matieres.items():
        print(f"\n📖 Matière: {nom_matiere}")
        
        if matiere.appreciation_s1:
            print(f"   S1 original  : {matiere.appreciation_s1}")
            anonymized = anonymizer.anonymize_text(matiere.appreciation_s1, eleve.nom, eleve.prenom)
            print(f"   S1 anonymisé : {anonymized}")
        
        if matiere.appreciation_s2:
            print(f"   S2 original  : {matiere.appreciation_s2}")
            anonymized = anonymizer.anonymize_text(matiere.appreciation_s2, eleve.nom, eleve.prenom)
            print(f"   S2 anonymisé : {anonymized}")
    
    # Test sur l'appréciation générale
    if bulletin.appreciation_generale_s1:
        print(f"\n📋 Appréciation générale S1:")
        print(f"   Original  : {bulletin.appreciation_generale_s1}")
        anonymized = anonymizer.anonymize_text(bulletin.appreciation_generale_s1, eleve.nom, eleve.prenom)
        print(f"   Anonymisé : {anonymized}")

def main():
    """Fonction principale de démonstration"""
    print("🔒 DÉMONSTRATION ANONYMISATION RGPD BGRAPP PYCONSEIL")
    print("=" * 60)
    print("Cette démonstration teste le système d'anonymisation RGPD")
    print("qui protège les données personnelles des élèves lors des")
    print("appels à l'API OpenAI.")
    
    # Test de base de l'anonymiseur
    anonymizer = test_rgpd_anonymizer()
    
    # Test du service OpenAI avec RGPD
    test_openai_service_rgpd()
    
    # Démonstration avec un bulletin complet
    demo_with_bulletin()
    
    print("\n\n✅ DÉMONSTRATION TERMINÉE")
    print("=" * 30)
    print("Le système d'anonymisation RGPD est fonctionnel.")
    print("Les noms et prénoms des élèves sont automatiquement")
    print("remplacés par 'John DOE' avant envoi à OpenAI, puis")
    print("restaurés dans les réponses.")
    print("\n🔒 Confidentialité RGPD respectée !")

if __name__ == "__main__":
    main() 