#!/usr/bin/env python3
"""
Module de traitement des bulletins pour l'application de conseil de classe.
Convertit les données brutes en objets Bulletin.
"""

import re
from typing import List, Dict, Any, Optional, Tuple, Sequence
# Import conditionnel pour gérer les imports relatifs
try:
    from ..models.bulletin import (
        Eleve, AppreciationMatiere, Bulletin,
        parse_heures_absence, parse_moyenne, parse_retards,
        normalize_absence, absence_to_hours,
    )
    from .file_reader import FileReaderError
    from ..utils.semester import Period, PeriodSystem, PERIOD_CODES
except ImportError:
    # Fallback pour l'exécution directe via PYTHONPATH
    from models.bulletin import (
        Eleve, AppreciationMatiere, Bulletin,
        parse_heures_absence, parse_moyenne, parse_retards,
        normalize_absence, absence_to_hours,
    )
    from services.file_reader import FileReaderError
    from utils.semester import Period, PeriodSystem, PERIOD_CODES


class BulletinProcessorError(Exception):
    """Exception levée en cas d'erreur de traitement des bulletins."""
    pass


_GENERAL_APPRECIATION_COLUMN_ALIASES = {
    code: [
        f"AppreciationGenerale{code}",
        f"Appreciation {code}",
        f"Appreciation{code}",
    ]
    for code in PERIOD_CODES
}


def _read_general_appreciation_value(eleve_dict: Dict[str, Any], code: str) -> Optional[str]:
    """Lit une appréciation générale depuis les colonnes source.xlsx connues."""
    for key in _GENERAL_APPRECIATION_COLUMN_ALIASES.get(code, []):
        value = eleve_dict.get(key)
        if value is None:
            continue
        if isinstance(value, float) and value != value:  # NaN
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def create_bulletins_from_source(
    eleves_data: List[Dict[str, Any]],
    period: Optional[Period] = None,
) -> List[Bulletin]:
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
            bulletin = Bulletin(eleve=eleve)
            skip_semestre_codes = (
                period is not None and period.system == PeriodSystem.TRIMESTRE
            )
            for code in PERIOD_CODES:
                if skip_semestre_codes and code in ("S1", "S2"):
                    continue
                texte = _read_general_appreciation_value(eleve_dict, code)
                if texte:
                    bulletin.set_appreciation_generale(code, texte)

            # Rétro-compat : colonnes S1/S2 du source.xlsx utilisées pour T1/T2
            if skip_semestre_codes:
                if not bulletin.get_appreciation_generale("T1"):
                    s1 = _read_general_appreciation_value(eleve_dict, "S1")
                    if s1:
                        bulletin.set_appreciation_generale("T1", s1)
                if not bulletin.get_appreciation_generale("T2"):
                    s2 = _read_general_appreciation_value(eleve_dict, "S2")
                    if s2:
                        bulletin.set_appreciation_generale("T2", s2)
            
            bulletins.append(bulletin)
            
        except ValueError as e:
            raise BulletinProcessorError(f"Erreur lors du parsing du nom '{nom_complet}': {str(e)}")
        except Exception as e:
            raise BulletinProcessorError(f"Erreur lors de la création du bulletin: {str(e)}")
    
    return bulletins


def parse_rappel_periode(rappel_text: str) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    """
    Parse une colonne 'Rappel de la période précédente' pour extraire
    moyenne, heures d'absence et appréciation de la période précédente.
    
    Format attendu: "Moy. : 16,50 - H.Abs : 1h00 - Appréciation..."
    
    Args:
        rappel_text: Texte de la colonne rappel
        
    Returns:
        Tuple (moyenne, heures_absence, appreciation)
    """
    if not rappel_text or str(rappel_text).strip() == '':
        return None, None, None
    
    rappel_text = str(rappel_text)
    moyenne = None
    heures_absence = None
    appreciation = None
    
    # Rechercher la moyenne
    match_moy = re.search(r'Moy\.\s*:\s*([0-9,]+)', rappel_text)
    if match_moy:
        moyenne = parse_moyenne(match_moy.group(1))
    
    # Rechercher les heures d'absence
    match_abs = re.search(r'H\.Abs\s*:\s*([0-9]+h[0-9]*)', rappel_text)
    if match_abs:
        heures_absence = normalize_absence(match_abs.group(1))
    
    # L'appréciation est généralement après le dernier tiret
    parts = rappel_text.split(' - ')
    if len(parts) >= 3:
        # Prendre tout après les deux premières parties (Moy et H.Abs)
        appreciation = ' - '.join(parts[2:]).strip()
        if appreciation == '':
            appreciation = None
    elif len(parts) == 2 and not match_abs:
        # Si pas d'heures d'absence mentionnées, l'appréciation est après la moyenne
        appreciation = parts[1].strip()
        if appreciation == '':
            appreciation = None
    elif len(parts) == 1 and not match_moy and not match_abs:
        # Si aucun pattern reconnu, tout le texte est l'appréciation
        appreciation = rappel_text.strip()
    
    return moyenne, heures_absence, appreciation


# Alias rétro-compatible
parse_rappel_s1 = parse_rappel_periode


