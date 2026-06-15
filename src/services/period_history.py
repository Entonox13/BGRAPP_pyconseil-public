#!/usr/bin/env python3
"""
Gestion de l'historique des periodes reparti sur plusieurs fichiers JSON.

Contrairement a l'ancien modele ou un unique fichier accumulait toutes les
periodes (S1/S2 ou T1/T2/T3), chaque periode est desormais sauvegardee dans
son propre fichier JSON ne contenant que cette periode. Les autres periodes
sont referencees via des "liens" :

- auto-decouverte des fichiers freres du meme dossier (lecture de leurs
  metadonnees `current_period`) ;
- ajout/retrait manuel memorise dans le bloc `_metadata` du fichier courant
  (`period_links`, `period_link_overrides` et `period_links_excluded`).

Au chargement, les periodes liees sont fusionnees **en lecture seule** dans
une copie des bulletins courants afin de reconstruire la vue multi-periodes
(colonnes Moy./Abs./Ret., evolution, appreciations) sans jamais modifier le
fichier de la periode courante sur le disque.
"""

from __future__ import annotations

import copy
import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

# Import conditionnel pour gerer les imports relatifs
try:
    from ..models.bulletin import Bulletin
    from ..utils.semester import (
        PERIOD_CODES,
        Period,
        PeriodSystem,
        period_from_metadata,
        infer_period_from_bulletins_data,
        period_from_directory_name,
    )
    from .json_generator import load_bulletins_from_json
except ImportError:
    from models.bulletin import Bulletin
    from utils.semester import (
        PERIOD_CODES,
        Period,
        PeriodSystem,
        period_from_metadata,
        infer_period_from_bulletins_data,
        period_from_directory_name,
    )
    from services.json_generator import load_bulletins_from_json


# ---------------------------------------------------------------------------
# Lecture brute
# ---------------------------------------------------------------------------
def read_payload(path: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Lit un fichier JSON et separe le bloc `_metadata` des bulletins.

    Args:
        path: Chemin du fichier JSON.

    Returns:
        Tuple (metadata, bulletins_data). Les deux peuvent etre vides si le
        fichier est illisible ou absent.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}, []

    if not isinstance(raw_data, list):
        return {}, []

    metadata: Dict[str, Any] = {}
    data = raw_data
    if raw_data and isinstance(raw_data[0], dict) and '_metadata' in raw_data[0]:
        metadata = raw_data[0].get('_metadata') or {}
        data = raw_data[1:]

    bulletins_data = [item for item in data if isinstance(item, dict)]
    return metadata, bulletins_data


def update_file_metadata(json_path: str, metadata: Mapping[str, Any]) -> None:
    """
    Reecrit le bloc `_metadata` d'un fichier JSON sans toucher aux bulletins.

    Args:
        json_path: Chemin du fichier JSON a modifier.
        metadata: Nouveau contenu du bloc `_metadata`.
    """
    _existing_meta, bulletins_data = read_payload(json_path)
    payload: List[Any] = [{"_metadata": dict(metadata)}]
    payload.extend(bulletins_data)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


_FILENAME_PERIOD_RE = re.compile(
    r"(?:^|[_\-.])([ST][123])(?:[_\-.]|\.json$)",
    re.IGNORECASE,
)


def period_code_from_filename(path: str) -> Optional[str]:
    """Deduit un code de periode depuis le nom du fichier (ex. output_T2.json)."""
    name = os.path.basename(path)
    match = _FILENAME_PERIOD_RE.search(name)
    if match:
        return match.group(1).upper()
    return None


def period_code_of_file(path: str) -> Optional[str]:
    """
    Determine le code de periode (S1/S2/T1/T2/T3) d'un fichier JSON.

    Cherche dans les metadonnees, le nom du fichier, le dossier parent,
    puis le contenu des bulletins.

    Args:
        path: Chemin du fichier JSON.

    Returns:
        Code de periode ou None si indeterminable.
    """
    metadata, data = read_payload(path)
    period = period_from_metadata(metadata)
    if period is not None:
        return period.value
    from_name = period_code_from_filename(path)
    if from_name:
        return from_name
    from_dir = period_from_directory_name(os.path.dirname(path))
    if from_dir is not None:
        return from_dir.value
    if data:
        period = infer_period_from_bulletins_data(data)
        if period is not None:
            return period.value
    return None


