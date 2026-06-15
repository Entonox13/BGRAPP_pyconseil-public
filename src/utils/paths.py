#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilitaires de chemins pour l'interface graphique."""

from pathlib import Path


def get_documents_dir() -> str:
    """
    Retourne le dossier Documents de l'utilisateur.

    Utilisé comme répertoire initial des dialogues de sélection de fichiers
    et dossiers. Retombe sur le répertoire personnel si Documents n'existe pas.
    """
    documents = Path.home() / "Documents"
    if documents.is_dir():
        return str(documents)
    return str(Path.home())
