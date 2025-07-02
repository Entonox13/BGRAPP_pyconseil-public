#!/usr/bin/env python3
"""
Tests unitaires pour le moteur de traitement JSON.
"""

import pytest
import os
import tempfile
import shutil
import json
from pathlib import Path

# Import des modules à tester
from src.services.file_reader import (
    read_source_xlsx, read_csv_matiere, get_csv_files_in_directory,
    extract_matiere_name_from_filename, validate_source_directory,
    FileReaderError
)
from src.services.bulletin_processor import (
    create_bulletins_from_source, populate_bulletins_from_csv,
    calculate_min_max_moyennes, validate_bulletins_consistency,
    parse_rappel_s1, BulletinProcessorError
)
from src.services.json_generator import (
    bulletins_to_json, save_output_json, load_bulletins_from_json,
    get_all_matieres, JsonGeneratorError
)
from src.services.main_processor import (
    process_directory_to_json, get_processing_summary,
    MainProcessorError
)
from src.models.bulletin import Eleve, AppreciationMatiere, Bulletin


class TestFileReader:
    """Tests pour le module file_reader."""
    
    def test_validate_source_directory_with_exemples(self):
        """Test la validation du répertoire d'exemples."""
        validation = validate_source_directory("exemples")
        
        assert validation['valid'] == True
        assert validation['source_xlsx'] is not None
        assert len(validation['csv_files']) >= 3
        assert validation['errors'] == []
    
    def test_read_source_xlsx_exemples(self):
        """Test la lecture du fichier source.xlsx d'exemple."""
        eleves_data = read_source_xlsx("exemples/source.xlsx")
        
        assert len(eleves_data) > 0
        assert 'Élève' in eleves_data[0]
        
        # Vérifier qu'on a bien des noms d'élèves
        noms_eleves = [e['Élève'] for e in eleves_data if e.get('Élève')]
        assert len(noms_eleves) > 0
    
    def test_read_csv_matiere_exemples(self):
        """Test la lecture d'un fichier CSV de matière."""
        matiere_data = read_csv_matiere("exemples/mathematiques.csv", "Mathematiques")
        
        assert len(matiere_data) > 0
        assert 'Élève' in matiere_data[0]
        assert 'matiere' in matiere_data[0]
        assert matiere_data[0]['matiere'] == "Mathematiques"
    
    def test_get_csv_files_in_directory(self):
        """Test la recherche de fichiers CSV."""
        csv_files = get_csv_files_in_directory("exemples")
        
        assert len(csv_files) >= 3
        assert all(f.endswith('.csv') for f in csv_files)
    
    def test_extract_matiere_name_from_filename(self):
        """Test l'extraction du nom de matière."""
        assert extract_matiere_name_from_filename("exemples/mathematiques.csv") == "mathematiques"
        assert extract_matiere_name_from_filename("/path/to/francais.csv") == "francais"
    
    def test_file_reader_errors(self):
        """Test les erreurs de lecture de fichiers."""
        with pytest.raises(FileReaderError):
            read_source_xlsx("fichier_inexistant.xlsx")
        
        with pytest.raises(FileReaderError):
            read_csv_matiere("fichier_inexistant.csv", "Test")


