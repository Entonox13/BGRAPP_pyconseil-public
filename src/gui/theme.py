# -*- coding: utf-8 -*-
"""
Thème graphique centralisé pour l'interface Tkinter/ttk.
"""

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import Optional, Tuple

# Polices reconnues pour la lisibilité à l'écran (ordre de préférence).
_UI_FONT_CANDIDATES = (
    "DejaVu Sans",
    "Noto Sans",
    "Ubuntu",
    "Liberation Sans",
    "Cantarell",
    "Source Sans 3",
    "Source Sans Pro",
    "Open Sans",
    "Inter",
    "Verdana",
    "Segoe UI",
    "SF Pro Text",
    "Arial",
)
_MONO_FONT_CANDIDATES = (
    "DejaVu Sans Mono",
    "Liberation Mono",
    "Ubuntu Mono",
    "JetBrains Mono",
    "Cascadia Mono",
    "Noto Sans Mono",
    "Consolas",
)

FONT_SIZE_BODY = 13
FONT_SIZE_HEADER = 14
FONT_SIZE_LARGE = 15
FONT_SIZE_SUBTITLE = 15
FONT_SIZE_TITLE = 20
FONT_SIZE_TITLE_CONSEIL = 22
FONT_SIZE_MONO = 12

PADDING_COMPACT = "8"
PADDING_NORMAL = "12"
PADDING_LARGE = "20"

ROW_HEIGHT_TREEVIEW = 30
NAV_PANEL_WIDTH = 220

# Libellés UI sans emoji (polices Tkinter/Linux sans glyphes emoji)
TITLE_APP = "BGRAPP Pyconseil"
TITLE_CONSEIL = "Conseil de Classe — Vue plein écran"

SECTION_DIRECTORY = "Sélection du dossier de travail"
SECTION_PROCESSING = "Traitement des données"
SECTION_NAVIGATION = "Navigation"
LABEL_PERIOD_ACTIVE = "Période active :"
SECTION_CONFIG_STATUS = "État de la configuration"

BTN_CREATE_JSON = "Créer fichier JSON"
BTN_LOAD_JSON = "Charger JSON"
BTN_LOAD_JSON_EXISTING = "Charger JSON existant"
BTN_PERIOD_LINKS = "Périodes liées"
BTN_QUIT = "Quitter"
BTN_BACK = "\u2190 Retour"
BTN_PREV = "\u2190 Précédent"
BTN_NEXT = "Suivant \u2192"
BTN_CANCEL = "Annuler"
BTN_EDIT_WINDOW = "Fenêtre d'édition"
BTN_CONSEIL_WINDOW = "Fenêtre conseil"
BTN_CONFIG_IA = "Configuration IA"
BTN_TEST_CONNECTION = "Tester la connexion"
BTN_ADD_JSON = "Ajouter un JSON"
BTN_REMOVE_SELECTION = "Retirer la sélection"
BTN_EDIT_PERIOD = "Modifier la période"
BTN_SAVE = "Sauvegarder"
BTN_REFRESH_MODELS = "Rafraîchir les modèles"
BTN_REFRESHING = "Récupération..."
BTN_TEST_IN_PROGRESS = "Test en cours..."
BTN_PREPROCESS = "Prétraitement"
BTN_PREPROCESS_BULLETIN = "Prétraiter ce bulletin"
BTN_GENERATE = "Générer appréciation"
BTN_GENERATE_GENERAL = "Génération appréciation générale"
BTN_EXPORT = "Exporter"
BTN_PRINT = "Imprimer"
BTN_FULLSCREEN = "Basculer plein écran"
BTN_SHOW = "Afficher"
BTN_HELP = "Aide"

TITLE_EDITION = "Édition des bulletins"
TITLE_CONFIG_IA = "Configuration IA"

TAB_SYNTHESIS = "Synthèse"
TAB_DETAILS = "Détails des appréciations"
TAB_STUDENT = "Élève"
TAB_SUBJECTS = "Matières"
TAB_GENERAL = "Appréciation générale"

DIALOG_PERIOD_LINKS_TITLE = "Périodes liées"

# Préfixes de messages (ASCII, lisibles en police mono)
LOG_OK = "[OK]"
LOG_ERR = "[ERREUR]"
LOG_WARN = "[AVERT]"
LOG_INFO = "[INFO]"

_available_families: Optional[set] = None
_font_ui: Optional[str] = None
_font_mono: Optional[str] = None
_fonts_initialized = False
_font_warning_shown = False


def _fallback_families() -> set:
    return set(_UI_FONT_CANDIDATES) | set(_MONO_FONT_CANDIDATES)


def _reset_font_cache() -> None:
    global _available_families, _font_ui, _font_mono, _fonts_initialized
    _available_families = None
    _font_ui = None
    _font_mono = None
    _fonts_initialized = False


