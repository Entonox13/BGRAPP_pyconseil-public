# Section à ajouter dans le README.md principal

## 📥 Téléchargement et Installation

### 🚀 Versions Portables (Recommandées)

| Plateforme | Téléchargement | Taille | Compatibilité |
|------------|---------------|--------|---------------|
| 🪟 **Windows** | [📦 BGRAPP_Pyconseil_Latest_Windows.exe](releases/latest/BGRAPP_Pyconseil_Latest_Windows.exe) | ~100MB | Windows 7/8/10/11 |
| 🐧 **Linux** | [📦 BGRAPP_Pyconseil_Latest_Linux.AppImage](releases/latest/BGRAPP_Pyconseil_Latest_Linux.AppImage) | ~100MB | Ubuntu 18.04+, Debian 10+ |

### ⚡ Installation Rapide

#### Windows
```bash
# 1. Téléchargez le fichier .exe
# 2. Double-cliquez pour lancer
# ✅ Aucune installation requise !
```

#### Linux
```bash
# 1. Téléchargez le fichier .AppImage
wget https://github.com/VOTRE_USERNAME/BGRAPP_Pyconseil/releases/latest/download/BGRAPP_Pyconseil_Latest_Linux.AppImage

# 2. Rendez-le exécutable
chmod +x BGRAPP_Pyconseil_Latest_Linux.AppImage

# 3. Lancez l'application
./BGRAPP_Pyconseil_Latest_Linux.AppImage
```

### 🔒 Vérification d'Intégrité (Optionnel)

Pour vérifier l'intégrité des fichiers téléchargés :

```bash
# Windows
certutil -hashfile BGRAPP_Pyconseil_Latest_Windows.exe SHA256

# Linux
sha256sum BGRAPP_Pyconseil_Latest_Linux.AppImage
```

Comparez avec les checksums disponibles dans le dossier [releases/latest/](releases/latest/).

### 📋 Configuration Requise

| Système | Minimum | Recommandé |
|---------|---------|------------|
| **Windows** | Windows 7 SP1 | Windows 10/11 |
| **Linux** | Ubuntu 18.04, Debian 10 | Ubuntu 22.04+, Debian 11+ |
| **RAM** | 2 GB | 4 GB+ |
| **Espace disque** | 200 MB | 500 MB |
| **Réseau** | Connexion Internet pour l'IA | Connexion stable |

### 🔧 Alternative : Installation depuis les Sources

Si vous préférez installer depuis les sources ou pour le développement :

```bash
# 1. Cloner le repository
git clone https://github.com/VOTRE_USERNAME/BGRAPP_Pyconseil.git
cd BGRAPP_Pyconseil

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
python main.py
```

### 📝 Première Utilisation

1. **Lancez l'application**
2. **Configurez vos clés IA** (menu Configuration)
   - OpenAI, Anthropic, ou Google Gemini
   - Voir [guide de configuration](README_CONFIG_IA.md)
3. **Sélectionnez votre dossier** de bulletins
4. **Générez votre fichier JSON** de données
5. **Utilisez l'assistant conseil** pour vos préparations

### 🆘 Support et Documentation

- 📖 **Documentation complète** : [README principal](README.md)
- ⚙️ **Configuration IA** : [Guide de configuration](README_CONFIG_IA.md) 
- 🏗️ **Build depuis les sources** : [Guide de build](build_config/README_BUILD.md)
- 🐛 **Signaler un bug** : [Issues GitHub](https://github.com/VOTRE_USERNAME/BGRAPP_Pyconseil/issues)
- 💬 **Questions** : [Discussions GitHub](https://github.com/VOTRE_USERNAME/BGRAPP_Pyconseil/discussions)

---

## Badges à ajouter en haut du README

```markdown
[![Dernière Release](https://img.shields.io/github/v/release/VOTRE_USERNAME/BGRAPP_Pyconseil)](https://github.com/VOTRE_USERNAME/BGRAPP_Pyconseil/releases/latest)
[![Téléchargements](https://img.shields.io/github/downloads/VOTRE_USERNAME/BGRAPP_Pyconseil/total)](https://github.com/VOTRE_USERNAME/BGRAPP_Pyconseil/releases)
[![Licence](https://img.shields.io/github/license/VOTRE_USERNAME/BGRAPP_Pyconseil)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/downloads/)
[![Plateforme](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)](releases/)
```

## Instructions pour GitHub Releases

### 1. Activation des GitHub Releases

1. Allez dans votre repository GitHub
2. Cliquez sur l'onglet **"Releases"**
3. Cliquez sur **"Create a new release"**

### 2. Création d'une Release

```yaml
Tag version: v1.0.0
Release title: "BGRAPP Pyconseil v1.0.0 - Première Release Stable"
Description: |
  ## 🎉 Première release stable de BGRAPP Pyconseil
  
  ### ✨ Fonctionnalités
  - Interface graphique complète
  - Support OpenAI, Anthropic, Google Gemini
  - Génération automatique de JSON depuis bulletins
  - Assistant conseil intelligent
  - Versions portables Windows et Linux
  
  ### 📦 Téléchargements
  - **Windows**: BGRAPP_Pyconseil_Latest_Windows.exe
  - **Linux**: BGRAPP_Pyconseil_Latest_Linux.AppImage
  
  ### 🔒 Checksums SHA256
  Voir les fichiers .sha256 pour vérifier l'intégrité.

Fichiers à attacher:
- BGRAPP_Pyconseil_Latest_Windows.exe
- BGRAPP_Pyconseil_Latest_Windows.exe.sha256
- BGRAPP_Pyconseil_Latest_Linux.AppImage
- BGRAPP_Pyconseil_Latest_Linux.AppImage.sha256
```

### 3. Automation avec GitHub Actions (Optionnel)

Créez `.github/workflows/release.yml` pour automatiser :

```yaml
name: Build and Release
on:
  push:
    tags:
      - 'v*'
  
jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Build Windows
        run: |
          cd build_config
          build_windows.bat
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: windows-exe
          path: releases/latest/BGRAPP_Pyconseil_Latest_Windows.*

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Build Linux
        run: |
          cd build_config
          ./build_linux.sh
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: linux-appimage
          path: releases/latest/BGRAPP_Pyconseil_Latest_Linux.*

  release:
    needs: [build-windows, build-linux]
    runs-on: ubuntu-latest
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v3
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            windows-exe/*
            linux-appimage/*
``` 