class TestBulletinProcessor:
    """Tests pour le module bulletin_processor."""
    
    def test_create_bulletins_from_source(self):
        """Test la création de bulletins depuis les données source."""
        eleves_data = [
            {'Élève': 'DUPONT Alice'},
            {'Élève': 'MARTIN Jean-Paul'},
            {'Élève': 'BERNARD Marie'}
        ]
        
        bulletins = create_bulletins_from_source(eleves_data)
        
        assert len(bulletins) == 3
        assert bulletins[0].eleve.nom == "DUPONT"
        assert bulletins[0].eleve.prenom == "Alice"
        assert bulletins[1].eleve.nom == "MARTIN"
        assert bulletins[1].eleve.prenom == "Jean-Paul"
    
    def test_parse_rappel_s1(self):
        """Test le parsing de la colonne rappel S1."""
        rappel = "Moy. : 16,50 - H.Abs : 1h00 - Très bon travail ce trimestre."
        
        moyenne, heures, appreciation = parse_rappel_s1(rappel)
        
        assert moyenne == 16.5
        assert heures == 1
        assert "Très bon travail" in appreciation
    
    def test_parse_rappel_s1_variations(self):
        """Test les variations du format rappel S1."""
        # Avec heures d'absence
        moy, abs, app = parse_rappel_s1("Moy. : 12,00 - H.Abs : 2h30 - Bien.")
        assert moy == 12.0
        assert abs == 2  # Parser retourne les heures entières
        
        # Sans heures d'absence
        moy, abs, app = parse_rappel_s1("Moy. : 15,25 - Excellent travail.")
        assert moy == 15.25
        assert abs is None
        assert "Excellent" in app
    
    def test_populate_bulletins_from_csv(self):
        """Test l'ajout d'appréciations depuis un CSV."""
        # Créer des bulletins de base
        eleves_data = [{'Élève': 'ARAZAD Nada'}, {'Élève': 'BINOT Maureen'}]
        bulletins = create_bulletins_from_source(eleves_data)
        
        # Lire des données de matière réelles
        matiere_data = read_csv_matiere("exemples/mathematiques.csv", "Mathematiques")
        
        # Ajouter les appréciations
        populate_bulletins_from_csv(bulletins, matiere_data, "Mathematiques")
        
        # Vérifier qu'au moins un bulletin a des données de maths
        nada_bulletin = next((b for b in bulletins if b.eleve.prenom == "Nada"), None)
        assert nada_bulletin is not None
        
        maths_appreciation = nada_bulletin.get_matiere("Mathematiques")
        assert maths_appreciation is not None
        assert maths_appreciation.moyenne_s2 is not None
    
    def test_calculate_min_max_moyennes(self):
        """Test le calcul des moyennes min/max."""
        # Créer des bulletins avec des moyennes variées
        bulletins = []
        for i, (nom, moyennes) in enumerate([
            ("ELEVE1", (12.0, 14.0)),
            ("ELEVE2", (16.0, 11.0)),
            ("ELEVE3", (8.0, 18.0))
        ]):
            eleve = Eleve(nom=nom, prenom=f"Prenom{i}")
            bulletin = Bulletin(eleve=eleve)
            
            appreciation = AppreciationMatiere(
                matiere="Test",
                moyenne_s1=moyennes[0],
                moyenne_s2=moyennes[1]
            )
            bulletin.add_matiere(appreciation)
            bulletins.append(bulletin)
        
        # Calculer min/max
        calculate_min_max_moyennes(bulletins)
        
        # Vérifier les résultats
        for bulletin in bulletins:
            appreciation = bulletin.get_matiere("Test")
            assert appreciation.moyenne_s1_min == 8.0
            assert appreciation.moyenne_s1_max == 16.0
            assert appreciation.moyenne_s2_min == 11.0
            assert appreciation.moyenne_s2_max == 18.0
    
    def test_validate_bulletins_consistency(self):
        """Test la validation de cohérence des bulletins."""
        eleve = Eleve(nom="TEST", prenom="Test")
        bulletin = Bulletin(eleve=eleve)
        
        # Ajouter une appréciation avec moyenne suspecte
        appreciation = AppreciationMatiere(
            matiere="Test",
            moyenne_s1=25.0,  # Moyenne > 20, suspecte
            heures_absence_s1=150  # Heures excessives
        )
        bulletin.add_matiere(appreciation)
        
        warnings = validate_bulletins_consistency([bulletin])
        
        assert len(warnings) >= 2  # Au moins 2 avertissements
        assert any("suspecte" in w for w in warnings)
        assert any("élevées" in w for w in warnings)


