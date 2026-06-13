#!/bin/bash
# Script de build pour Linux - BGRAPP Pyconseil
# Crée un exécutable portable et une AppImage

set -e  # Arrêt en cas d'erreur

echo ""
echo "========================================"
echo "  BGRAPP Pyconseil - Build Linux"
echo "========================================"
echo ""

# Vérification que nous sommes dans le bon répertoire
if [ ! -f "../main.py" ]; then
    echo "❌ ERREUR: Ce script doit être exécuté depuis le dossier build_config"
    echo "Le fichier main.py doit être présent dans le répertoire parent"
    exit 1
fi

# Fonction pour vérifier si une commande existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Vérification des dépendances système
echo "[0/6] Vérification des dépendances système..."
if ! command_exists python3; then
    echo "❌ ERREUR: Python 3 n'est pas installé"
    exit 1
fi

if ! command_exists pip3; then
    echo "❌ ERREUR: pip3 n'est pas installé"
    exit 1
fi

# Création d'un environnement virtuel de build
echo "[1/6] Création de l'environnement virtuel de build..."
python3 -m venv build_env
source build_env/bin/activate

# Installation des dépendances de build
echo "[2/6] Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements_build.txt

# Nettoyage des anciens builds
echo "[3/6] Nettoyage des anciens builds..."
rm -rf dist build *.AppImage

# Construction de l'exécutable avec PyInstaller
echo "[4/6] Construction de l'exécutable avec PyInstaller..."
pyinstaller --clean pyconseil.spec

# Vérification du résultat PyInstaller
if [ -f "dist/BGRAPP_Pyconseil" ]; then
    echo "✅ Exécutable PyInstaller créé avec succès !"
    
    # Rendre l'exécutable... exécutable
    chmod +x dist/BGRAPP_Pyconseil
    
    echo "📁 Emplacement: $(pwd)/dist/BGRAPP_Pyconseil"
    echo "💾 Taille: $(du -h dist/BGRAPP_Pyconseil | cut -f1)"
else
    echo "❌ ERREUR: L'exécutable PyInstaller n'a pas été créé"
    exit 1
fi

# Création de l'AppImage (optionnel)
echo "[5/6] Tentative de création d'AppImage..."

# Vérification si appimagetool est disponible
if command_exists appimagetool; then
    echo "📦 Création de l'AppImage..."
    
    # Création de la structure AppImage
    mkdir -p AppDir/usr/bin
    mkdir -p AppDir/usr/share/applications
    mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
    
    # Copie de l'exécutable
    cp dist/BGRAPP_Pyconseil AppDir/usr/bin/
    
    # Création du fichier .desktop
    cat > AppDir/usr/share/applications/pyconseil.desktop << EOF
[Desktop Entry]
Type=Application
Name=BGRAPP Pyconseil
Comment=Outil d'aide à la préparation des conseils de classe
Exec=BGRAPP_Pyconseil
Icon=pyconseil
Categories=Education;Office;
EOF
    
    # Création d'une icône de placeholder (optionnel)
    # Si vous avez une icône PNG, copiez-la ici :
    # cp ../icon.png AppDir/usr/share/icons/hicolor/256x256/apps/pyconseil.png
    
    # Liens symboliques requis pour AppImage
    ln -sf usr/share/applications/pyconseil.desktop AppDir/
    ln -sf usr/bin/BGRAPP_Pyconseil AppDir/AppRun
    
    # Création de l'AppImage
    VERSION=$(date +%Y.%m.%d) appimagetool AppDir BGRAPP_Pyconseil-$(date +%Y.%m.%d)-x86_64.AppImage
    
    if [ -f "BGRAPP_Pyconseil-$(date +%Y.%m.%d)-x86_64.AppImage" ]; then
        chmod +x "BGRAPP_Pyconseil-$(date +%Y.%m.%d)-x86_64.AppImage"
        echo "✅ AppImage créée avec succès !"
        echo "📁 Emplacement: $(pwd)/BGRAPP_Pyconseil-$(date +%Y.%m.%d)-x86_64.AppImage"
        echo "💾 Taille: $(du -h BGRAPP_Pyconseil-$(date +%Y.%m.%d)-x86_64.AppImage | cut -f1)"
    else
        echo "⚠️  Échec de création de l'AppImage (l'exécutable PyInstaller reste disponible)"
    fi
    
    # Nettoyage
    rm -rf AppDir
else
    echo "⚠️  appimagetool non trouvé - AppImage non créée"
    echo "   Pour installer appimagetool:"
    echo "   wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    echo "   chmod +x appimagetool-x86_64.AppImage"
    echo "   sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool"
fi

echo "[6/6] Build terminé !"

# Désactivation de l'environnement virtuel
deactivate

# Préparation des releases finales
echo "[7/7] Préparation de la release..."

# Création des dossiers releases
mkdir -p ../releases/latest

# Variables pour les noms de fichiers
APPIMAGE_NAME="BGRAPP_Pyconseil-$(date +%Y.%m.%d)-x86_64.AppImage"
LATEST_APPIMAGE="../releases/latest/BGRAPP_Pyconseil_Latest_Linux.AppImage"
LATEST_EXECUTABLE="../releases/latest/BGRAPP_Pyconseil_Latest_Linux"

# Copie de l'exécutable standard
if [ -f "dist/BGRAPP_Pyconseil" ]; then
    cp "dist/BGRAPP_Pyconseil" "$LATEST_EXECUTABLE"
    chmod +x "$LATEST_EXECUTABLE"
    echo "✅ Exécutable copié vers releases/latest/"
fi

# Copie de l'AppImage si elle existe
if [ -f "$APPIMAGE_NAME" ]; then
    cp "$APPIMAGE_NAME" "$LATEST_APPIMAGE"
    chmod +x "$LATEST_APPIMAGE"
    echo "✅ AppImage copiée vers releases/latest/"
fi

# Génération des checksums
echo "🔒 Génération des checksums SHA256..."
cd ../releases/latest

if [ -f "BGRAPP_Pyconseil_Latest_Linux" ]; then
    sha256sum "BGRAPP_Pyconseil_Latest_Linux" > "BGRAPP_Pyconseil_Latest_Linux.sha256"
fi

if [ -f "BGRAPP_Pyconseil_Latest_Linux.AppImage" ]; then
    sha256sum "BGRAPP_Pyconseil_Latest_Linux.AppImage" > "BGRAPP_Pyconseil_Latest_Linux.AppImage.sha256"
fi

# Retour au dossier de build
cd ../../build_config

echo ""
echo "🎉 Build Linux terminé avec succès !"
echo ""
echo "📦 Fichiers de release créés :"
if [ -f "../releases/latest/BGRAPP_Pyconseil_Latest_Linux" ]; then
    echo "  📄 Exécutable: releases/latest/BGRAPP_Pyconseil_Latest_Linux"
fi
if [ -f "../releases/latest/BGRAPP_Pyconseil_Latest_Linux.AppImage" ]; then
    echo "  📦 AppImage: releases/latest/BGRAPP_Pyconseil_Latest_Linux.AppImage"
fi
echo "  🔒 Checksums SHA256 générés"
echo "" 