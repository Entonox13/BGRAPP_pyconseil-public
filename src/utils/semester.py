#!/usr/bin/env python3
"""
Utilitaires liés aux périodes scolaires pour la préparation des conseils.

Le logiciel peut fonctionner soit en mode semestre (S1, S2),
soit en mode trimestre (T1, T2, T3). La notion de `Period` généralise
l'ancienne notion de `Semester` (qui reste disponible en alias).
"""

from __future__ import annotations

import os
import re
from collections import Counter
from enum import Enum
from typing import Any, Iterable, List, Mapping, Optional, Sequence


class PeriodSystem(str, Enum):
    """Système d'organisation de l'année scolaire."""

    SEMESTRE = "SEMESTRE"
    TRIMESTRE = "TRIMESTRE"

    @property
    def label(self) -> str:
        return "Semestre" if self is PeriodSystem.SEMESTRE else "Trimestre"


# Définition centralisée des périodes (code -> métadonnées)
_PERIOD_META = {
    "S1": (PeriodSystem.SEMESTRE, 1, "Semestre 1"),
    "S2": (PeriodSystem.SEMESTRE, 2, "Semestre 2"),
    "T1": (PeriodSystem.TRIMESTRE, 1, "Trimestre 1"),
    "T2": (PeriodSystem.TRIMESTRE, 2, "Trimestre 2"),
    "T3": (PeriodSystem.TRIMESTRE, 3, "Trimestre 3"),
}

PERIOD_CODES = ("S1", "S2", "T1", "T2", "T3")


class Period(str, Enum):
    """Période scolaire supportée (semestre ou trimestre)."""

    S1 = "S1"
    S2 = "S2"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"

    @property
    def system(self) -> PeriodSystem:
        """Retourne le système (semestre/trimestre) auquel appartient la période."""
        return _PERIOD_META[self.value][0]

    @property
    def order(self) -> int:
        """Retourne l'ordre chronologique de la période dans son système."""
        return _PERIOD_META[self.value][1]

    @property
    def label(self) -> str:
        """Retourne un libellé humain lisible."""
        return _PERIOD_META[self.value][2]

    @property
    def previous(self) -> Optional["Period"]:
        """Retourne la période précédente du même système, si elle existe."""
        for candidate in periods_for_system(self.system):
            if candidate.order == self.order - 1:
                return candidate
        return None

    @classmethod
    def from_code(cls, code: Optional[str]) -> Optional["Period"]:
        """Crée une période depuis un code texte (ex: 'T3', 's1')."""
        if not isinstance(code, str):
            return None
        normalized = code.strip().upper()
        if normalized in cls.__members__:
            return cls[normalized]
        return None


# Alias de rétro-compatibilité : l'ancien code utilise `Semester`.
# `Semester.S1` / `Semester.S2` restent valides ; les trimestres sont
# désormais accessibles via le même type.
Semester = Period


def periods_for_system(system: PeriodSystem) -> List[Period]:
    """Retourne la liste ordonnée des périodes d'un système donné."""
    periods = [Period[code] for code, meta in _PERIOD_META.items() if meta[0] == system]
    return sorted(periods, key=lambda p: p.order)


def _normalize_headers(headers: Iterable[str]) -> Sequence[str]:
    """Nettoie et normalise les en-têtes pour la détection."""
    normalized = []
    for header in headers:
        if not header:
            continue
        normalized.append(str(header).strip().lower())
    return normalized


def detect_period_from_headers(headers: Iterable[str]) -> Period:
    """
    Détecte la période courante à partir des en-têtes d'un CSV matière.

    Recherche un motif du type `Moy. T3`, `Moy. S1`, etc.
    En l'absence d'indice clair, retombe sur `Period.S2` par défaut
    (comportement historique).

    Args:
        headers: Iterable des noms de colonnes.

    Returns:
        Period: Période détectée.
    """
    normalized = _normalize_headers(headers)
    if not normalized:
        return Period.S2

    for header in normalized:
        match = re.search(r"moy\.?\s*(t[123]|s[12])\b", header)
        if match:
            period = Period.from_code(match.group(1))
            if period:
                return period

    # Présence d'un rappel de période précédente => semestre courant = S2
    if any("rappel de la période précédente" in h for h in normalized):
        return Period.S2

    return Period.S2


def detect_period_from_matiere_data(matiere_data: Sequence[Mapping[str, object]]) -> Period:
    """
    Détecte la période à partir d'un jeu de données matière.

    Args:
        matiere_data: Lignes du CSV déjà converties en dictionnaires.

    Returns:
        Period: Résultat de la détection.
    """
    if not matiere_data:
        return Period.S2

    first_row = matiere_data[0]
    return detect_period_from_headers(first_row.keys())


def period_from_metadata(metadata: Optional[Mapping[str, object]]) -> Optional[Period]:
    """
    Restaure une période depuis les métadonnées JSON.

    Cherche d'abord `current_period`, puis l'ancien champ `semester`.

    Args:
        metadata: Bloc `_metadata` extrait du fichier JSON.

    Returns:
        Period ou None si absent.
    """
    if not metadata:
        return None

    for key in ("current_period", "semester"):
        value = metadata.get(key)
        if isinstance(value, str):
            period = Period.from_code(value)
            if period:
                return period

    return None


def period_system_from_metadata(metadata: Optional[Mapping[str, object]]) -> Optional[PeriodSystem]:
    """Restaure le système de période depuis les métadonnées JSON."""
    if not metadata:
        return None

    value = metadata.get("period_system")
    if isinstance(value, str):
        normalized = value.strip().upper()
        if normalized in PeriodSystem.__members__:
            return PeriodSystem[normalized]

    # Déduction depuis la période courante si disponible
    period = period_from_metadata(metadata)
    if period:
        return period.system

    return None