def suggested_period_code_for_link(file_path: str) -> Optional[str]:
    """
    Suggestion pour l'attribution manuelle : nom de fichier prioritaire sur le contenu.
    """
    from_name = period_code_from_filename(file_path)
    if from_name:
        return from_name
    return period_code_of_file(file_path)


def _period_link_override_key(json_path: str, file_path: str) -> str:
    """Cle storable dans period_link_overrides (chemin relatif au JSON courant)."""
    return _to_storable_path(json_path, file_path)


def effective_period_code_for_file(
    file_path: str,
    metadata: Optional[Mapping[str, Any]] = None,
    json_path: Optional[str] = None,
) -> Optional[str]:
    """
    Periode effective d'un fichier lie : surcharge manuelle puis detection auto.
    """
    overrides = (metadata or {}).get("period_link_overrides") or {}
    if json_path:
        rel = _period_link_override_key(json_path, file_path)
        if rel in overrides:
            return str(overrides[rel]).strip().upper()
        base = os.path.basename(file_path)
        if base in overrides:
            return str(overrides[base]).strip().upper()
    return period_code_of_file(file_path)


# ---------------------------------------------------------------------------
# Nommage
# ---------------------------------------------------------------------------
def default_period_filename(directory: Optional[str], code: str, base: str = "output") -> str:
    """
    Propose un nom de fichier par defaut pour une periode donnee.

    Convention : `<base>_<CODE>.json` (ex: `output_T3.json`).

    Args:
        directory: Dossier cible (non utilise pour le calcul du nom, conserve
            pour permettre de futures strategies anti-collision).
        code: Code de la periode (ex: "T3").
        base: Prefixe du nom de fichier.

    Returns:
        Nom de fichier (basename) suggere.
    """
    code = (code or "").strip().upper()
    if not code:
        return f"{base}.json"
    return f"{base}_{code}.json"


# ---------------------------------------------------------------------------
# Decouverte / resolution des liens
# ---------------------------------------------------------------------------
def discover_sibling_period_files(
    json_path: str,
    current_code: str,
    metadata: Optional[Mapping[str, Any]] = None,
) -> Dict[str, str]:
    """
    Scanne les fichiers JSON freres du meme dossier et retourne ceux
    correspondant a une periode differente de la periode courante.

    Les surcharges `period_link_overrides` sont appliquees.

    Args:
        json_path: Chemin du fichier JSON courant.
        current_code: Code de la periode courante (exclue du resultat).
        metadata: Bloc `_metadata` du fichier courant (surcharges manuelles).

    Returns:
        Dictionnaire {code_periode: chemin_absolu}.
    """
    result: Dict[str, str] = {}
    if not json_path:
        return result

    directory = os.path.dirname(os.path.abspath(json_path))
    if not os.path.isdir(directory):
        return result

    current_abs = os.path.abspath(json_path)
    current_code = (current_code or "").strip().upper()

    for sibling in sorted(Path(directory).glob("*.json")):
        sibling_abs = os.path.abspath(str(sibling))
        if sibling_abs == current_abs:
            continue
        code = effective_period_code_for_file(sibling_abs, metadata, json_path)
        if not code or code == current_code:
            continue
        # En cas de doublon pour une meme periode, on garde le premier (tri).
        result.setdefault(code, sibling_abs)

    return result


def _resolve_path(json_path: str, stored_path: str) -> Optional[str]:
    """Resout un chemin (relatif au dossier du JSON courant ou absolu)."""
    if not stored_path:
        return None
    if os.path.isabs(stored_path):
        resolved = stored_path
    else:
        base_dir = os.path.dirname(os.path.abspath(json_path))
        resolved = os.path.abspath(os.path.join(base_dir, stored_path))
    return resolved if os.path.exists(resolved) else None


