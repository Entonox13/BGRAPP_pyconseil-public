#!/usr/bin/env python3
"""
Tests unitaires pour les modèles de données de l'application de conseil de classe.
"""

import pytest
import sys
from pathlib import Path

# Ajouter le répertoire racine au path pour les imports
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.models import Eleve, AppreciationMatiere, Bulletin, parse_heures_absence, parse_moyenne


class TestEleve:
    """Tests pour la classe Eleve."""
    
    def test_creation_eleve_basique(self):
        """Test de création d'un élève avec nom et prénom."""
        eleve = Eleve(nom="DUPONT", prenom="Alice")
        assert eleve.nom == "DUPONT"
        assert eleve.prenom == "Alice"
        assert eleve.classe is None
        
    def test_creation_eleve_avec_classe(self):
        """Test de création d'un élève avec classe."""
        eleve = Eleve(nom="MARTIN", prenom="Paul", classe="4ème A")
        assert eleve.nom == "MARTIN"
        assert eleve.prenom == "Paul"
        assert eleve.classe == "4ème A"
        
    def test_from_full_name_simple(self):
        """Test de création à partir du nom complet."""
        eleve = Eleve.from_full_name("DUPONT Alice")
        assert eleve.nom == "DUPONT"
        assert eleve.prenom == "Alice"
        
    def test_from_full_name_nom_compose(self):
        """Test avec nom composé."""
        eleve = Eleve.from_full_name("MARTIN-DUPONT Jean-Pierre")
        assert eleve.nom == "MARTIN-DUPONT"
        assert eleve.prenom == "Jean-Pierre"
        
    def test_from_full_name_erreur(self):
        """Test d'erreur avec format invalide."""
        with pytest.raises(ValueError):
            Eleve.from_full_name("Alice")
            
    def test_str_representation(self):
        """Test de la représentation en chaîne."""
        eleve = Eleve(nom="DUPONT", prenom="Alice")
        assert str(eleve) == "DUPONT Alice"


class TestAppreciationMatiere:
    """Tests pour la classe AppreciationMatiere."""
    
    def test_creation_appreciation_basique(self):
        """Test de création d'une appréciation basique."""
        appreciation = AppreciationMatiere(matiere="Mathematiques")
        assert appreciation.matiere == "Mathematiques"
        assert appreciation.moyenne_s1 is None
        assert appreciation.moyenne_s2 is None
        
    def test_creation_appreciation_complete(self):
        """Test de création d'une appréciation complète."""
        appreciation = AppreciationMatiere(
            matiere="Francais",
            moyenne_s1=14.5,
            moyenne_s2=15.0,
            appreciation_s1="Bon travail",
            appreciation_s2="Très bien"
        )
        assert appreciation.matiere == "Francais"
        assert appreciation.moyenne_s1 == 14.5
        assert appreciation.moyenne_s2 == 15.0
        assert appreciation.appreciation_s1 == "Bon travail"
        assert appreciation.appreciation_s2 == "Très bien"
        
    def test_to_dict(self):
        """Test de conversion en dictionnaire."""
        appreciation = AppreciationMatiere(
            matiere="Histoire",
            moyenne_s1=12.0,
            heures_absence_s2=2,
            appreciation_s1="Correct"
        )
        result = appreciation.to_dict()
        
        assert "MoyenneS1" in result
        assert result["MoyenneS1"] == 12.0
        assert "HeuresAbsenceS2" in result
        assert result["HeuresAbsenceS2"] == 2
        assert "AppreciationS1" in result
        assert result["AppreciationS1"] == "Correct"
        
        # Les valeurs None ne doivent pas être présentes
        assert "MoyenneS2" not in result


class TestBulletin:
    """Tests pour la classe Bulletin."""
    
    def test_creation_bulletin(self):
        """Test de création d'un bulletin."""
        eleve = Eleve(nom="DUPONT", prenom="Alice")
        bulletin = Bulletin(eleve=eleve)
        
        assert bulletin.eleve == eleve
        assert bulletin.appreciation_generale_s1 is None
        assert bulletin.appreciation_generale_s2 is None
        assert len(bulletin.matieres) == 0
        
    def test_ajout_matiere(self):
        """Test d'ajout d'une matière au bulletin."""
        eleve = Eleve(nom="DUPONT", prenom="Alice")
        bulletin = Bulletin(eleve=eleve)
        
        appreciation = AppreciationMatiere(matiere="Mathematiques", moyenne_s1=14.0)
        bulletin.add_matiere(appreciation)
        
        assert len(bulletin.matieres) == 1
        assert "Mathematiques" in bulletin.matieres
        assert bulletin.get_matiere("Mathematiques") == appreciation
        
    def test_to_dict(self):
        """Test de conversion bulletin en dictionnaire."""
        eleve = Eleve(nom="DUPONT", prenom="Alice")
        bulletin = Bulletin(
            eleve=eleve,
            appreciation_generale_s1="Bon trimestre"
        )
        
        appreciation = AppreciationMatiere(matiere="Mathematiques", moyenne_s1=14.0)
        bulletin.add_matiere(appreciation)
        
        result = bulletin.to_dict()
        
        assert result["Nom"] == "DUPONT"
        assert result["Prenom"] == "Alice"
        assert result["AppreciationGeneraleS1"] == "Bon trimestre"
        assert "Matieres" in result
        assert "Mathematiques" in result["Matieres"]
        
    def test_from_dict(self):
        """Test de création bulletin depuis dictionnaire."""
        data = {
            "Nom": "MARTIN",
            "Prenom": "Paul",
            "AppreciationGeneraleS1": "Très bien",
            "Matieres": {
                "Mathematiques": {
                    "MoyenneS1": 15.0,
                    "AppreciationS1": "Excellent"
                }
            }
        }
        
        bulletin = Bulletin.from_dict(data)
        
        assert bulletin.eleve.nom == "MARTIN"
        assert bulletin.eleve.prenom == "Paul"
        assert bulletin.appreciation_generale_s1 == "Très bien"
        assert len(bulletin.matieres) == 1
        assert bulletin.get_matiere("Mathematiques").moyenne_s1 == 15.0
        
    def test_str_representation(self):
        """Test de la représentation en chaîne."""
        eleve = Eleve(nom="DUPONT", prenom="Alice")
        bulletin = Bulletin(eleve=eleve)
        appreciation = AppreciationMatiere(matiere="Mathematiques")
        bulletin.add_matiere(appreciation)
        
        assert "DUPONT Alice" in str(bulletin)
        assert "1 matières" in str(bulletin)


class TestParseFunctions:
    """Tests pour les fonctions de parsing."""
    
    def test_parse_heures_absence(self):
        """Test de parsing des heures d'absence."""
        assert parse_heures_absence("3h00") == 3
        assert parse_heures_absence("1h30") == 1
        assert parse_heures_absence("") is None
        assert parse_heures_absence("N.Not") is None
        assert parse_heures_absence("5") == 5
        
    def test_parse_moyenne(self):
        """Test de parsing des moyennes."""
        assert parse_moyenne("14,50") == 14.5
        assert parse_moyenne("12.25") == 12.25
        assert parse_moyenne("N.Not") is None
        assert parse_moyenne("") is None
        assert parse_moyenne("16,00") == 16.0


if __name__ == "__main__":
    # Lancer les tests
    pytest.main([__file__, "-v"]) 