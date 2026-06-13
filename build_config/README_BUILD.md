# 🏗️ Guide de Build et Packaging - BGRAPP Pyconseil

Ce dossier contient tous les outils nécessaires pour créer des versions portables de l'application BGRAPP Pyconseil pour Windows et Linux.

## 📋 Prérequis

### Pour tous les systèmes
- Python 3.8+ installé
- pip (gestionnaire de paquets Python)
- Connexion Internet (pour télécharger les dépendances)

### Pour Windows
- Windows 7+ (recommandé: Windows 10/11)
- PowerShell ou Invite de commandes

### Pour Linux
- Distribution Linux moderne (Ubuntu 18.04+, Debian 10+, CentOS 8+, etc.)
- `python3-venv` installé (`sudo apt install python3-venv` sur Ubuntu/Debian)

## 🚀 Instructions de Build

### Windows - Exécutable Portable (.exe)

1. **Ouvrir un terminal** dans le dossier `build_config`
2. **Exécuter le script de build :**
   ```cmd
   build_windows.bat
   ```

3. **Attendre la fin du processus** (peut prendre 5-15 minutes selon votre machine)

4. **Récupérer l'exécutable :**
   - Fichier créé : `build_config/dist/BGRAPP_Pyconseil.exe`
   - Taille approximative : 80-150 MB
   - **Portable** : Peut être copié sur n'importe quel PC Windows sans installation

### Linux - Exécutable et AppImage

1. **Ouvrir un terminal** dans le dossier `build_config`
2. **Exécuter le script de build :**
   ```bash
   ./build_linux.sh
   ```

3. **Attendre la fin du processus** (peut prendre 5-15 minutes)

4. **Récupérer les fichiers créés :**
   - **Exécutable standard :** `build_config/dist/BGRAPP_Pyconseil`
   - **AppImage (si appimagetool disponible) :** `BGRAPP_Pyconseil-YYYY.MM.DD-x86_64.AppImage`

#### Installation d'appimagetool (optionnel)
Pour créer une AppImage, installez appimagetool :
```bash
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
```

## 📁 Structure des Fichiers

```
build_config/
├── README_BUILD.md          # Ce fichier
├── requirements_build.txt   # Dépendances épurées pour le build
├── pyconseil.spec          # Configuration PyInstaller
├── build_windows.bat       # Script de build Windows
├── build_linux.sh          # Script de build Linux
├── build_env/              # Environnement virtuel temporaire (créé automatiquement)
├── dist/                   # Dossier de sortie des exécutables
└── build/                  # Fichiers temporaires PyInstaller
```

## 🔧 Personnalisation

### Modifier la configuration PyInstaller

Éditez le fichier `pyconseil.spec` pour :
- **Ajouter une icône :** Décommentez et modifiez la ligne `icon=None`
- **Inclure des fichiers supplémentaires :** Ajoutez-les dans la section `datas`
- **Modifier les exclusions :** Ajustez la liste `excludes` pour réduire la taille

### Ajouter des dépendances

Si vous ajoutez de nouveaux modules Python à l'application :
1. Ajoutez-les dans `requirements_build.txt`
2. Ajoutez-les dans `hiddenimports` du fichier `pyconseil.spec` si nécessaire

## 🐛 Résolution de Problèmes

### "Module not found" lors de l'exécution
- Ajoutez le module manquant dans `hiddenimports` du fichier `pyconseil.spec`
- Vérifiez que toutes les dépendances sont dans `requirements_build.txt`

### Exécutable trop volumineux
- Ajoutez des modules inutiles dans `excludes` du fichier `pyconseil.spec`
- Activez la compression UPX (déjà activée par défaut)

### Erreur "No such file or directory" sur Linux
- Vérifiez que le script a les permissions d'exécution : `chmod +x build_linux.sh`
- Assurez-vous d'être dans le bon dossier : `cd build_config`

### Problème avec tkinter
- Ubuntu/Debian : `sudo apt install python3-tk`
- CentOS/RHEL : `sudo yum install tkinter` ou `sudo dnf install python3-tkinter`

## 📦 Distribution

### Windows
- Distribuez le fichier `BGRAPP_Pyconseil.exe`
- Aucune installation requise sur le PC cible
- Compatible Windows 7/8/10/11

### Linux
- **Exécutable standard :** Nécessite les mêmes bibliothèques système que votre machine de build
- **AppImage :** Portable, fonctionne sur la plupart des distributions Linux modernes
- Rendez le fichier exécutable avant distribution : `chmod +x`

## 🔒 Sécurité

- Les exécutables créés ne contiennent **aucune clé API** par défaut
- Les utilisateurs devront configurer leurs propres clés IA via l'interface
- Tous les fichiers de configuration restent locaux sur la machine de l'utilisateur

## 📈 Optimisation

### Réduire la taille de l'exécutable
1. **Examinez les dépendances incluses :**
   ```bash
   pyinstaller --clean --log-level=DEBUG pyconseil.spec
   ```

2. **Ajoutez des exclusions spécifiques** dans `pyconseil.spec`

3. **Utilisez le mode "onedir"** au lieu de "onefile" si nécessaire :
   - Décommentez la section `COLLECT` dans `pyconseil.spec`
   - Commentez `a.binaries, a.zipfiles, a.datas` dans la section `EXE`

### Améliorer les performances de démarrage
- Le mode "onedir" démarre plus rapidement que "onefile"
- Réduisez les imports inutiles dans le code source

## 🆘 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs de build pour des erreurs spécifiques
2. Assurez-vous que tous les prérequis sont installés
3. Consultez la documentation PyInstaller : https://pyinstaller.readthedocs.io/

---

**Note :** Ce système de build est conçu pour créer des versions de distribution. Pour le développement quotidien, continuez à utiliser `python main.py` directement. 