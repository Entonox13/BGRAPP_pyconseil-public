#!/usr/bin/env python3
"""
Module de traitement des bulletins pour l'application de conseil de classe.
Convertit les données brutes en objets Bulletin.
"""

import re
from typing import List, Dict, Any, Optional, Tuple, Sequence
# Import conditionnel pour gérer les imports relatifs
try:
    from ..models.bulletin import Eleve, AppreciationMatiere, Bulletin, parse_heures_absence, parse_moyenne
    from .file_reader import FileReaderError
    from ..utils.semester import Semester
except ImportError:
    # Fallback pour l'exécution directe via PYTHONPATH
    from models.bulletin import Eleve, AppreciationMatiere, Bulletin, parse_heures_absence, parse_moyenne
    from services.file_reader import FileReaderError
    from utils.semester import Semester


class BulletinProcessorError(Exception):
    """Exception levée en cas d'erreur de traitement des bulletins."""
    pass


def create_bulletins_from_source(eleves_data: List[Dict[str, Any]]) -> List[Bulletin]:
    """
    Crée les objets Bulletin à partir des données du fichier source.xlsx.
    
    Args:
        eleves_data: Données des élèves du fichier source.xlsx
        
    Returns:
        Liste d'objets Bulletin avec les informations de base
        
    Raises:
        BulletinProcessorError: Si les données sont invalides
    """
    if not eleves_data:
        raise BulletinProcessorError("Aucune donnée d'élève fournie")
    
    bulletins = []
    
    for eleve_dict in eleves_data:
        try:
            # Extraire le nom complet de l'élève
            nom_complet = eleve_dict.get('Élève')
            if not nom_complet:
                continue  # Ignorer les lignes sans nom
            
            # Créer l'objet Eleve
            eleve = Eleve.from_full_name(nom_complet)
            
            # Créer le bulletin avec les appréciations générales s'il y en a
            # Essayer plusieurs noms de colonnes pour la compatibilité
            appreciation_s1 = (eleve_dict.get('AppreciationGeneraleS1') or 
                              eleve_dict.get('Appreciation S1') or 
                              eleve_dict.get('AppreciationS1'))
            
            appreciation_s2 = (eleve_dict.get('AppreciationGeneraleS2') or 
                              eleve_dict.get('Appreciation S2') or 
                              eleve_dict.get('AppreciationS2'))
            
            bulletin = Bulletin(
                eleve=eleve,
                appreciation_generale_s1=appreciation_s1,
                appreciation_generale_s2=appreciation_s2
            )
            
            bulletins.append(bulletin)
            
        except ValueError as e:
            raise BulletinProcessorError(f"Erreur lors du parsing du nom '{nom_complet}': {str(e)}")
        except Exception as e:
            raise BulletinProcessorError(f"Erreur lors de la création du bulletin: {str(e)}")
    
    return bulletins


def parse_rappel_s1(rappel_text: str) -> Tuple[Optional[float], Optional[int], Optional[str]]:
    """
    Parse la colonne 'Rappel de la période précédente : S1' pour extraire
    moyenne S1, heures d'absence S1 et appréciation S1.
    
    Format attendu: "Moy. : 16,50 - H.Abs : 1h00 - Appréciation..."
    
    Args:
        rappel_text: Texte de la colonne rappel
        
    Returns:
        Tuple (moyenne_s1, heures_absence_s1, appreciation_s1)
    """
    if not rappel_text or rappel_text.strip() == '':
        return None, None, None
    
    moyenne_s1 = None
    heures_absence_s1 = None
    appreciation_s1 = None
    
    # Rechercher la moyenne S1
    match_moy = re.search(r'Moy\.\s*:\s*([0-9,]+)', rappel_text)
    if match_moy:
        moyenne_s1 = parse_moyenne(match_moy.group(1))
    
    # Rechercher les heures d'absence S1
    match_abs = re.search(r'H\.Abs\s*:\s*([0-9]+h[0-9]*)', rappel_text)
    if match_abs:
        heures_absence_s1 = parse_heures_absence(match_abs.group(1))
    
    # L'appréciation est généralement après le dernier tiret
    parts = rappel_text.split(' - ')
    if len(parts) >= 3:
        # Prendre tout après les deux premières parties (Moy et H.Abs)
        appreciation_s1 = ' - '.join(parts[2:]).strip()
        if appreciation_s1 == '':
            appreciation_s1 = None
    elif len(parts) == 2 and not match_abs:
        # Si pas d'heures d'absence mentionnées, l'appréciation est après la moyenne
        appreciation_s1 = parts[1].strip()
        if appreciation_s1 == '':
            appreciation_s1 = None
    elif len(parts) == 1 and not match_moy and not match_abs:
        # Si aucun pattern reconnu, tout le texte est l'appréciation
        appreciation_s1 = rappel_text.strip()
    
    return moyenne_s1, heures_absence_s1, appreciation_s1


