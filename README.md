# 🎓 BGRAPP Pyconseil

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-orange.svg)](https://openai.com/)

**Outil d'aide à la préparation des conseils de classe en collège**

Une application Python avec interface graphique pour centraliser et traiter les données des élèves, optimisant ainsi la préparation des conseils de classe dans les établissements de collège.

## ✨ Fonctionnalités

### 🔄 Traitement des données
- **Import automatique** : Traitement des fichiers Excel (liste élèves) et CSV (notes par matière)
- **Génération JSON** : Création d'un fichier structuré contenant tous les bulletins
- **Vérification de cohérence** : Correspondance automatique entre nombre d'élèves et bulletins générés

### 🤖 Intelligence artificielle
- **Traitement OpenAI** : Amélioration automatique des appréciations avec balises HTML sémantiques
- **Génération synthétique** : Création d'appréciations générales à partir des notes de chaque matière
- **Balises contextuelles** : Identification automatique des éléments positifs et négatifs

### 🖥️ Interface graphique
- **Fenêtre principale** : Sélection du dossier de travail et lancement des traitements
- **Fenêtre d'édition** : Visualisation et navigation dans les bulletins générés
- **Fenêtre conseil** : Interface dédiée à la préparation des conseils (en développement)

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- Environnement Conda recommandé

### Installation des dépendances
```bash
# Cloner le repository
git clone https://github.com/votre-utilisateur/BGRAPP_Pyconseil.git
cd BGRAPP_Pyconseil

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement pour OpenAI
cp .env.example .env
# Éditer .env avec votre clé API OpenAI
```

### Configuration OpenAI
Créez un fichier `.env` à la racine du projet :
```env
OPENAI_API_KEY=votre_clé_api_openai
```

### 🔒 Protection RGPD intégrée

**L'application intègre un système d'anonymisation automatique conforme RGPD** :

- **Anonymisation transparente** : Les noms et prénoms des élèves sont automatiquement remplacés par "John DOE" avant envoi à OpenAI
- **Désanonymisation automatique** : Les réponses de l'API sont automatiquement restaurées avec les vrais noms des élèves  
- **Aucun impact utilisateur** : Le processus est totalement transparent
- **Activation par défaut** : La protection RGPD est activée automatiquement
- **Conformité réglementaire** : Respect des articles 4(5), 5(1)(c) et 32 du RGPD
- **Repository sécurisé** : Aucun fichier contenant de vraies données personnelles d'élèves n'est versionné

```python
# La protection RGPD est activée par défaut
service = get_openai_service()  # enable_rgpd=True

# Pour désactiver (déconseillé) :
service = get_openai_service(enable_rgpd=False)
```

**⚠️ IMPORTANT** : Ce repository ne contient aucune donnée personnelle réelle. Pour utiliser l'application avec vos propres données :
1. Créez un dossier privé (non versionné) avec vos fichiers Excel/CSV
2. Utilisez l'interface pour sélectionner ce dossier
3. L'anonymisation RGPD protégera automatiquement vos données

Consultez `exemples/README_DONNEES_ANONYMISEES.md` pour les détails complets.

## 📖 Utilisation

### Lancement de l'application
```bash
python main.py
```

### Structure des fichiers d'entrée
Votre dossier de travail doit contenir : un fichier .csv par matière (nommé selon la matière); un fichier source.xlsx contenant les noms les appréciations du semestre précédent(il est préférable de travailler à partir du fichier source.xlsx afin de respecter la forme des données attendues).
```
dossier_de_travail/
├── source.xlsx          # Liste des élèves
├── mathematiques.csv    # Notes de mathématiques
├── francais.csv        # Notes de français
├── histoire_geo.csv    # Notes d'histoire-géographie
└── ...                 # Autres matières
```

### Workflow typique
1. **Sélection du dossier** : Choisir le dossier contenant vos fichiers source
2. **Génération JSON** : Traiter les données pour créer le fichier `output.json`
3. **Édition** : Parcourir et améliorer les bulletins avec l'IA
4. **Conseil** : Utiliser l'interface de préparation des conseils

### Obtention des fichiers csv
1. **Connexion à Pronote** : Via l'ENT de votre établissement
2. **Localiser les appréciations par matière** : Bulletins->Saisie des appréciations->Appréciations des professeurs du bulletin
3. **Téléchargement des fichiers d'appréciation** : cliquer sur le bouton "Copier la liste" 
    ![Bouton Copier la liste](docs/logo_dl_csv.png)
4. **Renommer le fichier** : Renommer le fichier par le nom de la matière
5. **Recommencer pour chaque matière** : Recommencer à partir de l'étape 3 pour chacune des matières
6. **Préparer le dossier** : Placer l'ensemble des fichiers CSV et le fichier source.xlsx dans un dossier


## 🏗️ Architecture

```
BGRAPP_Pyconseil/
├── src/
│   ├── gui/                 # Interfaces graphiques
│   │   ├── main_window.py   # Fenêtre principale
│   │   ├── edition_window.py # Fenêtre d'édition
│   │   └── conseil_window.py # Fenêtre conseil
│   ├── services/            # Services métier
│   │   ├── main_processor.py    # Traitement principal
│   │   ├── bulletin_processor.py # Logique bulletins
│   │   ├── openai_service.py    # Interface OpenAI
│   │   ├── file_reader.py       # Lecture fichiers
│   │   └── json_generator.py    # Génération JSON
│   ├── models/              # Modèles de données
│   │   └── bulletin.py      # Structure bulletin
│   └── utils/               # Utilitaires
├── tests/                   # Tests unitaires
├── docs/                    # Documentation
├── exemples/               # Fichiers d'exemple
└── main.py                 # Point d'entrée
```

## 🔧 Technologies utilisées

- **Interface** : Tkinter (GUI native Python)
- **Traitement données** : pandas, openpyxl
- **IA** : OpenAI API
- **Configuration** : python-dotenv
- **Tests** : pytest

## 📝 Format des données

### Structure d'un bulletin (JSON)
```json
{
  "Nom": "DUPONT",
  "Prenom": "Alice",
  "AppreciationGeneraleS1": "Bon travail d'ensemble",
  "AppreciationGeneraleS2": "Des efforts constants", 
  "Matieres": {
    "Mathematiques": {
      "HeuresAbsence": 3,
      "MoyenneS1": 14.5,
      "MoyenneS2": 13.0,
      "MoyenneMax": 18.5,
      "MoyenneMin": 9.0,
      "AppreciationS1": "Bon travail d'ensemble",
      "AppreciationS2": "Des efforts constants"
    },
    "Francais": {
      "HeuresAbsence": 0,
      "MoyenneS1": 12.0,
      "MoyenneS2": 14.0,
      "MoyenneMax": 16.0,
      "MoyenneMin": 10.0,
      "AppreciationS1": "Participation en progrès",
      "AppreciationS2": "Très bonne implication"
    }
  }
}
```

## 🧪 Tests

```bash
# Exécuter tous les tests
python -m pytest tests/

# Tests spécifiques
python -m pytest tests/test_models.py
python -m pytest tests/test_processor.py
```

## 📊 Exemples

Le dossier `exemples/` contient :
- `exemple.json` : Structure de référence des bulletins
- Fichiers CSV d'exemple pour les tests
- Scripts de démonstration

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

### Standards de développement
- Code en français (commentaires, variables)
- Documentation docstring pour toutes les fonctions
- Tests unitaires pour les nouvelles fonctionnalités
- Respect de la structure MVC

## 📋 Roadmap

- [x] Interface graphique principale
- [x] Traitement des fichiers Excel/CSV
- [x] Génération JSON des bulletins
- [x] Intégration OpenAI pour les appréciations
- [x] Fenêtre d'édition des bulletins
- [ ] Fenêtre conseil (spécifications en cours)
- [ ] Export vers d'autres formats
- [ ] Gestion des modèles d'appréciation
- [ ] Interface web (future version)

## 🐛 Problèmes connus

- La fenêtre conseil est en cours de développement
- Certaines dépendances conda peuvent nécessiter une installation manuelle
- Performance à optimiser pour les gros fichiers (>500 élèves)

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/votre-utilisateur/BGRAPP_Pyconseil/issues)
- **Documentation** : Dossier `docs/`
- **Email** : bgrapp@proton.me

## 💝 Soutenir le projet

Si ce projet vous aide dans votre travail quotidien et que vous souhaitez soutenir son développement, vous pouvez faire un don via PayPal. Votre soutien m'aide à consacrer plus de temps à l'amélioration de l'outil, au développement de nouvelles fonctionnalités et au financement de mon addiction à la caféine.

<p align="center">
  <a href="https://www.paypal.com/donate/?hosted_button_id=NVZ2K47TMT636">
    <img src="https://img.shields.io/badge/PayPal-Faire%20un%20don-0070ba.svg?style=for-the-badge&logo=paypal&logoColor=white" alt="Faire un don via PayPal" height="50">
  </a>
</p>

**Merci pour votre soutien !**

---

*Développé avec ❤️ pour faciliter le travail des équipes éducatives* 