#!/usr/bin/env python3
"""
Module principal d'orchestration pour l'application de conseil de classe.
Coordonne la lecture des fichiers, le traitement et la génération JSON.
"""

import os
import copy
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
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
    from .json_generator import save_output_json, load_bulletins_from_json, JsonGeneratorError
    from ..models.bulletin import Bulletin
    from ..utils.semester import Period, detect_period_from_matiere_data
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
    from services.json_generator import save_output_json, load_bulletins_from_json, JsonGeneratorError
    from models.bulletin import Bulletin
    from utils.semester import Period, detect_period_from_matiere_data


class MainProcessorError(Exception):
    """Exception levée en cas d'erreur du processeur principal."""
    pass


def merge_history_into_bulletins(bulletins: List[Bulletin],
                                 previous_bulletins: List[Bulletin],
                                 current_code: str) -> None:
    """
    Fusionne l'historique des périodes précédentes (issu d'un output JSON
    existant) dans les bulletins fraîchement construits.

    Les données de la période courante (`current_code`) ne sont jamais
    écrasées : seules les périodes antérieures absentes sont reportées.

    Args:
        bulletins: Bulletins de la période courante (modifiés sur place)
        previous_bulletins: Bulletins chargés depuis l'output existant
        current_code: Code de la période courante (ex: "T3")
    """
    if not previous_bulletins:
        return

    # On ne fusionne que les périodes du même système (trimestre/semestre) que
    # la période courante : un traitement T2 ne doit pas récupérer des données
    # S1/S2 issues d'un ancien output, et inversement (évite les conflits).
    current_period = Period.from_code(current_code)
    current_system = current_period.system if current_period else None

    def _same_system(code: str) -> bool:
        if current_system is None:
            return True
        period = Period.from_code(code)
        return period is not None and period.system == current_system

    prev_index = {
        f"{b.eleve.nom} {b.eleve.prenom}": b for b in previous_bulletins
    }

    for bulletin in bulletins:
        key = f"{bulletin.eleve.nom} {bulletin.eleve.prenom}"
        previous = prev_index.get(key)
        if not previous:
            continue

        # Reporter les appréciations générales des périodes précédentes
        for code, texte in previous.appreciations_generales.items():
            if code == current_code or not _same_system(code):
                continue
            if code not in bulletin.appreciations_generales:
                bulletin.appreciations_generales[code] = texte

        # Reporter les données par matière/période
        for matiere_name, prev_app in previous.matieres.items():
            current_app = bulletin.get_matiere(matiere_name)
            if current_app is None:
                # Matière absente de l'export courant : conserver l'historique
                # (copie), en filtrant les périodes d'un autre système.
                clone = copy.deepcopy(prev_app)
                clone.periodes = {
                    code: periode
                    for code, periode in clone.periodes.items()
                    if _same_system(code)
                }
                if clone.periodes:
                    bulletin.add_matiere(clone)
                continue
            for code, periode in prev_app.periodes.items():
                if code == current_code or not _same_system(code):
                    continue
                if code not in current_app.periodes:
                    current_app.periodes[code] = copy.deepcopy(periode)


def process_directory_to_json(source_directory: str, 
                             output_path: str,
                             validate_data: bool = True,
                             merge_history: bool = False,
                             period_override: Optional["Period"] = None) -> Dict[str, Any]:
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
        - 'semester': str - Semestre détecté (S1/S2)
        
    Raises:
        MainProcessorError: Si le traitement échoue
    """
    result = {
        'success': False,
        'bulletins_count': 0,
        'matieres_count': 0,
        'warnings': [],
        'output_file': output_path,
        'semester': Period.S2.value,
        'period': Period.S2.value,
        'period_system': Period.S2.system.value
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
        
        # Période initiale (override ou défaut) — utilisée pour lire source.xlsx
        period = period_override if period_override is not None else Period.S2
        period_detected = period_override is not None

        # 3. Créer les bulletins de base (appréciations générales du source.xlsx)
        bulletins = create_bulletins_from_source(eleves_data, period=period)
        result['bulletins_count'] = len(bulletins)
        
        # 4. Traiter chaque fichier CSV de matière
        csv_files = validation['csv_files']
        matieres_traitees = []
        for csv_file in csv_files:
            matiere_name = extract_matiere_name_from_filename(csv_file)
            
            try:
                matiere_data = read_csv_matiere(csv_file, matiere_name)
                
                if not period_detected and matiere_data:
                    period = detect_period_from_matiere_data(matiere_data)
                    period_detected = True
                
                populate_bulletins_from_csv(bulletins, matiere_data, matiere_name, period)
                matieres_traitees.append(matiere_name)
                
            except (FileReaderError, BulletinProcessorError) as e:
                # Avertissement mais pas d'arrêt du traitement
                result['warnings'].append(f"Erreur matière {matiere_name}: {str(e)}")
        
        result['matieres_count'] = len(matieres_traitees)
        result['semester'] = period.value
        result['period'] = period.value
        result['period_system'] = period.system.value
        
        # 5. Fusionner l'historique des périodes précédentes (output existant)
        if merge_history and os.path.exists(output_path):
            try:
                previous_bulletins = load_bulletins_from_json(output_path)
                merge_history_into_bulletins(bulletins, previous_bulletins, period.value)
            except JsonGeneratorError as e:
                result['warnings'].append(f"Historique ignoré (output illisible): {str(e)}")
        
        # 6. Calculer les moyennes min/max (après fusion historique)
        calculate_min_max_moyennes(bulletins)
        
        # 7. Validation optionnelle des données
        if validate_data:
            warnings = validate_bulletins_consistency(bulletins)
            result['warnings'].extend(warnings)
        
        # 8. Sauvegarder le JSON
        metadata = {
            "semester": period.value,
            "current_period": period.value,
            "period_system": period.system.value,
            "period_label": period.label,
            "semester_label": period.label,
            "generated_at": datetime.utcnow().isoformat(timespec="seconds"),
            "source_directory": os.path.abspath(source_directory),
            "matieres_count": len(matieres_traitees)
        }
        save_output_json(bulletins, output_path, metadata=metadata)
        
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
        # Lire tous les bulletins (sans fusion d'historique sur le fichier temporaire)
        result = process_directory_to_json(source_directory, "/tmp/temp.json", merge_history=False)
        
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