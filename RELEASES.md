# 🚀 Guide des Releases - BGRAPP Pyconseil

Ce document décrit le processus de création et de distribution des releases pour BGRAPP Pyconseil.

## 📦 Types de Releases

### Windows - Exécutable Portable
- **Format :** `.exe` (exécutable unique)
- **Compatibilité :** Windows 7/8/10/11 (32-bit et 64-bit)
- **Installation :** Aucune installation requise
- **Taille :** ~80-150 MB

### Linux - AppImage
- **Format :** `.AppImage` (portable) + exécutable standard
- **Compatibilité :** La plupart des distributions Linux modernes
- **Installation :** Aucune installation requise pour AppImage
- **Taille :** ~80-150 MB

## 🛠️ Processus de Build

### Prérequis
1. **Environnement de développement** configuré
2. **Python 3.8+** installé
3. **Toutes les dépendances** du projet disponibles

### Étapes de Build

#### 1. Préparation
```bash
# Vérifier que tout fonctionne
python main.py

# Tester la configuration de build
cd build_config
python test_build.py
```

#### 2. Build Windows (sur machine Windows)
```cmd
cd build_config
build_windows.bat
```

**Résultat :** `build_config/dist/BGRAPP_Pyconseil.exe`

#### 3. Build Linux (sur machine Linux)
```bash
cd build_config
./build_linux.sh
```

**Résultats :**
- `build_config/dist/BGRAPP_Pyconseil` (exécutable)
- `BGRAPP_Pyconseil-YYYY.MM.DD-x86_64.AppImage` (AppImage)

### Vérification des Builds

1. **Test de démarrage :** L'application doit se lancer sans erreur
2. **Test des fonctionnalités principales :**
   - Sélection de dossier
   - Configuration IA
   - Génération JSON
   - Interface de conseil
3. **Test sur machine "propre"** (sans environnement de développement)

## 📋 Checklist de Release

### Avant le Build
- [ ] Code finalisé et testé
- [ ] Version mise à jour dans les fichiers appropriés
- [ ] Documentation à jour
- [ ] Tests passent avec succès
- [ ] Configuration IA testée avec tous les providers

### Pendant le Build
- [ ] Build Windows réussi sans erreur
- [ ] Build Linux réussi sans erreur
- [ ] Taille des exécutables raisonnable (< 200 MB)
- [ ] Aucun fichier sensible inclus (clés API, etc.)

### Après le Build
- [ ] Test des exécutables sur machine de test
- [ ] Vérification des permissions sur Linux (`chmod +x`)
- [ ] Documentation utilisateur mise à jour
- [ ] Notes de release rédigées

## 📝 Convention de Nommage

### Fichiers de Release
```
Windows: BGRAPP_Pyconseil_v[VERSION]_Windows.exe
Linux:   BGRAPP_Pyconseil_v[VERSION]_Linux.AppImage
```

### Exemple
```
BGRAPP_Pyconseil_v1.0.0_Windows.exe
BGRAPP_Pyconseil_v1.0.0_Linux.AppImage
```

## 🌐 Distribution

### Plateformes de Distribution
1. **GitHub Releases** (recommandé)
   - Upload des binaires
   - Notes de release
   - Checksums SHA256

2. **Site web du projet**
   - Liens de téléchargement
   - Guide d'installation
   - FAQ

### Information Utilisateur
Chaque release doit inclure :
- **Notes de version** (nouveautés, corrections)
- **Instructions d'installation** simples
- **Configuration requise** minimale
- **Guide de première utilisation**

## 🔒 Sécurité

### Vérifications Importantes
- **Aucune clé API** dans les exécutables
- **Données de test** supprimées ou anonymisées
- **Permissions appropriées** sur les fichiers
- **Signature numérique** (optionnel mais recommandé)

### Checksums
Générer des checksums pour vérification :
```bash
# Windows
certutil -hashfile BGRAPP_Pyconseil_v1.0.0_Windows.exe SHA256

# Linux
sha256sum BGRAPP_Pyconseil_v1.0.0_Linux.AppImage
```

## 📊 Métriques de Release

### Suivi Recommandé
- Nombre de téléchargements
- Rapports de bugs utilisateurs
- Feedback sur les performances
- Compatibilité avec différents systèmes

## 🆘 Résolution de Problèmes

### Build Échoue
1. Vérifier les logs de PyInstaller
2. Tester `python test_build.py`
3. Nettoyer les fichiers temporaires
4. Mettre à jour les dépendances

### Exécutable Ne Démarre Pas
1. Tester sur machine de développement
2. Vérifier les modules manquants
3. Contrôler les exclusions PyInstaller
4. Tester en mode debug

### Taille Excessive
1. Réviser les exclusions dans `pyconseil.spec`
2. Supprimer les modules inutiles
3. Activer la compression UPX
4. Considérer le mode "onedir"

## 📅 Planning de Release

### Release Majeure (X.0.0)
- Nouvelles fonctionnalités importantes
- Changements d'interface
- Tests étendus sur multiple plateformes

### Release Mineure (X.Y.0)
- Nouvelles fonctionnalités
- Améliorations existantes
- Corrections de bugs

### Release de Correctif (X.Y.Z)
- Corrections de bugs uniquement
- Améliorations de performance
- Mises à jour de sécurité

---

**Note :** Ce processus est conçu pour être reproductible et sûr. Testez toujours sur des machines différentes avant la distribution finale. 