def populate_bulletins_from_csv(bulletins: List[Bulletin], 
                               matiere_data: List[Dict[str, Any]], 
                               matiere_name: str,
                               period: Period) -> None:
    """
    Ajoute les appréciations d'une matière aux bulletins existants pour
    la période courante détectée.
    
    Args:
        bulletins: Liste des bulletins à compléter
        matiere_data: Données de la matière depuis le CSV
        matiere_name: Nom de la matière
        period: Période détectée (S1/S2/T1/T2/T3) pour le mapping des colonnes
        
    Raises:
        BulletinProcessorError: Si les données sont incohérentes
    """
    if not bulletins:
        raise BulletinProcessorError("Aucun bulletin fourni")
    
    if not matiere_data:
        # Pas d'erreur si aucune donnée pour cette matière
        return
    
    code = period.value  # ex: "T3", "S2"
    
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
        nom_eleve = str(nom_eleve).strip('"').strip()
        
        # Trouver le bulletin correspondant
        bulletin = bulletins_index.get(nom_eleve)
        if not bulletin:
            # Élève non trouvé dans source.xlsx - on continue sans erreur
            # (peut arriver si les fichiers ne sont pas parfaitement synchronisés)
            continue
        
        # Récupérer (ou créer) l'appréciation pour cette matière
        appreciation = bulletin.get_matiere(matiere_name)
        if appreciation is None:
            appreciation = AppreciationMatiere(matiere=matiere_name)
            bulletin.add_matiere(appreciation)
        
        periode_data = appreciation.ensure_periode(code)
        
        # Parser les heures d'absence (stockage fidèle "XhMM")
        heures_abs_value = _get_first_value(ligne, ['H.Abs.', 'H Abs.', 'Absences'])
        if heures_abs_value:
            periode_data.heures_absence = normalize_absence(heures_abs_value)
        
        # Parser les retards
        retards_value = _get_first_value(ligne, ['Ret.', 'Retards', 'Ret'])
        if retards_value is not None:
            periode_data.retards = parse_retards(retards_value)
        
        # Parser la moyenne de la période courante
        moy_value = _get_first_value(
            ligne,
            [f'Moy. {code}', f'Moyenne {code}', 'Moy.', 'Moyenne']
        )
        if moy_value is not None:
            periode_data.moyenne = parse_moyenne(str(moy_value))
        
        # Parser l'appréciation principale
        appreciation_value = _get_first_value(
            ligne,
            ['App. A : Appréciations', 'Appréciations', 'Appreciations']
        )
        if appreciation_value:
            periode_data.appreciation = str(appreciation_value).strip()
        
        # Parser un éventuel rappel de la période précédente (mode semestre S2)
        previous = period.previous
        if previous is not None:
            rappel_text = _get_first_value(
                ligne,
                [
                    f'Rappel de la période précédente : {previous.value}',
                    'Rappel de la période précédente : S1',
                ]
            )
            if rappel_text:
                moy_prev, abs_prev, app_prev = parse_rappel_periode(rappel_text)
                prev_data = appreciation.ensure_periode(previous.value)
                if moy_prev is not None:
                    prev_data.moyenne = moy_prev
                if abs_prev is not None:
                    prev_data.heures_absence = abs_prev
                if app_prev is not None:
                    prev_data.appreciation = app_prev


def calculate_min_max_moyennes(bulletins: List[Bulletin]) -> None:
    """
    Calcule les moyennes min/max par matière et par période pour tous
    les bulletins.
    
    Args:
        bulletins: Liste des bulletins à traiter
    """
    if not bulletins:
        return
    
    # Collecter toutes les matières
    matieres = set()
    for bulletin in bulletins:
        matieres.update(bulletin.matieres.keys())
    
    # Pour chaque matière, calculer min/max par période présente
    for matiere_name in matieres:
        # Identifier les périodes présentes pour cette matière
        codes = set()
        for bulletin in bulletins:
            appreciation = bulletin.get_matiere(matiere_name)
            if appreciation:
                codes.update(appreciation.periodes.keys())
        
        for code in codes:
            moyennes = []
            for bulletin in bulletins:
                appreciation = bulletin.get_matiere(matiere_name)
                if not appreciation:
                    continue
                periode = appreciation.get_periode(code)
                if periode and periode.moyenne is not None:
                    moyennes.append(periode.moyenne)
            
            min_val = min(moyennes) if moyennes else None
            max_val = max(moyennes) if moyennes else None
            
            for bulletin in bulletins:
                appreciation = bulletin.get_matiere(matiere_name)
                if not appreciation:
                    continue
                periode = appreciation.get_periode(code)
                if periode:
                    periode.moyenne_min = min_val
                    periode.moyenne_max = max_val


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
            for code, periode in appreciation.periodes.items():
                # Vérifier que les moyennes sont dans une plage raisonnable
                if periode.moyenne is not None and (periode.moyenne < 0 or periode.moyenne > 20):
                    warnings.append(
                        f"{nom_eleve} - {matiere_name} {code}: Moyenne suspecte ({periode.moyenne})"
                    )
                
                # Vérifier que les heures d'absence ne sont pas excessives
                heures = absence_to_hours(periode.heures_absence)
                if heures is not None and heures > 100:  # Plus de 100h semble suspect
                    warnings.append(
                        f"{nom_eleve} - {matiere_name} {code}: Heures d'absence élevées ({periode.heures_absence})"
                    )
    
    return warnings 