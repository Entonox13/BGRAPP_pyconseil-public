#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitaire de renommage des fichiers CSV d'un dossier source.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Tuple

from .file_reader import get_csv_files_in_directory


class CsvRenamerError(Exception):
    """Erreur lors de la préparation ou l'application des renommages."""


def display_name_without_extension(filename: str) -> str:
    """Retourne le nom affiché sans l'extension .csv."""
    return Path(filename).stem


def normalize_csv_filename(name: str) -> str:
    """
    Normalise un nom de fichier CSV (sans chemin).

    Ajoute l'extension .csv si absente.
    """
    cleaned = name.strip()
    if not cleaned:
        return cleaned
    if cleaned.lower().endswith(".csv"):
        cleaned = Path(cleaned).stem
    return f"{cleaned}.csv"


def _is_safe_filename(name: str) -> bool:
    if not name or name in {".", ".."}:
        return False
    if os.path.sep in name or (os.path.altsep and os.path.altsep in name):
        return False
    return True


def plan_csv_renames(
    directory_path: str,
    renames: Dict[str, str],
) -> Tuple[List[Tuple[Path, Path]], List[str]]:
    """
    Valide une liste de renommages et retourne les paires source/cible.

    Args:
        directory_path: Dossier contenant les CSV
        renames: {nom_actuel: nouveau_nom}

    Returns:
        (paires à appliquer, messages d'erreur)
    """
    directory = Path(directory_path)
    errors: List[str] = []
    pairs: List[Tuple[Path, Path]] = []

    if not directory.is_dir():
        return [], [f"Répertoire non trouvé: {directory_path}"]

    existing_csv = {Path(path).name for path in get_csv_files_in_directory(directory_path)}
    planned_targets: Dict[str, str] = {}

    for old_name, raw_new_name in renames.items():
        old_name = old_name.strip()
        new_name = normalize_csv_filename(raw_new_name)

        if old_name not in existing_csv:
            errors.append(f"Fichier introuvable: {old_name}")
            continue

        if new_name == old_name:
            continue

        if not _is_safe_filename(new_name):
            errors.append(f"Nom invalide pour « {old_name} » → « {new_name} »")
            continue

        if new_name in planned_targets.values():
            errors.append(f"Nom cible en double: {new_name}")
            continue

        source = directory / old_name
        target = directory / new_name

        if target.exists() and target.name != old_name:
            errors.append(f"Le fichier existe déjà: {new_name}")
            continue

        planned_targets[old_name] = new_name
        pairs.append((source, target))

    return pairs, errors


def apply_csv_renames(pairs: List[Tuple[Path, Path]]) -> None:
    """Applique les renommages validés."""
    for source, target in pairs:
        source.rename(target)


def rename_csv_files(directory_path: str, renames: Dict[str, str]) -> int:
    """
    Valide et applique les renommages.

    Returns:
        Nombre de fichiers renommés.

    Raises:
        CsvRenamerError: si la validation échoue ou si aucun renommage n'est demandé.
    """
    pairs, errors = plan_csv_renames(directory_path, renames)
    if errors:
        raise CsvRenamerError("\n".join(errors))
    if not pairs:
        raise CsvRenamerError("Aucun fichier à renommer (noms identiques).")
    apply_csv_renames(pairs)
    return len(pairs)