def _to_storable_path(json_path: str, file_path: str) -> str:
    """Convertit un chemin absolu en chemin relatif au JSON courant si possible."""
    base_dir = os.path.dirname(os.path.abspath(json_path))
    abs_path = os.path.abspath(file_path)
    try:
        # Chemin relatif uniquement s'il reste dans une arborescence raisonnable
        relative = os.path.relpath(abs_path, base_dir)
        if not relative.startswith(os.pardir + os.sep) and relative != os.pardir:
            return relative
    except ValueError:
        # Lecteurs differents (Windows) : conserver l'absolu
        pass
    return abs_path


def resolve_period_links(
    json_path: str,
    metadata: Optional[Mapping[str, Any]],
    current_code: str,
) -> Dict[str, str]:
    """
    Calcule l'ensemble effectif des fichiers de periodes liees.

    Effectif = auto-decouverte (moins exclusions) puis surcharge par les liens
    manuels memorises dans la metadata.

    Args:
        json_path: Chemin du fichier JSON courant.
        metadata: Bloc `_metadata` du fichier courant (peut etre None).
        current_code: Code de la periode courante.

    Returns:
        Dictionnaire {code_periode: chemin_absolu} (fichiers existants seulement).
    """
    metadata = metadata or {}
    current_code = (current_code or "").strip().upper()

    auto = discover_sibling_period_files(json_path, current_code, metadata)

    excluded = set()
    for code in metadata.get("period_links_excluded", []) or []:
        if isinstance(code, str):
            excluded.add(code.strip().upper())

    effective: Dict[str, str] = {
        code: path for code, path in auto.items() if code not in excluded
    }

    manual = metadata.get("period_links", {}) or {}
    if isinstance(manual, Mapping):
        for code, stored in manual.items():
            if not isinstance(code, str) or not isinstance(stored, str):
                continue
            code = code.strip().upper()
            if code == current_code:
                continue
            resolved = _resolve_path(json_path, stored)
            if resolved:
                effective[code] = resolved

    return effective


def _set_period_link_override(
    metadata: Dict[str, Any],
    json_path: str,
    file_path: str,
    period_code: str,
) -> None:
    """Enregistre la periode choisie manuellement pour un fichier lie."""
    store_key = _period_link_override_key(json_path, file_path)
    overrides = metadata.get("period_link_overrides")
    if not isinstance(overrides, dict):
        overrides = {}
    overrides[store_key] = period_code.strip().upper()
    metadata["period_link_overrides"] = overrides


def _clear_manual_link_for_path(
    metadata: Dict[str, Any],
    json_path: str,
    file_path: str,
) -> None:
    """Retire toute entree period_links pointant vers le meme fichier."""
    abs_target = os.path.normpath(os.path.abspath(file_path))
    links = metadata.get("period_links")
    if not isinstance(links, dict):
        return
    to_drop = []
    for code, stored in links.items():
        resolved = _resolve_path(json_path, stored)
        if resolved and os.path.normpath(resolved) == abs_target:
            to_drop.append(code)
    for code in to_drop:
        del links[code]
    if links:
        metadata["period_links"] = links
    else:
        metadata.pop("period_links", None)


def _remove_excluded_code(metadata: Dict[str, Any], code: str) -> None:
    """Retire un code de la liste d'exclusions auto."""
    excluded = [
        c for c in (metadata.get("period_links_excluded") or [])
        if isinstance(c, str) and c.strip().upper() != code
    ]
    if excluded:
        metadata["period_links_excluded"] = excluded
    else:
        metadata.pop("period_links_excluded", None)