def populate_bulletins_from_csv(bulletins: List[Bulletin], 
                               matiere_data: List[Dict[str, Any]], 
                               matiere_name: str,
                               semester: Semester) -> None:
    """
    Ajoute les appréciations d'une matière aux bulletins existants.
    
    Args:
        bulletins: Liste des bulletins à compléter
        matiere_data: Données de la matière depuis le CSV
        matiere_name: Nom de la matière
        semester: Semestre détecté pour orienter le mapping des colonnes
        
    Raises:
        BulletinProcessorError: Si les données sont incohérentes
    """
    if not bulletins:
        raise BulletinProcessorError("Aucun bulletin fourni")
    
    if not matiere_data:
        # Pas d'erreur si aucune donnée pour cette matière
        return
    
    # Créer un index des bulletins par nom complet d'élève
    bulletins_index = {}
    for bulletin in bulletins:
        nom_complet = f"{bulletin.eleve.nom} {bulletin.eleve.prenom}"
        bulletins_index[nom_complet] = bulletin
    
    def _get_first_value(row: Dict[str, Any], keys: Sequence[str]) -> Optional[Any]:
        """Retourne la première valeur non vide correspondant aux clés données."""
        for key in keys:
            if key not in row:
                continue
            value = row.get(key)
            if value not in (None, ""):
                return value
        return None
    
    # Traiter chaque ligne de données de matière
    for ligne in matiere_data:
        nom_eleve = ligne.get('Élève')
        if not nom_eleve:
            continue
        
        # Nettoyer le nom (supprimer les guillemets)
        nom_eleve = nom_eleve.strip('"').strip()
        
        # Trouver le bulletin correspondant
        bulletin = bulletins_index.get(nom_eleve)
        if not bulletin:
            # Élève non trouvé dans source.xlsx - on continue sans erreur
            # (peut arriver si les fichiers ne sont pas parfaitement synchronisés)
            continue
        
        # Créer l'appréciation pour cette matière
        appreciation = AppreciationMatiere(matiere=matiere_name)
        
        # Parser les heures d'absence selon le semestre
        heures_abs_value = _get_first_value(ligne, ['H.Abs.', 'H Abs.', 'Absences'])
        if heures_abs_value:
            if semester == Semester.S1:
                appreciation.heures_absence_s1 = parse_heures_absence(heures_abs_value)
            else:
                appreciation.heures_absence_s2 = parse_heures_absence(heures_abs_value)
        
        # Parser la moyenne selon le semestre
        if semester == Semester.S1:
            moy_value = _get_first_value(ligne, ['Moy. S1', 'Moyenne S1'])
            if moy_value is not None:
                appreciation.moyenne_s1 = parse_moyenne(str(moy_value))
        else:
            moy_value = _get_first_value(ligne, ['Moy. S2', 'Moyenne S2'])
            if moy_value is not None:
                appreciation.moyenne_s2 = parse_moyenne(str(moy_value))
        
        # Parser l'appréciation principale
        appreciation_value = _get_first_value(
            ligne,
            ['App. A : Appréciations', 'Appréciations', 'Appreciations']
        )
        if appreciation_value:
            appreciation_text = str(appreciation_value).strip()
            if semester == Semester.S1:
                appreciation.appreciation_s1 = appreciation_text
            else:
                appreciation.appreciation_s2 = appreciation_text
        
        # En S2, parser le rappel S1 (moyenne/heures/appreciation)
        if semester == Semester.S2:
            rappel_s1 = ligne.get('Rappel de la période précédente : S1')
            if rappel_s1:
                moy_s1, abs_s1, app_s1 = parse_rappel_s1(rappel_s1)
                appreciation.moyenne_s1 = moy_s1
                appreciation.heures_absence_s1 = abs_s1
                appreciation.appreciation_s1 = app_s1
        
        # Ajouter l'appréciation au bulletin
        bulletin.add_matiere(appreciation)


