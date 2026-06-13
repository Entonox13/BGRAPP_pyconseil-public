#!/usr/bin/env python3
"""
Utilitaires liés aux semestres (S1/S2) pour la préparation des conseils.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping, Optional, Sequence


class Semester(str, Enum):
    """Enumération des semestres supportés par l'application."""

    S1 = "S1"
    S2 = "S2"

    @property
    def label(self) -> str:
        """Retourne un libellé humain lisible."""
        return "Semestre 1" if self is Semester.S1 else "Semestre 2"


def _normalize_headers(headers: Iterable[str]) -> Sequence[str]:
    """Nettoie et normalise les en-têtes pour la détection."""
    normalized = []
    for header in headers:
        if not header:
            continue
        normalized.append(header.strip().lower())
    return normalized


def detect_semester_from_headers(headers: Iterable[str]) -> Semester:
    """
    Détecte le semestre en se basant sur les en-têtes d'un CSV matière.

    Args:
        headers: Iterable des noms de colonnes.

    Returns:
        Semester: S1 par défaut si aucun indice clair ne ressort,
                  sinon S2 lorsque des colonnes spécifiques sont présentes.
    """
    normalized = _normalize_headers(headers)
    if not normalized:
        return Semester.S2

    has_moy_s2 = any("moy" in h and "s2" in h for h in normalized)
    has_rappel_s1 = any("rappel de la période précédente" in h for h in normalized)

    if has_moy_s2 or has_rappel_s1:
        return Semester.S2

    has_moy_s1 = any("moy" in h and "s1" in h for h in normalized)
    if has_moy_s1:
        return Semester.S1

    return Semester.S2


def detect_semester_from_matiere_data(matiere_data: Sequence[Mapping[str, object]]) -> Semester:
    """
    Détecte le semestre à partir d'un jeu de données matière.

    Args:
        matiere_data: Lignes du CSV déjà converties en dictionnaires.

    Returns:
        Semester: Résultat de la détection.
    """
    if not matiere_data:
        return Semester.S2

    first_row = matiere_data[0]
    return detect_semester_from_headers(first_row.keys())


def semester_from_metadata(metadata: Optional[Mapping[str, object]]) -> Optional[Semester]:
    """
    Restaure un semestre depuis les métadonnées JSON.

    Args:
        metadata: Bloc `_metadata` extrait du fichier JSON.

    Returns:
        Semester ou None si absent.
    """
    if not metadata:
        return None

    semester_value = metadata.get("semester")
    if isinstance(semester_value, str):
        normalized = semester_value.strip().upper()
        if normalized in Semester.__members__:
            return Semester[normalized]

    return None


def infer_semester_from_bulletins_data(
    bulletins_data: Sequence[Mapping[str, Any]]
) -> Semester:
    """
    Déduit le semestre à partir des données JSON des bulletins.

    Args:
        bulletins_data: Liste de bulletins tels que stockés dans le JSON.

    Returns:
        Semester: Semestre le plus probable (S2 par défaut).
    """
    for bulletin_data in bulletins_data:
        matieres = bulletin_data.get("Matieres") if isinstance(bulletin_data, Mapping) else None
        if not isinstance(matieres, Mapping):
            continue
        for appreciation in matieres.values():
            if not isinstance(appreciation, Mapping):
                continue
            if appreciation.get("MoyenneS2") is not None or appreciation.get("AppreciationS2"):
                return Semester.S2
            if appreciation.get("MoyenneS1") is not None or appreciation.get("AppreciationS1"):
                return Semester.S1

    return Semester.S2

