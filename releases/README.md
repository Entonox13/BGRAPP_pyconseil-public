# 📦 Dossier des Releases - BGRAPP Pyconseil

Ce dossier contient toutes les versions releases de l'application BGRAPP Pyconseil.

## 📁 Organisation

```
releases/
├── README.md                                      # Ce fichier
├── latest/                                        # Liens vers la dernière version
│   ├── BGRAPP_Pyconseil_Latest_Windows.exe
│   └── BGRAPP_Pyconseil_Latest_Linux.AppImage
├── v1.0.0/                                       # Version 1.0.0
│   ├── BGRAPP_Pyconseil_v1.0.0_Windows.exe
│   ├── BGRAPP_Pyconseil_v1.0.0_Linux.AppImage
│   ├── BGRAPP_Pyconseil_v1.0.0_Linux
│   └── checksums.txt
└── archives/                                     # Versions archivées
    ├── v0.9.0/
    └── v0.8.0/
```

## 🎯 Téléchargement Rapide

### Dernière Version
- **Windows** : [BGRAPP_Pyconseil_Latest_Windows.exe](latest/BGRAPP_Pyconseil_Latest_Windows.exe)
- **Linux AppImage** : [BGRAPP_Pyconseil_Latest_Linux.AppImage](latest/BGRAPP_Pyconseil_Latest_Linux.AppImage)

## 📋 Instructions d'Installation

### Windows
1. Téléchargez le fichier `.exe`
2. Double-cliquez pour lancer l'application
3. **Aucune installation requise** - L'application est portable

### Linux
1. Téléchargez le fichier `.AppImage`
2. Rendez-le exécutable : `chmod +x BGRAPP_Pyconseil_*.AppImage`
3. Double-cliquez ou lancez en ligne de commande
4. **Aucune installation requise** - L'application est portable

## 🔒 Vérification d'Intégrité

Chaque release inclut un fichier `checksums.txt` contenant les hashes SHA256 pour vérifier l'intégrité des fichiers téléchargés.

```bash
# Vérification sur Linux/Mac
sha256sum -c checksums.txt

# Vérification sur Windows
certutil -hashfile filename.exe SHA256
```

## 📝 Changelog

Consultez le fichier [RELEASES.md](../RELEASES.md) pour voir l'historique complet des versions et les notes de release.

## 🆘 Support

- **Documentation** : Consultez le [README principal](../README.md)
- **Issues** : Reportez les problèmes sur GitHub
- **Configuration** : Voir [README_CONFIG_IA.md](../README_CONFIG_IA.md)

---

**Note** : Ces fichiers sont générés automatiquement par les scripts de build. Ne modifiez pas ce dossier manuellement. 