def add_period_link(
    metadata: Dict[str, Any],
    json_path: str,
    file_path: str,
    period_code: Optional[str] = None,
) -> Optional[str]:
    """
    Enregistre un lien manuel vers un fichier de periode dans la metadata.

    Si `period_code` est fourni, il est utilise a la place de la detection auto
    et memorise dans `period_link_overrides`.

    Args:
        metadata: Bloc `_metadata` a modifier sur place.
        json_path: Chemin du fichier JSON courant.
        file_path: Chemin du fichier de periode a lier.
        period_code: Code de periode impose par l'utilisateur (optionnel).

    Returns:
        Le code de periode associe, ou None si indeterminable.
    """
    if period_code:
        code = period_code.strip().upper()
        if code not in PERIOD_CODES:
            return None
        _set_period_link_override(metadata, json_path, file_path, code)
    else:
        code = effective_period_code_for_file(file_path, metadata, json_path)
    if not code:
        return None

    store = _to_storable_path(json_path, file_path)
    _clear_manual_link_for_path(metadata, json_path, file_path)
    links = metadata.get("period_links")
    if not isinstance(links, dict):
        links = {}
    links[code] = store
    metadata["period_links"] = links
    _remove_excluded_code(metadata, code)
    return code


def set_period_link_code(
    metadata: Dict[str, Any],
    json_path: str,
    file_path: str,
    period_code: str,
    current_code: str,
) -> Optional[str]:
    """
    Reattribue un fichier lie (auto ou manuel) a une autre periode.
    """
    code = (period_code or "").strip().upper()
    if code not in PERIOD_CODES:
        return None
    if code == (current_code or "").strip().upper():
        raise ValueError("La periode liee ne peut pas etre la periode courante.")

    _set_period_link_override(metadata, json_path, file_path, code)
    store = _to_storable_path(json_path, file_path)
    _clear_manual_link_for_path(metadata, json_path, file_path)
    links = metadata.get("period_links")
    if not isinstance(links, dict):
        links = {}
    links[code] = store
    metadata["period_links"] = links
    _remove_excluded_code(metadata, code)

    auto_detected = period_code_of_file(file_path)
    if auto_detected and auto_detected != code:
        excluded = list(metadata.get("period_links_excluded") or [])
        normalized = {c.strip().upper() for c in excluded if isinstance(c, str)}
        if auto_detected not in normalized:
            excluded.append(auto_detected)
            metadata["period_links_excluded"] = excluded

    return code


def remove_period_link(
    metadata: Dict[str, Any],
    json_path: str,
    code: str,
    current_code: str,
) -> None:
    """
    Retire un lien (manuel ou auto-decouvert) pour une periode donnee.

    Si le lien etait manuel il est simplement supprime ; s'il provenait de
    l'auto-decouverte, le code est ajoute aux exclusions.

    Args:
        metadata: Bloc `_metadata` a modifier sur place.
        json_path: Chemin du fichier JSON courant.
        code: Code de periode a retirer.
        current_code: Code de la periode courante (pour la decouverte).
    """
    code = (code or "").strip().upper()
    if not code:
        return

    links = metadata.get("period_links")
    if isinstance(links, dict) and code in links:
        del links[code]
        if links:
            metadata["period_links"] = links
        else:
            metadata.pop("period_links", None)

    # Si la periode reste auto-decouverte dans le dossier, l'exclure
    # explicitement pour qu'elle disparaisse reellement de l'ensemble effectif.
    auto = discover_sibling_period_files(json_path, current_code, metadata)
    if code in auto:
        excluded = list(metadata.get("period_links_excluded") or [])
        normalized = {c.strip().upper() for c in excluded if isinstance(c, str)}
        if code not in normalized:
            excluded.append(code)
        metadata["period_links_excluded"] = excluded


# ---------------------------------------------------------------------------
# Chargement et fusion (lecture seule)
# ---------------------------------------------------------------------------
def native_period_from_file_content(path: str) -> Optional[str]:
    """Deduit la periode uniquement du contenu des bulletins (pas meta/nom)."""
    _, data = read_payload(path)
    if not data:
        return None
    period = infer_period_from_bulletins_data(data)
    return period.value if period else None