class TestJsonGenerator:
    """Tests pour le module json_generator."""
    
    def test_bulletins_to_json(self):
        """Test la conversion de bulletins en JSON."""
        eleve = Eleve(nom="DUPONT", prenom="Alice")
        bulletin = Bulletin(eleve=eleve)
        
        appreciation = AppreciationMatiere(
            matiere="Mathematiques",
            moyenne_s1=15.0,
            moyenne_s2=16.0,
            appreciation_s1="Bon travail",
            appreciation_s2="Très bon travail"
        )
        bulletin.add_matiere(appreciation)
        
        json_data = bulletins_to_json([bulletin])
        
        assert len(json_data) == 1
        assert json_data[0]['Nom'] == "DUPONT"
        assert json_data[0]['Prenom'] == "Alice"
        assert 'Matieres' in json_data[0]
        assert 'Mathematiques' in json_data[0]['Matieres']
    
    def test_save_and_load_json_roundtrip(self):
        """Test sauvegarde et rechargement JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un bulletin
            eleve = Eleve(nom="TEST", prenom="Eleve")
            bulletin = Bulletin(eleve=eleve, appreciation_generale_s1="Test")
            
            # Sauvegarder
            json_path = os.path.join(temp_dir, "test.json")
            save_output_json([bulletin], json_path)
            
            # Vérifier que le fichier existe
            assert os.path.exists(json_path)
            
            # Recharger
            bulletins_loaded = load_bulletins_from_json(json_path)
            
            assert len(bulletins_loaded) == 1
            assert bulletins_loaded[0].eleve.nom == "TEST"
            assert bulletins_loaded[0].eleve.prenom == "Eleve"
            assert bulletins_loaded[0].appreciation_generale_s1 == "Test"
    
    def test_get_all_matieres(self):
        """Test la récupération de toutes les matières."""
        bulletins = []
        
        for i, matieres in enumerate([
            ["Math", "Français"],
            ["Math", "Histoire"],
            ["Anglais", "Math"]
        ]):
            eleve = Eleve(nom=f"ELEVE{i}", prenom="Test")
            bulletin = Bulletin(eleve=eleve)
            
            for matiere in matieres:
                appreciation = AppreciationMatiere(matiere=matiere)
                bulletin.add_matiere(appreciation)
            
            bulletins.append(bulletin)
        
        matieres = get_all_matieres(bulletins)
        
        assert sorted(matieres) == ["Anglais", "Français", "Histoire", "Math"]


class TestMainProcessor:
    """Tests pour le processeur principal."""
    
    def test_get_processing_summary_exemples(self):
        """Test le résumé de traitement du répertoire d'exemples."""
        summary = get_processing_summary("exemples")
        
        assert summary['valid_directory'] == True
        assert summary['source_file_exists'] == True
        assert summary['csv_files_count'] >= 3
        assert summary['estimated_bulletins'] > 0
        assert len(summary['errors']) == 0
    
    def test_process_directory_to_json_exemples(self):
        """Test le traitement complet du répertoire d'exemples."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.json")
            
            result = process_directory_to_json("exemples", output_path)
            
            assert result['success'] == True
            assert result['bulletins_count'] > 0
            assert result['matieres_count'] >= 3
            assert os.path.exists(output_path)
            
            # Vérifier le contenu du fichier généré
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert isinstance(data, list)
            assert len(data) == result['bulletins_count']
            assert all('Nom' in item and 'Prenom' in item for item in data)


class TestIntegration:
    """Tests d'intégration end-to-end."""
    
    def test_full_workflow_exemples(self):
        """Test du workflow complet avec les fichiers d'exemples."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output_integration.json")
            
            # 1. Traitement complet
            result = process_directory_to_json("exemples", output_path, validate_data=True)
            
            # 2. Vérifications de base
            assert result['success'] == True
            assert result['bulletins_count'] > 0
            assert result['matieres_count'] >= 3
            
            # 3. Vérifier que le fichier est valide
            bulletins = load_bulletins_from_json(output_path)
            assert len(bulletins) == result['bulletins_count']
            
            # 4. Vérifier qu'au moins un bulletin a des matières
            bulletins_avec_matieres = [b for b in bulletins if len(b.matieres) > 0]
            assert len(bulletins_avec_matieres) > 0
            
            # 5. Vérifier que les moyennes min/max sont calculées
            for bulletin in bulletins_avec_matieres:
                for appreciation in bulletin.matieres.values():
                    if appreciation.moyenne_s1 is not None:
                        assert appreciation.moyenne_s1_min is not None
                        assert appreciation.moyenne_s1_max is not None
                    if appreciation.moyenne_s2 is not None:
                        assert appreciation.moyenne_s2_min is not None
                        assert appreciation.moyenne_s2_max is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 