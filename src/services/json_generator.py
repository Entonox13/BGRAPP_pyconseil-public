#!/usr/bin/env python3
"""
Module de génération JSON pour l'application de conseil de classe.
Convertit les objets Bulletin en JSON et sauvegarde le fichier output.json.
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime
# Import conditionnel pour gérer les imports relatifs
try:
    from ..models.bulletin import Bulletin
except ImportError:
    # Fallback pour l'exécution directe via PYTHONPATH
    from models.bulletin import Bulletin


class JsonGeneratorError(Exception):
    """Exception levée en cas d'erreur de génération JSON."""
    pass


def bulletins_to_json(bulletins: List[Bulletin]) -> List[Dict[str, Any]]:
    """
    Convertit une liste d'objets Bulletin en structure JSON.
    
    Args:
        bulletins: Liste des bulletins à convertir
        
    Returns:
        Liste de dictionnaires prêts pour la sérialisation JSON
        
    Raises:
        JsonGeneratorError: Si la conversion échoue
    """
    if not bulletins:
        raise JsonGeneratorError("Aucun bulletin à convertir")
    
    try:
        json_data = []
        
        for bulletin in bulletins:
            bulletin_dict = bulletin.to_dict()
            json_data.append(bulletin_dict)
        
        return json_data
        
    except Exception as e:
        raise JsonGeneratorError(f"Erreur lors de la conversion en JSON: {str(e)}")


def save_output_json(bulletins: List[Bulletin], 
                    output_path: str,
                    pretty_print: bool = True) -> None:
    """
    Sauvegarde les bulletins dans un fichier JSON.
    
    Args:
        bulletins: Liste des bulletins à sauvegarder
        output_path: Chemin du fichier de sortie
        pretty_print: Si True, formate le JSON pour la lisibilité
        
    Raises:
        JsonGeneratorError: Si la sauvegarde échoue
    """
    if not bulletins:
        raise JsonGeneratorError("Aucun bulletin à sauvegarder")
    
    try:
        # Convertir les bulletins en JSON
        json_data = bulletins_to_json(bulletins)
        
        # Créer le répertoire parent si nécessaire
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Sauvegarder le fichier JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty_print:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(json_data, f, ensure_ascii=False)
        
    except Exception as e:
        raise JsonGeneratorError(f"Erreur lors de la sauvegarde du fichier {output_path}: {str(e)}")