def primary_period_in_bulletins(bulletins: List[Bulletin]) -> Optional[str]:
    """Periode la plus frequente dans les donnees matieres."""
    from collections import Counter

    counter: Counter[str] = Counter()
    for bulletin in bulletins:
        for matiere in bulletin.matieres.values():
            for code in matiere.periodes:
                counter[code] += 1
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def remap_bulletins_period_code(
    bulletins: List[Bulletin],
    from_code: str,
    to_code: str,
) -> List[Bulletin]:
    """
    Reproduit les donnees d'une periode sous un autre code (copie profonde).

    Utilise lorsqu'un fichier lie est attribue manuellement a une periode
    dont les cles internes ne correspondent pas (ex. contenu S2 lie en T2).
    """
    from_code = (from_code or "").strip().upper()
    to_code = (to_code or "").strip().upper()
    if not from_code or from_code == to_code:
        return bulletins

    result = copy.deepcopy(bulletins)
    for bulletin in result:
        if from_code in bulletin.appreciations_generales:
            texte = bulletin.appreciations_generales.pop(from_code)
            bulletin.appreciations_generales.setdefault(to_code, texte)
        for matiere in bulletin.matieres.values():
            if from_code in matiere.periodes:
                periode = matiere.periodes.pop(from_code)
                matiere.periodes.setdefault(to_code, periode)
    return result


def normalize_linked_bulletins(
    bulletins: List[Bulletin],
    assigned_code: str,
    file_path: str,
) -> List[Bulletin]:
    """
    Aligne les cles de periode d'un fichier lie sur le code attribue.

    Si le JSON contient des donnees S2 mais est lie en T2, les champs S2
    sont recopies sous T2 pour que la fusion affiche les bonnes colonnes.
    """
    assigned_code = (assigned_code or "").strip().upper()
    if not assigned_code or not bulletins:
        return bulletins

    has_assigned_data = any(
        assigned_code in matiere.periodes
        for bulletin in bulletins
        for matiere in bulletin.matieres.values()
    )
    if has_assigned_data:
        return bulletins

    native = native_period_from_file_content(file_path)
    if not native:
        native = primary_period_in_bulletins(bulletins)
    if not native or native == assigned_code:
        return bulletins

    return remap_bulletins_period_code(bulletins, native, assigned_code)


def load_history_bulletins(links: Mapping[str, str]) -> Dict[str, List[Bulletin]]:
    """
    Charge les bulletins de chaque fichier de periode lie.

    Les periodes internes sont normalisees vers le code attribue dans les liens
    lorsque le contenu utilise un autre suffixe (ex. S2 dans un fichier lie T2).

    Args:
        links: Dictionnaire {code_periode: chemin}.

    Returns:
        Dictionnaire {code_periode: liste de Bulletin} (les fichiers illisibles
        sont ignores).
    """
    history: Dict[str, List[Bulletin]] = {}
    for code, path in links.items():
        try:
            bulletins = load_bulletins_from_json(path)
            history[code] = normalize_linked_bulletins(bulletins, code, path)
        except Exception:
            continue
    return history


def _bulletin_key(bulletin: Bulletin) -> str:
    return f"{bulletin.eleve.nom} {bulletin.eleve.prenom}"


# Abréviations Pronote / anciens exports -> clé canonique des noms normalisés
_MATIERE_ALIAS_TARGETS = {
    "eps": "educationphysiquesportive",
    "techno": "technologie",
    "sciencesdelavieetdelaterre": "sciencesvieterre",
}


def _matiere_canonical_key(name: str) -> str:
    """Clé de rapprochement pour fusionner des libellés de matières proches."""
    if not name:
        return ""
    normalized = unicodedata.normalize("NFD", str(name))
    ascii_name = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
    key = re.sub(r"[^a-z0-9]", "", ascii_name.lower())
    return _MATIERE_ALIAS_TARGETS.get(key, key)


def _resolve_matiere_name(bulletin: Bulletin, other_name: str) -> Optional[str]:
    """
    Retrouve le nom de matière équivalent déjà présent dans `bulletin`.

    Permet de fusionner « Anglais LV1 » (ancien export) avec « AnglaisLV1 ».
    """
    if bulletin.get_matiere(other_name) is not None:
        return other_name
    target = _matiere_canonical_key(other_name)
    for name in bulletin.matieres:
        if _matiere_canonical_key(name) == target:
            return name
    return None