def calculate_min_max_moyennes(bulletins: List[Bulletin]) -> None:
    """
    Calcule les moyennes min/max par matière et semestre pour tous les bulletins.
    
    Args:
        bulletins: Liste des bulletins à traiter
    """
    if not bulletins:
        return
    
    # Collecter toutes les matières
    matieres = set()
    for bulletin in bulletins:
        matieres.update(bulletin.matieres.keys())
    
    # Pour chaque matière, calculer min/max par semestre
    for matiere_name in matieres:
        # Collecter les moyennes S1 et S2
        moyennes_s1 = []
        moyennes_s2 = []
        
        for bulletin in bulletins:
            appreciation = bulletin.get_matiere(matiere_name)
            if appreciation:
                if appreciation.moyenne_s1 is not None:
                    moyennes_s1.append(appreciation.moyenne_s1)
                if appreciation.moyenne_s2 is not None:
                    moyennes_s2.append(appreciation.moyenne_s2)
        
        # Calculer min/max S1
        min_s1 = min(moyennes_s1) if moyennes_s1 else None
        max_s1 = max(moyennes_s1) if moyennes_s1 else None
        
        # Calculer min/max S2
        min_s2 = min(moyennes_s2) if moyennes_s2 else None
        max_s2 = max(moyennes_s2) if moyennes_s2 else None
        
        # Mettre à jour tous les bulletins pour cette matière
        for bulletin in bulletins:
            appreciation = bulletin.get_matiere(matiere_name)
            if appreciation:
                appreciation.moyenne_s1_min = min_s1
                appreciation.moyenne_s1_max = max_s1
                appreciation.moyenne_s2_min = min_s2
                appreciation.moyenne_s2_max = max_s2


def validate_bulletins_consistency(bulletins: List[Bulletin]) -> List[str]:
    """
    Valide la cohérence des données dans les bulletins.
    
    Args:
        bulletins: Liste des bulletins à valider
        
    Returns:
        Liste des messages d'avertissement/erreur trouvés
    """
    warnings = []
    
    if not bulletins:
        warnings.append("Aucun bulletin à valider")
        return warnings
    
    # Vérifier les doublons d'élèves
    noms_complets = []
    for bulletin in bulletins:
        nom_complet = f"{bulletin.eleve.nom} {bulletin.eleve.prenom}"
        if nom_complet in noms_complets:
            warnings.append(f"Élève en doublon: {nom_complet}")
        noms_complets.append(nom_complet)
    
    # Vérifier la cohérence des données par matière
    for bulletin in bulletins:
        nom_eleve = f"{bulletin.eleve.nom} {bulletin.eleve.prenom}"
        
        for matiere_name, appreciation in bulletin.matieres.items():
            # Vérifier que les moyennes sont dans une plage raisonnable
            for semestre, moyenne in [('S1', appreciation.moyenne_s1), ('S2', appreciation.moyenne_s2)]:
                if moyenne is not None and (moyenne < 0 or moyenne > 20):
                    warnings.append(f"{nom_eleve} - {matiere_name} {semestre}: Moyenne suspecte ({moyenne})")
            
            # Vérifier que les heures d'absence ne sont pas excessives
            for semestre, heures in [('S1', appreciation.heures_absence_s1), ('S2', appreciation.heures_absence_s2)]:
                if heures is not None and heures > 100:  # Plus de 100h semble suspect
                    warnings.append(f"{nom_eleve} - {matiere_name} {semestre}: Heures d'absence élevées ({heures}h)")
    
    return warnings 