def load_bulletins_from_json(json_path: str) -> List[Bulletin]:
    """
    Charge des bulletins depuis un fichier JSON.
    
    Args:
        json_path: Chemin du fichier JSON à charger
        
    Returns:
        Liste d'objets Bulletin reconstruits
        
    Raises:
        JsonGeneratorError: Si le chargement échoue
    """
    if not os.path.exists(json_path):
        raise JsonGeneratorError(f"Fichier JSON non trouvé: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        bulletins = []
        for item in data:
            if isinstance(item, dict) and "Nom" in item and "Prenom" in item:
                bulletin = Bulletin.from_dict(item)
                bulletins.append(bulletin)
        
        return bulletins
        
    except Exception as e:
        raise JsonGeneratorError(f"Erreur lors du chargement du fichier {json_path}: {str(e)}")


def validate_json_format(json_path: str) -> Dict[str, Any]:
    """
    Valide le format d'un fichier JSON de bulletins.
    
    Args:
        json_path: Chemin du fichier JSON à valider
        
    Returns:
        Dictionnaire avec les résultats de validation:
        - 'valid': bool - True si le format est valide
        - 'bulletins_count': int - Nombre de bulletins trouvés
        - 'errors': List[str] - Liste des erreurs trouvées
        - 'warnings': List[str] - Liste des avertissements
    """
    validation = {
        'valid': False,
        'bulletins_count': 0,
        'errors': [],
        'warnings': []
    }
    
    if not os.path.exists(json_path):
        validation['errors'].append(f"Fichier non trouvé: {json_path}")
        return validation
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            validation['errors'].append("Le fichier JSON doit contenir une liste")
            return validation
        
        # Ignorer les métadonnées si présentes
        bulletins_data = data
        if len(data) > 0 and isinstance(data[0], dict) and "_metadata" in data[0]:
            bulletins_data = data[1:]
            validation['warnings'].append("Métadonnées détectées et ignorées")
        
        validation['bulletins_count'] = len(bulletins_data)
        
        # Valider chaque bulletin
        required_fields = ['Nom', 'Prenom']
        for i, bulletin_data in enumerate(bulletins_data):
            if not isinstance(bulletin_data, dict):
                validation['errors'].append(f"Bulletin {i+1}: doit être un objet JSON")
                continue
            
            # Vérifier les champs requis
            for field in required_fields:
                if field not in bulletin_data:
                    validation['errors'].append(f"Bulletin {i+1}: champ '{field}' manquant")
            
            # Vérifier la structure des matières si présente
            if 'Matieres' in bulletin_data:
                matieres = bulletin_data['Matieres']
                if not isinstance(matieres, dict):
                    validation['errors'].append(f"Bulletin {i+1}: 'Matieres' doit être un objet")
        
        # Le fichier est valide s'il n'y a pas d'erreurs
        validation['valid'] = len(validation['errors']) == 0
        
    except json.JSONDecodeError as e:
        validation['errors'].append(f"Erreur de format JSON: {str(e)}")
    except Exception as e:
        validation['errors'].append(f"Erreur lors de la validation: {str(e)}")
    
    return validation


def get_all_matieres(bulletins: List[Bulletin]) -> List[str]:
    """
    Récupère la liste de toutes les matières présentes dans les bulletins.
    
    Args:
        bulletins: Liste des bulletins à analyser
        
    Returns:
        Liste triée des noms de matières uniques
    """
    matieres = set()
    for bulletin in bulletins:
        matieres.update(bulletin.matieres.keys())
    return sorted(list(matieres))


def generate_summary_stats(bulletins: List[Bulletin]) -> Dict[str, Any]:
    """
    Génère des statistiques de résumé sur les bulletins.
    
    Args:
        bulletins: Liste des bulletins à analyser
        
    Returns:
        Dictionnaire avec statistiques diverses
    """
    if not bulletins:
        return {}
    
    stats = {
        'total_bulletins': len(bulletins),
        'total_matieres': len(get_all_matieres(bulletins)),
        'matieres_list': get_all_matieres(bulletins),
    }
    
    # Compter les appréciations par semestre
    appreciation_s1_count = 0
    appreciation_s2_count = 0
    
    for bulletin in bulletins:
        if bulletin.appreciation_generale_s1:
            appreciation_s1_count += 1
        if bulletin.appreciation_generale_s2:
            appreciation_s2_count += 1
    
    stats['appreciation_generale_s1_count'] = appreciation_s1_count
    stats['appreciation_generale_s2_count'] = appreciation_s2_count
    
    # Statistiques par matière
    matiere_stats = {}
    for matiere in get_all_matieres(bulletins):
        bulletins_avec_matiere = 0
        moyennes_s1 = []
        moyennes_s2 = []
        
        for bulletin in bulletins:
            appreciation = bulletin.get_matiere(matiere)
            if appreciation:
                bulletins_avec_matiere += 1
                if appreciation.moyenne_s1 is not None:
                    moyennes_s1.append(appreciation.moyenne_s1)
                if appreciation.moyenne_s2 is not None:
                    moyennes_s2.append(appreciation.moyenne_s2)
        
        matiere_stats[matiere] = {
            'bulletins_count': bulletins_avec_matiere,
            'moyenne_s1_count': len(moyennes_s1),
            'moyenne_s2_count': len(moyennes_s2),
        }
        
        if moyennes_s1:
            matiere_stats[matiere]['moyenne_s1_avg'] = sum(moyennes_s1) / len(moyennes_s1)
        if moyennes_s2:
            matiere_stats[matiere]['moyenne_s2_avg'] = sum(moyennes_s2) / len(moyennes_s2)
    
    stats['matieres_stats'] = matiere_stats
    
    return stats 