def merge_periods_into_bulletins(
    bulletins: List[Bulletin],
    other_bulletins: List[Bulletin],
    current_code: str,
) -> None:
    """
    Fusionne (sur place) les periodes d'une autre source dans `bulletins`.

    Version generalisee de `main_processor.merge_history_into_bulletins`, sans
    filtrage par systeme : toutes les periodes autres que `current_code` sont
    reportees lorsqu'elles sont absentes. La periode courante n'est jamais
    ecrasee.

    Args:
        bulletins: Bulletins de la periode courante (modifies sur place).
        other_bulletins: Bulletins charges depuis un fichier de periode lie.
        current_code: Code de la periode courante (protege de l'ecrasement).
    """
    if not other_bulletins:
        return

    current_code = (current_code or "").strip().upper()
    other_index = {_bulletin_key(b): b for b in other_bulletins}

    for bulletin in bulletins:
        other = other_index.get(_bulletin_key(bulletin))
        if not other:
            continue

        # Appreciations generales des autres periodes
        for code, texte in other.appreciations_generales.items():
            if code == current_code:
                continue
            if code not in bulletin.appreciations_generales:
                bulletin.appreciations_generales[code] = texte

        # Donnees par matiere / periode
        for other_name, other_app in other.matieres.items():
            resolved_name = _resolve_matiere_name(bulletin, other_name)
            if resolved_name is None:
                # Matiere absente de la periode courante : la cloner en ne
                # gardant que les periodes autres que la periode courante.
                clone = copy.deepcopy(other_app)
                clone.periodes = {
                    code: periode
                    for code, periode in clone.periodes.items()
                    if code != current_code
                }
                if clone.periodes:
                    bulletin.add_matiere(clone)
                continue

            current_app = bulletin.get_matiere(resolved_name)
            if current_app is None:
                continue
            for code, periode in other_app.periodes.items():
                if code == current_code:
                    continue
                if code not in current_app.periodes:
                    current_app.periodes[code] = copy.deepcopy(periode)


def normalize_trimestre_general_appreciations(bulletin: Bulletin) -> None:
    """
    Expose les appreciations S1/S2 sous T1/T2 pour l'affichage trimestre.

    Utile pour les JSON generes avec d'anciennes colonnes source.xlsx
    (AppreciationGeneraleS1/S2) ou des fichiers lies encore en suffixe semestre.
    """
    if not bulletin.get_appreciation_generale("T1"):
        s1 = bulletin.get_appreciation_generale("S1")
        if s1:
            bulletin.set_appreciation_generale("T1", s1)
    if not bulletin.get_appreciation_generale("T2"):
        s2 = bulletin.get_appreciation_generale("S2")
        if s2:
            bulletin.set_appreciation_generale("T2", s2)
    # Eviter les doublons S1/S2 + T1/T2 dans la vue trimestre
    bulletin.appreciations_generales.pop("S1", None)
    bulletin.appreciations_generales.pop("S2", None)


def build_display_bulletins(
    current_bulletins: List[Bulletin],
    history_by_code: Mapping[str, List[Bulletin]],
    current_code: str,
) -> List[Bulletin]:
    """
    Construit une liste de bulletins enrichie des periodes liees, destinee a
    l'affichage en lecture seule.

    Les bulletins courants ne sont pas modifies : une copie profonde est
    realisee avant fusion.

    Args:
        current_bulletins: Bulletins de la periode courante.
        history_by_code: Bulletins des periodes liees (par code).
        current_code: Code de la periode courante.

    Returns:
        Nouvelle liste de Bulletin fusionnes pour l'affichage.
    """
    display = copy.deepcopy(current_bulletins)
    for _code, other_bulletins in history_by_code.items():
        merge_periods_into_bulletins(display, other_bulletins, current_code)
    current_period = Period.from_code(current_code)
    if current_period and current_period.system == PeriodSystem.TRIMESTRE:
        for bulletin in display:
            normalize_trimestre_general_appreciations(bulletin)
    return display