def infer_period_from_bulletins_data(
    bulletins_data: Sequence[Mapping[str, Any]]
) -> Period:
    """
    Déduit la période courante à partir des données JSON des bulletins.

    Recherche les codes de période présents (S1/S2/T1/T2/T3) dans les
    clés des matières et retourne la plus avancée.

    Args:
        bulletins_data: Liste de bulletins tels que stockés dans le JSON.

    Returns:
        Period: Période la plus probable (S2 par défaut).
    """
    code_counts: Counter = Counter()
    pattern = re.compile(r"(?:Moyenne|Appreciation|HeuresAbsence|Retards)(S1|S2|T1|T2|T3)")

    for bulletin_data in bulletins_data:
        if not isinstance(bulletin_data, Mapping):
            continue
        # Appréciations générales par période
        for key in bulletin_data.keys():
            match = re.match(r"AppreciationGenerale(S1|S2|T1|T2|T3)$", str(key))
            if match:
                code_counts[match.group(1)] += 1
        matieres = bulletin_data.get("Matieres")
        if not isinstance(matieres, Mapping):
            continue
        for appreciation in matieres.values():
            if not isinstance(appreciation, Mapping):
                continue
            for key in appreciation.keys():
                match = pattern.match(str(key))
                if match:
                    code_counts[match.group(1)] += 1

    if not code_counts:
        return Period.S2

    # Déterminer le système réellement dominant (le plus d'occurrences de
    # champs), au lieu de privilégier arbitrairement le trimestre : sinon des
    # données semestre noyées dans une structure trimestre seraient masquées.
    system_counts: Counter = Counter()
    for code, count in code_counts.items():
        system_counts[Period[code].system] += count

    # Égalité => semestre (comportement historique par défaut).
    dominant_system = max(
        system_counts,
        key=lambda s: (system_counts[s], s is PeriodSystem.SEMESTRE)
    )

    # Période la plus avancée présente dans le système dominant.
    candidates = [
        Period[code] for code in code_counts if Period[code].system == dominant_system
    ]
    return max(candidates, key=lambda p: p.order)


def period_from_directory_name(path_or_name: Optional[str]) -> Optional[Period]:
    """
    Déduit la période à partir du nom du dossier contenant les CSV.

    Exemples : '.../PP/T3' -> T3, 'S1' -> S1, 'Trimestre 2 (T2)' -> T2.

    Args:
        path_or_name: Chemin complet ou simple nom de dossier.

    Returns:
        Period si un code (S1/S2/T1/T2/T3) est reconnu, sinon None.
    """
    if not path_or_name:
        return None

    name = os.path.basename(os.path.normpath(str(path_or_name)))

    # 1. Le nom du dossier est exactement un code de période
    direct = Period.from_code(name)
    if direct:
        return direct

    # 2. Le nom contient un code de période isolé (ex: "Trimestre 2 (T2)")
    match = re.search(r"\b([ST][123])\b", name.upper())
    if match:
        return Period.from_code(match.group(1))

    return None


def available_periods_from_bulletins_data(
    bulletins_data: Sequence[Mapping[str, Any]]
) -> List[Period]:
    """
    Liste ordonnée des périodes réellement présentes dans les données JSON.

    Contrairement à `infer_period_from_bulletins_data` qui ne retourne qu'une
    seule période (la plus probable), cette fonction retourne toutes les
    périodes détectées afin d'alimenter un sélecteur manuel.

    Args:
        bulletins_data: Liste de bulletins tels que stockés dans le JSON.

    Returns:
        List[Period]: Périodes présentes, dans l'ordre canonique S1,S2,T1,T2,T3.
    """
    present = set()
    pattern = re.compile(r"(?:Moyenne|Appreciation|HeuresAbsence|Retards)(S1|S2|T1|T2|T3)")

    for bulletin_data in bulletins_data:
        if not isinstance(bulletin_data, Mapping):
            continue
        for key in bulletin_data.keys():
            match = re.match(r"AppreciationGenerale(S1|S2|T1|T2|T3)$", str(key))
            if match:
                present.add(match.group(1))
        matieres = bulletin_data.get("Matieres")
        if not isinstance(matieres, Mapping):
            continue
        for appreciation in matieres.values():
            if not isinstance(appreciation, Mapping):
                continue
            for key in appreciation.keys():
                match = pattern.match(str(key))
                if match:
                    present.add(match.group(1))

    canonical_order = ["S1", "S2", "T1", "T2", "T3"]
    return [Period[code] for code in canonical_order if code in present]


# ---------------------------------------------------------------------------
# Rétro-compatibilité : anciennes fonctions basées sur "semester".
# Elles délèguent désormais aux fonctions génériques ci-dessus.
# ---------------------------------------------------------------------------

def detect_semester_from_headers(headers: Iterable[str]) -> Period:
    """Alias rétro-compatible de `detect_period_from_headers`."""
    return detect_period_from_headers(headers)


def detect_semester_from_matiere_data(matiere_data: Sequence[Mapping[str, object]]) -> Period:
    """Alias rétro-compatible de `detect_period_from_matiere_data`."""
    return detect_period_from_matiere_data(matiere_data)


def semester_from_metadata(metadata: Optional[Mapping[str, object]]) -> Optional[Period]:
    """Alias rétro-compatible de `period_from_metadata`."""
    return period_from_metadata(metadata)


def infer_semester_from_bulletins_data(
    bulletins_data: Sequence[Mapping[str, Any]]
) -> Period:
    """Alias rétro-compatible de `infer_period_from_bulletins_data`."""
    return infer_period_from_bulletins_data(bulletins_data)
