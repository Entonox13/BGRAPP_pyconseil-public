#!/usr/bin/env python3
"""
Module principal d'orchestration pour l'application de conseil de classe.
Coordonne la lecture des fichiers, le traitement et la génération JSON.
"""

import os
from typing import List, Dict, Any, Tuple
# Import conditionnel pour gérer les imports relatifs
try:
    from .file_reader import (
        read_source_xlsx, read_csv_matiere, get_csv_files_in_directory,
        extract_matiere_name_from_filename, validate_source_directory,
        FileReaderError
    )
    from .bulletin_processor import (
        create_bulletins_from_source, populate_bulletins_from_csv,
        calculate_min_max_moyennes, validate_bulletins_consistency,
        BulletinProcessorError
    )
    from .json_generator import save_output_json, JsonGeneratorError
    from ..models.bulletin import Bulletin
except ImportError:
    # Fallback pour l'exécution directe via PYTHONPATH
    from services.file_reader import (
        read_source_xlsx, read_csv_matiere, get_csv_files_in_directory,
        extract_matiere_name_from_filename, validate_source_directory,
        FileReaderError
    )
    from services.bulletin_processor import (
        create_bulletins_from_source, populate_bulletins_from_csv,
        calculate_min_max_moyennes, validate_bulletins_consistency,
        BulletinProcessorError
    )
    from services.json_generator import save_output_json, JsonGeneratorError
    from models.bulletin import Bulletin


class MainProcessorError(Exception):
    """Exception levée en cas d'erreur du processeur principal."""
    pass


def process_directory_to_json(source_directory: str, 
                             output_path: str,
                             validate_data: bool = True) -> Dict[str, Any]:
    """
    Traite un répertoire complet et génère le fichier JSON de sortie.
    
    Args:
        source_directory: Répertoire contenant source.xlsx et les fichiers CSV
        output_path: Chemin du fichier JSON de sortie
        validate_data: Si True, valide la cohérence des données
        
    Returns:
        Dictionnaire avec les résultats du traitement:
        - 'success': bool - True si le traitement a réussi
        - 'bulletins_count': int - Nombre de bulletins générés
        - 'matieres_count': int - Nombre de matières traitées
        - 'warnings': List[str] - Liste des avertissements
        - 'output_file': str - Chemin du fichier généré
        
    Raises:
        MainProcessorError: Si le traitement échoue
    """
    result = {
        'success': False,
        'bulletins_count': 0,
        'matieres_count': 0,
        'warnings': [],
        'output_file': output_path
    }
    
    try:
        # 1. Valider le répertoire source
        validation = validate_source_directory(source_directory)
        if not validation['valid']:
            raise MainProcessorError(f"Répertoire source invalide: {', '.join(validation['errors'])}")
        
        # 2. Lire le fichier source.xlsx
        eleves_data = read_source_xlsx(validation['source_xlsx'])
        if not eleves_data:
            raise MainProcessorError("Aucun élève trouvé dans source.xlsx")
        
        # 3. Créer les bulletins de base
        bulletins = create_bulletins_from_source(eleves_data)
        result['bulletins_count'] = len(bulletins)
        
        # 4. Traiter chaque fichier CSV de matière
        csv_files = validation['csv_files']
        matieres_traitees = []
        
        for csv_file in csv_files:
            matiere_name = extract_matiere_name_from_filename(csv_file)
            
            try:
                matiere_data = read_csv_matiere(csv_file, matiere_name)
                populate_bulletins_from_csv(bulletins, matiere_data, matiere_name)
                matieres_traitees.append(matiere_name)
                
            except (FileReaderError, BulletinProcessorError) as e:
                # Avertissement mais pas d'arrêt du traitement
                result['warnings'].append(f"Erreur matière {matiere_name}: {str(e)}")
        
        result['matieres_count'] = len(matieres_traitees)
        
        # 5. Calculer les moyennes min/max
        calculate_min_max_moyennes(bulletins)
        
        # 6. Validation optionnelle des données
        if validate_data:
            warnings = validate_bulletins_consistency(bulletins)
            result['warnings'].extend(warnings)
        
        # 7. Sauvegarder le JSON
        save_output_json(bulletins, output_path)
        
        result['success'] = True
        return result
        
    except (FileReaderError, BulletinProcessorError, JsonGeneratorError) as e:
        raise MainProcessorError(f"Erreur lors du traitement: {str(e)}")
    except Exception as e:
        raise MainProcessorError(f"Erreur inattendue: {str(e)}")


def process_single_bulletin(source_directory: str, nom_eleve: str) -> Bulletin:
    """
    Traite un seul bulletin d'élève (utile pour le debug/test).
    
    Args:
        source_directory: Répertoire contenant les fichiers source
        nom_eleve: Nom complet de l'élève (format "NOM Prenom")
        
    Returns:
        Objet Bulletin pour cet élève
        
    Raises:
        MainProcessorError: Si l'élève n'est pas trouvé ou erreur
    """
    try:
        # Lire tous les bulletins
        result = process_directory_to_json(source_directory, "/tmp/temp.json")
        
        # Recharger les bulletins depuis le fichier temporaire (pas optimal mais simple)
        try:
            from .json_generator import load_bulletins_from_json
        except ImportError:
            from services.json_generator import load_bulletins_from_json
        bulletins = load_bulletins_from_json("/tmp/temp.json")
        
        # Chercher l'élève demandé
        for bulletin in bulletins:
            nom_complet = f"{bulletin.eleve.nom} {bulletin.eleve.prenom}"
            if nom_complet == nom_eleve:
                return bulletin
        
        raise MainProcessorError(f"Élève non trouvé: {nom_eleve}")
        
    except Exception as e:
        raise MainProcessorError(f"Erreur lors du traitement de l'élève {nom_eleve}: {str(e)}")


def get_processing_summary(source_directory: str) -> Dict[str, Any]:
    """
    Retourne un résumé de ce qui serait traité sans faire le traitement.
    
    Args:
        source_directory: Répertoire à analyser
        
    Returns:
        Dictionnaire avec informations sur le contenu
    """
    summary = {
        'valid_directory': False,
        'source_file_exists': False,
        'csv_files_count': 0,
        'csv_files': [],
        'estimated_bulletins': 0,
        'estimated_matieres': 0,
        'errors': []
    }
    
    try:
        # Valider le répertoire
        validation = validate_source_directory(source_directory)
        summary['valid_directory'] = validation['valid']
        summary['source_file_exists'] = validation['source_xlsx'] is not None
        summary['csv_files_count'] = len(validation['csv_files'])
        summary['csv_files'] = [extract_matiere_name_from_filename(f) 
                               for f in validation['csv_files']]
        summary['estimated_matieres'] = len(validation['csv_files'])
        
        if validation['errors']:
            summary['errors'].extend(validation['errors'])
        
        # Estimer le nombre de bulletins si possible
        if validation['source_xlsx']:
            try:
                eleves_data = read_source_xlsx(validation['source_xlsx'])
                summary['estimated_bulletins'] = len(eleves_data)
            except FileReaderError as e:
                summary['errors'].append(f"Erreur lecture source.xlsx: {str(e)}")
    
    except Exception as e:
        summary['errors'].append(f"Erreur d'analyse: {str(e)}")
    
    return summary 