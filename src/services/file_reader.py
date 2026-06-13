#!/usr/bin/env python3
"""
Module de lecture des fichiers source pour l'application de conseil de classe.
Lit le fichier source.xlsx et les fichiers CSV par matière.
"""

import pandas as pd
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class FileReaderError(Exception):
    """Exception levée en cas d'erreur de lecture des fichiers."""
    pass


def read_source_xlsx(file_path: str) -> List[Dict[str, Any]]:
    """
    Lit le fichier source.xlsx et retourne la liste des élèves.
    
    Args:
        file_path: Chemin vers le fichier source.xlsx
        
    Returns:
        Liste de dictionnaires contenant les données des élèves
        
    Raises:
        FileReaderError: Si le fichier n'existe pas ou ne peut pas être lu
    """
    if not os.path.exists(file_path):
        raise FileReaderError(f"Fichier source non trouvé: {file_path}")
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(file_path)
        
        # Valider la présence de la colonne 'Élève'
        if 'Élève' not in df.columns:
            raise FileReaderError("Colonne 'Élève' manquante dans le fichier source.xlsx")
        
        # Convertir en liste de dictionnaires
        eleves_data = []
        for _, row in df.iterrows():
            eleve_dict = {}
            for col in df.columns:
                # Conserver toutes les colonnes, nettoyer les valeurs NaN
                value = row[col]
                if pd.isna(value):
                    value = None
                eleve_dict[col] = value
            eleves_data.append(eleve_dict)
        
        return eleves_data
        
    except Exception as e:
        raise FileReaderError(f"Erreur lors de la lecture du fichier source.xlsx: {str(e)}")


def read_csv_matiere(file_path: str, matiere_name: str) -> List[Dict[str, Any]]:
    """
    Lit un fichier CSV de matière et retourne les données formatées.
    
    Args:
        file_path: Chemin vers le fichier CSV de la matière
        matiere_name: Nom de la matière (pour référence)
        
    Returns:
        Liste de dictionnaires contenant les données par élève pour cette matière
        
    Raises:
        FileReaderError: Si le fichier n'existe pas ou ne peut pas être lu
    """
    if not os.path.exists(file_path):
        raise FileReaderError(f"Fichier matière non trouvé: {file_path}")
    
    try:
        # Lire le fichier CSV avec séparateur point-virgule
        df = pd.read_csv(file_path, sep=';', encoding='utf-8')
        
        # Valider la présence de la colonne 'Élève'
        if 'Élève' not in df.columns:
            raise FileReaderError(f"Colonne 'Élève' manquante dans le fichier {file_path}")
        
        # Convertir en liste de dictionnaires
        matiere_data = []
        for _, row in df.iterrows():
            eleve_dict = {'matiere': matiere_name}
            for col in df.columns:
                # Conserver toutes les colonnes, nettoyer les valeurs NaN
                value = row[col]
                if pd.isna(value):
                    value = None
                elif isinstance(value, str):
                    value = value.strip()  # Nettoyer les espaces
                eleve_dict[col] = value
            matiere_data.append(eleve_dict)
        
        return matiere_data
        
    except Exception as e:
        raise FileReaderError(f"Erreur lors de la lecture du fichier {file_path}: {str(e)}")


def get_csv_files_in_directory(directory_path: str) -> List[str]:
    """
    Trouve tous les fichiers CSV dans un répertoire (excluant source.xlsx).
    
    Args:
        directory_path: Chemin du répertoire à scanner
        
    Returns:
        Liste des chemins des fichiers CSV trouvés
        
    Raises:
        FileReaderError: Si le répertoire n'existe pas
    """
    if not os.path.exists(directory_path):
        raise FileReaderError(f"Répertoire non trouvé: {directory_path}")
    
    directory = Path(directory_path)
    csv_files = []
    
    for file_path in directory.glob("*.csv"):
        csv_files.append(str(file_path))
    
    return sorted(csv_files)  # Tri pour un ordre prévisible


def extract_matiere_name_from_filename(file_path: str) -> str:
    """
    Extrait le nom de la matière à partir du nom de fichier CSV.
    
    Args:
        file_path: Chemin du fichier CSV
        
    Returns:
        Nom de la matière (nom du fichier sans extension)
    """
    return Path(file_path).stem


def validate_source_directory(directory_path: str) -> Dict[str, Any]:
    """
    Valide qu'un répertoire contient les fichiers requis et retourne un résumé.
    
    Args:
        directory_path: Chemin du répertoire à valider
        
    Returns:
        Dictionnaire avec informations de validation:
        - 'valid': bool - True si le répertoire est valide
        - 'source_xlsx': str|None - Chemin du fichier source.xlsx
        - 'csv_files': List[str] - Liste des fichiers CSV trouvés
        - 'errors': List[str] - Liste des erreurs rencontrées
        
    """
    validation = {
        'valid': False,
        'source_xlsx': None,
        'csv_files': [],
        'errors': []
    }
    
    if not os.path.exists(directory_path):
        validation['errors'].append(f"Répertoire non trouvé: {directory_path}")
        return validation
    
    # Vérifier la présence de source.xlsx
    source_path = os.path.join(directory_path, 'source.xlsx')
    if os.path.exists(source_path):
        validation['source_xlsx'] = source_path
    else:
        validation['errors'].append("Fichier source.xlsx manquant")
    
    # Chercher les fichiers CSV
    try:
        csv_files = get_csv_files_in_directory(directory_path)
        validation['csv_files'] = csv_files
        
        if len(csv_files) == 0:
            validation['errors'].append("Aucun fichier CSV de matière trouvé")
        
    except FileReaderError as e:
        validation['errors'].append(str(e))
    
    # Le répertoire est valide s'il n'y a pas d'erreurs
    validation['valid'] = len(validation['errors']) == 0
    
    return validation 