def _font_families(root: Optional[tk.Misc] = None) -> set:
    global _available_families
    if _available_families is None:
        try:
            probe = root or tk._default_root
            if probe is None:
                temp = tk.Tk()
                temp.withdraw()
                families = tkfont.families(temp)
                temp.destroy()
            else:
                families = tkfont.families(probe)
            if isinstance(families, (list, tuple, set)):
                _available_families = set(families)
            else:
                _available_families = _fallback_families()
        except Exception:
            _available_families = _fallback_families()
    return _available_families


def _font_resolves_to_bitmap(family: str, root: Optional[tk.Misc] = None) -> bool:
    """True si Tk retombe sur une police bitmap (fixed, etc.)."""
    try:
        probe = root or tk._default_root
        if probe is None:
            return False
        actual = tkfont.Font(root=probe, family=family, size=FONT_SIZE_BODY).actual()
        resolved = str(actual.get("family", "")).lower()
        return resolved in {"fixed", "courier", "helvetica"}
    except tk.TclError:
        return False


def _pick_font_family(
    candidates: Tuple[str, ...],
    root: Optional[tk.Misc] = None,
) -> str:
    families = _font_families(root)
    for name in candidates:
        if name in families and not _font_resolves_to_bitmap(name, root):
            return name
    for name in candidates:
        if name in families:
            return name
    return "TkDefaultFont"


def get_font_ui() -> str:
    global _font_ui
    if _font_ui is None:
        _font_ui = _pick_font_family(_UI_FONT_CANDIDATES)
    return _font_ui


def get_font_mono() -> str:
    global _font_mono
    if _font_mono is None:
        _font_mono = _pick_font_family(_MONO_FONT_CANDIDATES)
    return _font_mono


def init_fonts(root: tk.Misc) -> str:
    """Initialise les polices lisibles via la fenêtre Tk courante."""
    global _font_ui, _font_mono, _fonts_initialized, _font_warning_shown, _available_families
    _available_families = None
    _font_families(root)
    _font_ui = _pick_font_family(_UI_FONT_CANDIDATES, root)
    _font_mono = _pick_font_family(_MONO_FONT_CANDIDATES, root)
    _fonts_initialized = True

    if _font_resolves_to_bitmap(_font_ui, root) and not _font_warning_shown:
        _font_warning_shown = True
        print(
            f"{LOG_WARN} Polices Tk pixellisées : installez tk avec fontconfig.\n"
            "  conda install -c conda-forge --force-reinstall \"tk=xft_*\""
        )
    return _font_ui


def font_ui(size: int, bold: bool = False) -> Tuple[str, int, str]:
    style = "bold" if bold else "normal"
    return (get_font_ui(), size, style)


def font_body(bold: bool = False) -> Tuple[str, int, str]:
    return font_ui(FONT_SIZE_BODY, bold=bold)


def font_mono() -> Tuple[str, int]:
    return (get_font_mono(), FONT_SIZE_MONO)


def font_html_tag(class_name: str) -> Tuple[str, int, str]:
    if class_name in ("positif", "negatif"):
        return font_body(bold=True)
    return font_body(bold=False)


def html_tag_foreground(class_name: str) -> str:
    if class_name == "positif":
        return "green"
    if class_name == "negatif":
        return "red"
    return "black"


def apply_theme(style: ttk.Style, *, conseil: bool = False) -> None:
    """Applique les styles ttk partagés."""
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    title_size = FONT_SIZE_TITLE_CONSEIL if conseil else FONT_SIZE_TITLE
    subtitle_size = FONT_SIZE_SUBTITLE if conseil else FONT_SIZE_SUBTITLE - 1

    style.configure("Title.TLabel", font=font_ui(title_size, bold=True))
    style.configure("Subtitle.TLabel", font=font_ui(subtitle_size, bold=True))
    style.configure("Info.TLabel", font=font_body())
    style.configure("Header.TLabel", font=font_ui(FONT_SIZE_HEADER, bold=True))
    style.configure("Large.TLabel", font=font_ui(FONT_SIZE_LARGE))
    style.configure("Success.TLabel", font=font_body(), foreground="green")
    style.configure("Error.TLabel", font=font_body(), foreground="red")
    style.configure("Warning.TLabel", font=font_body(), foreground="orange")
    style.configure(
        "Treeview",
        font=font_body(),
        rowheight=ROW_HEIGHT_TREEVIEW,
    )
    style.configure("Treeview.Heading", font=font_ui(FONT_SIZE_HEADER, bold=True))
    style.configure("TButton", font=font_body())


def setup_root_scaling(root: tk.Misc) -> None:
    """Initialise polices + scaling DPI pour un rendu lisible."""
    global _fonts_initialized
    if not _fonts_initialized:
        init_fonts(root)
    try:
        dpi = root.winfo_fpixels("1i")
        if not isinstance(dpi, (int, float)) or dpi <= 0:
            return
        scaling = max(1.0, min(dpi / 96.0, 2.0))
        root.tk.call("tk", "scaling", scaling)
    except (tk.TclError, TypeError, AttributeError):
        pass
