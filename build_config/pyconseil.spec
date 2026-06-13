# -*- mode: python ; coding: utf-8 -*-
"""
Fichier de configuration PyInstaller pour BGRAPP Pyconseil
Génère un exécutable portable avec toutes les dépendances incluses
"""

import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Configuration des chemins
project_root = Path('..').resolve()
src_path = project_root / 'src'
main_script = project_root / 'main.py'

# Collecte automatique des sous-modules des SDK IA (souvent mal détectés)
ai_hiddenimports = (
    collect_submodules('google.genai')
    + collect_submodules('anthropic')
    + collect_submodules('openai')
)
ai_datas = collect_data_files('google.genai') + collect_data_files('certifi')

# Configuration de l'analyse
a = Analysis(
    [str(main_script)],
    pathex=[str(project_root), str(src_path)],
    binaries=[],
    datas=[
        # Inclure les fichiers de configuration d'exemple si nécessaires
        (str(project_root / 'exemples'), 'exemples'),
        (str(project_root / 'docs'), 'docs'),
    ] + ai_datas,
    hiddenimports=[
        # Modules qui pourraient ne pas être détectés automatiquement
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        # SDK IA
        'openai',
        'anthropic',
        'google.genai',
        'google.genai.types',
        # Configuration / environnement
        'dotenv',
        'json',
        'pathlib',
        'threading',
        'queue',
        'urllib3',
        'certifi',
        # Lecture des bulletins (.xlsx)
        'pandas',
        'pandas.core',
        'pandas.io',
        'pandas.io.formats',
        'pandas.io.formats.style',
        'openpyxl',
        'openpyxl.cell._writer',
        'numpy',
        # Modules du projet
        'src.gui.main_window',
        'src.gui.config_window',
        'src.gui.conseil_window',
        'src.gui.edition_window',
        'src.services.main_processor',
        'src.services.ai_config_service',
        'src.services.ai_connection_test_service',
        'src.services.openai_service',
        'src.services.bulletin_processor',
        'src.services.file_reader',
        'src.services.json_generator',
        'src.models.bulletin',
    ] + ai_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclure les modules non nécessaires pour réduire la taille
        'matplotlib',
        # 'numpy',  # Requis par pandas
        # 'pandas', # Requis par file_reader
        'scipy',
        'jupyter',
        'IPython',
        'conda',
        'anaconda',
        'pytest',
        'test',
        'unittest',
        'doctest',
        'pydoc',
        'distutils',
        'setuptools._vendor',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Configuration du PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Configuration de l'exécutable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BGRAPP_Pyconseil',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compression UPX si disponible
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Interface GUI, pas de console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Icône de l'application (optionnel)
    icon=None,  # Ajouter un fichier .ico/.icns si disponible
)

# Configuration pour créer un dossier de distribution (optionnel)
# Décommentez les lignes suivantes pour créer un dossier au lieu d'un seul exe
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='BGRAPP_Pyconseil'
# ) 