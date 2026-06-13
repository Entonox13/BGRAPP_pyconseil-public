# DEVBOOK - Outil d'aide aux conseils de classe

## 📋 Vue d'ensemble du projet

**Objectif** : Développement d'un outil Python avec interface graphique pour faciliter la préparation des conseils de classe en collège.

**Technologies** : Python, Interface graphique (tkinter/PyQt), API OpenAI, pandas/openpyxl

---

## 🏗️ ARCHITECTURE DU DÉVELOPPEMENT

### Phase 1: Préparation et environnement
### Phase 2: Analyse et modélisation des données  
### Phase 3: Moteur de traitement JSON
### Phase 4: Interface graphique - Fenêtre principale
### Phase 5: Interface graphique - Fenêtre d'édition
### Phase 6: Intégration API OpenAI
### Phase 7: Interface graphique - Fenêtre conseil
### Phase 8: Tests et validation
### Phase 9: Documentation et finalisation

---

## 📝 DÉTAIL DES PHASES

## PHASE 1: PRÉPARATION ET ENVIRONNEMENT

### 🎯 Objectifs
- Mise en place de l'environnement de développement
- Structure du projet
- Dépendances et outils

### 📋 Tâches détaillées

#### 1.1 Configuration de l'environnement Conda
- **Livrable** : Environnement conda fonctionnel
- **Nom de l'environnement** : `BGRAPP_pyconseil`
- **Actions** :
  - Créer un environnement conda dédié : `conda create -n BGRAPP_pyconseil python=3.9`
  - Activer l'environnement : `conda activate BGRAPP_pyconseil`
- **Critères de validation** : 
  - Environnement activable sans erreur
  - Python 3.9+ disponible
- **Statut** : ✅ **TERMINÉ** - Environnement créé avec Python 3.9.23

#### 1.2 Structure du projet
- **Livrable** : Architecture de dossiers
- **Structure créée** :
  ```
  BGRAPP_Pyconseil/
  ├── src/                     # Code source principal
  │   ├── __init__.py
  │   ├── models/              # Modèles de données
  │   │   └── __init__.py
  │   ├── gui/                 # Interface graphique
  │   │   └── __init__.py
  │   ├── services/            # Services métier
  │   │   └── __init__.py
  │   └── utils/               # Utilitaires
  │       └── __init__.py
  ├── exemples/                # Fichiers d'exemple existants
  ├── tests/                   # Tests unitaires
  │   └── README.md
  ├── docs/                    # Documentation
  │   └── README.md
  ├── main.py                  # Point d'entrée application
  ├── requirements.txt         # Dépendances Python
  ├── .gitignore              # Fichiers à ignorer Git
  ├── devbook.md              # Plan de développement
  └── cahier des charges.txt   # Spécifications
  ```
- **Critères de validation** : Tous les dossiers créés ✅
- **Statut** : ✅ **TERMINÉ** - Structure complète créée et testée

#### 1.3 Installation des dépendances
- **Livrable** : `requirements.txt` et packages installés
- **Packages installés** :
  - **Python 3.9.23** - Langage principal
  - **pandas 2.2.3** - Traitement des données Excel/CSV
  - **openpyxl 3.1.5** - Lecture des fichiers Excel (.xlsx)
  - **requests 2.32.3** - Communication avec l'API OpenAI
  - **pytest 8.3.4** - Framework de tests unitaires
  - **numpy 2.0.1** - Calculs numériques (dépendance pandas)
  - **tkinter** - Interface graphique (inclus avec Python)
- **Actions** :
  - Installation via conda : `conda install pandas openpyxl requests pytest -y`
  - Génération du requirements.txt : `pip freeze > requirements.txt`
- **Critères de validation** : Tous les packages installés sans erreur
- **Statut** : ✅ **TERMINÉ** - Tous les packages installés dans l'environnement BGRAPP_pyconseil

---

## PHASE 2: ANALYSE ET MODÉLISATION DES DONNÉES ✅

### 🎯 Objectifs
- Comprendre la structure des données d'entrée ✅
- Modéliser les objets bulletin ✅
- Créer les fichiers d'exemple ✅

### 📈 Résumé des réalisations
- **Fichiers analysés** : `source.xlsx` (24 élèves) + 6 fichiers CSV de matières
- **Modèles créés** : 3 classes principales + fonctions utilitaires
- **Tests** : 16 tests unitaires avec 100% de réussite
- **Documentation** : Analyse complète dans `docs/analyse_donnees_phase2.md`
- **Structure JSON** : Conforme au fichier `exemple.json` (préservé)

### 📋 Tâches détaillées

#### 2.1 Analyse des fichiers source
- **Livrable** : Documentation de la structure des données
- **Actions** :
  - Analyser le format `source.xlsx` (colonnes, types de données)
  - Analyser le format des fichiers `.csv` par matière
  - Identifier les relations entre les données
- **Critères de validation** : Documentation complète des formats
- **Statut** : ✅ **TERMINÉ** - Structure analysée et documentée dans `docs/analyse_donnees_phase2.md`

#### 2.2 Création du modèle de données
- **Livrable** : `src/models/bulletin.py`
- **Actions** :
  - Classe `Eleve` (nom, prénom, classe, etc.)
  - Classe `AppreciationMatiere` (matière, notes, commentaires, etc.)
  - Classe `Bulletin` (élève, appréciations, appréciation générale)
  - Fonctions utilitaires `parse_heures_absence()` et `parse_moyenne()`
- **Critères de validation** : Classes instanciables avec validation
- **Statut** : ✅ **TERMINÉ** - Modèles complets avec sérialisation JSON bidirectionnelle

#### 2.3 Fichier exemple.json
- **Livrable** : `exemples/exemple.json`
- **Actions** :
  - Structure JSON complète d'un bulletin
  - Exemples d'appréciations par matière
  - Format de l'appréciation générale
- **Critères de validation** : JSON valide et conforme au modèle
- **Statut** : ✅ **TERMINÉ** - Fichier préservé comme référence (24 élèves)

#### 2.4 Fichiers de test
- **Livrable** : Fichiers dans `/exemples`
- **Actions** :
  - `exemples/source.xlsx` avec 24 élèves ✅
  - `exemples/mathematiques.csv` ✅
  - `exemples/francais.csv` ✅
  - `exemples/histoire.csv` ✅
  - `exemples/Anglais LV1.csv` (existant) ✅
  - `exemples/Arts Plastiques.csv` (existant) ✅
  - `exemples/Allemand LV2.csv` (existant) ✅
- **Critères de validation** : Fichiers cohérents entre eux
- **Statut** : ✅ **TERMINÉ** - 6 matières avec données complètes, structure cohérente

#### 2.5 Tests unitaires (ajouté)
- **Livrable** : `tests/test_models.py`
- **Actions** :
  - Tests pour toutes les classes (Eleve, AppreciationMatiere, Bulletin)
  - Tests des fonctions utilitaires de parsing
  - Tests de sérialisation/désérialisation JSON
  - Couverture complète des fonctionnalités
- **Critères de validation** : Tous les tests passent
- **Statut** : ✅ **TERMINÉ** - 16 tests unitaires, 100% de réussite

---

## PHASE 3: MOTEUR DE TRAITEMENT JSON ✅

### 🎯 Objectifs
- Lecture des fichiers d'entrée ✅
- Génération du fichier output.json ✅
- Logique métier de traitement ✅

### 📈 Résumé des réalisations
- **Modules créés** : 4 modules principaux (file_reader, bulletin_processor, json_generator, main_processor)
- **Tests fonctionnels** : Traitement réussi de 24 bulletins avec 6 matières
- **Validation** : Génération de output.json conforme (50KB de données)
- **Performance** : Traitement complet en moins d'une seconde
- **Robustesse** : Gestion d'erreurs et validation des données intégrées

### 📋 Tâches détaillées

#### 3.1 Lecteur de fichiers source ✅
- **Livrable** : `src/services/file_reader.py` ✅
- **Actions** :
  - Fonction `read_source_xlsx()` : lecture de la liste des élèves ✅
  - Fonction `read_csv_matiere()` : lecture des notes par matière ✅
  - Gestion des erreurs de fichiers ✅
- **Critères de validation** : Lecture sans erreur des fichiers d'exemple ✅
- **Statut** : ✅ **TERMINÉ** - Module complet avec validation de répertoire et gestion d'erreurs

#### 3.2 Processeur de bulletins ✅
- **Livrable** : `src/services/bulletin_processor.py` ✅
- **Actions** :
  - Fonction `create_bulletins_from_source()` : création des objets bulletin ✅
  - Fonction `populate_bulletins_from_csv()` : ajout des appréciations ✅
  - Validation de la cohérence des données ✅
- **Critères de validation** : Génération correcte des bulletins ✅
- **Statut** : ✅ **TERMINÉ** - Traitement de 24 bulletins avec parsing avancé S1/S2 et calcul min/max

#### 3.3 Générateur JSON ✅
- **Livrable** : `src/services/json_generator.py` ✅
- **Actions** :
  - Fonction `bulletins_to_json()` : conversion en JSON ✅
  - Fonction `save_output_json()` : sauvegarde du fichier ✅
  - Validation du format de sortie ✅
- **Critères de validation** : output.json conforme à exemple.json ✅
- **Statut** : ✅ **TERMINÉ** - Génération de 50KB JSON structuré avec chargement bidirectionnel

#### 3.4 Tests unitaires moteur ✅
- **Livrable** : `tests/test_processor.py` ✅
- **Actions** :
  - Tests de lecture des fichiers ✅
  - Tests de génération des bulletins ✅
  - Tests de cohérence des données ✅
- **Critères de validation** : Tous les tests passent ✅
- **Statut** : ✅ **TERMINÉ** - Suite de tests complète avec workflow end-to-end validé

---

## PHASE 4: INTERFACE GRAPHIQUE - FENÊTRE PRINCIPALE ✅

### 🎯 Objectifs
- Interface de sélection du dossier de travail ✅
- Boutons de navigation vers les autres fenêtres ✅
- Intégration du moteur de traitement ✅

### 📈 Résumé des réalisations
- **Interface complète** : Fenêtre principale fonctionnelle avec tkinter
- **Sélecteur avancé** : Validation automatique des dossiers + affichage des statistiques
- **Intégration moteur** : Traitement JSON en arrière-plan avec barre de progression
- **Navigation prête** : Boutons préparés pour les phases futures
- **Tests créés** : Suite de tests unitaires complète
- **Import fixes** : Résolution des imports relatifs pour compatibilité totale

### 📋 Tâches détaillées

#### 4.1 Fenêtre principale base ✅
- **Livrable** : `src/gui/main_window.py` ✅
- **Actions** :
  - Classe `MainWindow` héritant de tkinter ✅
  - Layout de base avec titre et sections ✅
  - Gestion de la fermeture de l'application ✅
- **Critères de validation** : Fenêtre s'affiche correctement ✅
- **Statut** : ✅ **TERMINÉ** - Interface moderne avec 4 sections organisées

#### 4.2 Sélecteur de dossier ✅
- **Livrable** : Fonctionnalité de sélection ✅
- **Actions** :
  - Bouton "Choisir dossier de travail" ✅
  - Dialog de sélection de dossier ✅
  - Validation de la présence des fichiers requis ✅
  - Affichage du dossier sélectionné ✅
- **Critères de validation** : Sélection et validation fonctionnelles ✅
- **Statut** : ✅ **TERMINÉ** - Analyse automatique avec preview des données détectées

#### 4.3 Lancement création JSON ✅
- **Livrable** : Intégration du moteur ✅
- **Actions** :
  - Bouton "Créer JSON" ✅
  - Appel au moteur de traitement ✅
  - Barre de progression ✅
  - Messages de succès/erreur ✅
- **Critères de validation** : Génération JSON depuis l'interface ✅
- **Statut** : ✅ **TERMINÉ** - Traitement asynchrone avec feedback temps réel

#### 4.4 Navigation vers autres fenêtres ✅
- **Livrable** : Boutons de navigation ✅
- **Actions** :
  - Bouton "Fenêtre édition" (préparation) ✅
  - Bouton "Fenêtre conseil" (préparation) ✅
  - Bouton "Quitter" ✅
- **Critères de validation** : Boutons présents et préparés ✅
- **Statut** : ✅ **TERMINÉ** - Placeholders informatifs pour les phases futures

#### 4.5 Tests et intégration (ajouté) ✅
- **Livrable** : `tests/test_gui.py` et corrections d'imports ✅
- **Actions** :
  - Suite de tests unitaires complète ✅
  - Correction des imports relatifs dans tous les modules ✅
  - Intégration dans main.py ✅
  - Mise à jour du module __init__.py ✅
- **Critères de validation** : Application lançable et testable ✅
- **Statut** : ✅ **TERMINÉ** - 15 tests unitaires + application fonctionnelle

---

## PHASE 5: INTERFACE GRAPHIQUE - FENÊTRE D'ÉDITION ✅

### 🎯 Objectifs
- Affichage des données de bulletins ✅
- Navigation entre bulletins ✅
- Préparation de l'intégration OpenAI ✅

### 📈 Résumé des réalisations
- **Interface complète** : Fenêtre d'édition fonctionnelle avec 3 onglets organisés
- **Chargement bulletins** : Support JSON complet avec validation et gestion d'erreurs
- **Affichage riche** : Informations élève, tableau des matières avec moyennes/absences, appréciations
- **Navigation fluide** : Boutons précédent/suivant + liste cliquable avec indicateur de position
- **Intégration réussie** : Lancement depuis la fenêtre principale avec vérification des prérequis
- **Sauvegarde** : Modifications des appréciations générales persistantes
- **Tests créés** : Suite de tests unitaires pour validation des fonctionnalités

### 📋 Tâches détaillées

#### 5.1 Fenêtre d'édition base ✅
- **Livrable** : `src/gui/edition_window.py` ✅
- **Actions** :
  - Classe `EditionWindow` avec layout moderne ✅
  - 3 onglets: Élève, Matières, Appréciation générale ✅
  - Barre d'outils avec chargeur JSON et indicateur position ✅
  - Bouton retour à la fenêtre principale ✅
- **Critères de validation** : Fenêtre s'ouvre depuis la principale ✅
- **Statut** : ✅ **TERMINÉ** - Interface moderne 1000x700px avec navigation intuitive

#### 5.2 Chargement des bulletins ✅
- **Livrable** : Gestionnaire de données ✅
- **Actions** :
  - Fonction `_load_bulletins_from_file()` avec gestion complète ✅
  - Dialog de sélection fichier + auto-chargement si fourni ✅
  - Gestion robuste des erreurs (fichier manquant, JSON invalide) ✅
  - Structure de données en mémoire avec modèles Bulletin ✅
- **Critères de validation** : Chargement correct des bulletins ✅
- **Statut** : ✅ **TERMINÉ** - Support JSON bidirectionnel avec validation complète

#### 5.3 Affichage des données bulletin ✅
- **Livrable** : Interface d'affichage ✅
- **Actions** :
  - Onglet élève: Nom, prénom, classe avec labels formatés ✅
  - Onglet matières: TreeView avec colonnes moyennes S1/S2 et absences ✅
  - Zone appréciations par matière (S1/S2) avec sélection ✅
  - Onglet appréciation générale: Zones de texte éditables S1/S2 ✅
  - Formatage lisible des données (moyennes à 2 décimales, "h" pour heures) ✅
- **Critères de validation** : Affichage complet et lisible ✅
- **Statut** : ✅ **TERMINÉ** - Interface riche avec données structurées et éditables

#### 5.4 Navigation entre bulletins ✅
- **Livrable** : Système de navigation ✅
- **Actions** :
  - Boutons "◀ Précédent" et "Suivant ▶" avec gestion d'état ✅
  - Liste des bulletins (panneau gauche) avec sélection directe ✅
  - Indicateur de position "Bulletin X / Y" en temps réel ✅
  - Gestion des limites (premier/dernier) avec boutons désactivés ✅
  - Synchronisation liste ↔ boutons ↔ affichage ✅
- **Critères de validation** : Navigation fluide entre tous les bulletins ✅
- **Statut** : ✅ **TERMINÉ** - Navigation complète avec scrollbar et synchronisation parfaite

#### 5.5 Boutons d'action préparatoires ✅
- **Livrable** : Boutons pour OpenAI ✅
- **Actions** :
  - Bouton "🔄 Prétraitement" avec placeholder informatif ✅
  - Bouton "✨ Génération appréciation générale" avec placeholder ✅
  - Messages d'information "Fonction à implémenter en Phase 6" ✅
  - Bouton "💾 Sauvegarder" fonctionnel pour appréciations générales ✅
  - Gestion d'état: activation/désactivation selon contexte ✅
- **Critères de validation** : Boutons présents avec messages temporaires ✅
- **Statut** : ✅ **TERMINÉ** - Interface prête pour intégration OpenAI en Phase 6

#### 5.6 Intégration et tests (ajouté) ✅
- **Livrable** : `tests/test_edition_window.py` et intégration main_window ✅
- **Actions** :
  - Mise à jour `main_window.py` pour lancer vraie fenêtre d'édition ✅
  - Vérification prérequis (fichier JSON existant) ✅
  - Import conditionnel et gestion d'erreurs ✅
  - Suite de tests unitaires avec mocking tkinter ✅
  - Mise à jour `__init__.py` pour exports ✅
- **Critères de validation** : Application fonctionnelle end-to-end ✅
- **Statut** : ✅ **TERMINÉ** - Application testée et fonctionnelle, prête pour Phase 6

---

## PHASE 6: INTÉGRATION API OPENAI ✅

### 🎯 Objectifs
- Configuration de l'API OpenAI ✅
- Prétraitement des appréciations ✅
- Génération d'appréciations générales ✅

### 📈 Résumé des réalisations
- **Service complet** : `openai_service.py` avec gestion d'erreurs et retry
- **Fonctionnalités globales** : Prétraitement et génération pour tous les bulletins
- **Fonctionnalités individuelles** : Boutons pour traiter le bulletin courant uniquement
- **Interface enrichie** : Barres de progression et feedback temps réel
- **Configuration flexible** : Support clé API via variable d'environnement
- **Tests créés** : Suite de tests d'intégration complète

### 📋 Tâches détaillées

#### 6.1 Configuration API OpenAI ✅
- **Livrable** : `src/services/openai_service.py` ✅
- **Actions** :
  - Configuration de la clé API (variable d'environnement OPENAI_API_KEY) ✅
  - Classe `OpenAIService` avec gestion des erreurs et retry ✅
  - Test de connexion à l'API avec `test_connection()` ✅
  - Factory function `get_openai_service()` ✅
- **Configuration clé API** : Fichier `.env` à la racine du projet (ligne 45 dans `__init__`)
- **Utilisation** : Éditer `.env` et remplacer `votre-clé-openai-ici` par votre vraie clé API
- **Critères de validation** : Connexion API fonctionnelle ✅
- **Statut** : ✅ **TERMINÉ** - Service robuste avec gestion complète des erreurs

#### 6.2 Prétraitement des appréciations ✅
- **Livrable** : Fonction de prétraitement ✅
- **Actions** :
  - Fonction `preprocess_appreciation(text)` avec prompt expert ✅
  - Ajout automatique de balises `<span class="positif">` et `<span class="negatif">` ✅
  - Fonction `preprocess_all_bulletins()` pour traitement en masse ✅
  - Gestion des erreurs API avec fallback sur texte original ✅
- **Prompt** : `src/services/openai_service.py` lignes 76-86 (fonction `preprocess_appreciation`)
- **Critères de validation** : Texte retourné avec balises HTML ✅
- **Statut** : ✅ **TERMINÉ** - Prétraitement avec progression et gestion d'erreurs

#### 6.3 Génération d'appréciation générale ✅
- **Livrable** : Fonction de génération ✅
- **Actions** :
  - Fonction `generate_general_appreciation(appreciations_by_subject)` ✅
  - Prompt de synthèse style "conseil de classe" (3-4 phrases max) ✅
  - Fonction `generate_all_general_appreciations()` pour tous les bulletins ✅
  - Synthèse basée sur appréciations S2 par matière ✅
- **Prompt** : `src/services/openai_service.py` lignes 108-122 (fonction `generate_general_appreciation`)
- **Critères de validation** : Appréciation générale cohérente générée ✅
- **Statut** : ✅ **TERMINÉ** - Génération avec validation des données d'entrée

#### 6.4 Intégration dans l'interface d'édition ✅
- **Livrable** : Fonctionnalités actives ✅
- **Actions** :
  - Activation du bouton "🔄 Prétraitement" pour tous les bulletins ✅
  - Activation du bouton "✨ Génération appréciation générale" pour tous les bulletins ✅
  - Ajout de boutons dans l'onglet appréciation générale pour le bulletin courant ✅
  - Fenêtres de progression avec barres et bouton annuler ✅
  - Threading pour éviter blocage de l'interface ✅
- **Critères de validation** : Fonctions opérationnelles depuis l'interface ✅
- **Statut** : ✅ **TERMINÉ** - Interface complète avec UX soignée

#### 6.5 Sauvegarde des modifications ✅
- **Livrable** : Persistance des données ✅
- **Actions** :
  - Sauvegarde automatique après chaque traitement ✅
  - Rafraîchissement de l'affichage après modifications ✅
  - Gestion des erreurs de sauvegarde ✅
  - Mise à jour du fichier JSON en temps réel ✅
- **Critères de validation** : Modifications persistantes ✅
- **Statut** : ✅ **TERMINÉ** - Sauvegarde automatique intégrée

#### 6.6 Tests et validation (ajouté) ✅
- **Livrable** : `test_openai_integration.py` et mise à jour requirements.txt ✅
- **Actions** :
  - Suite de tests d'intégration sans vraie clé API ✅
  - Test d'import et configuration du service ✅
  - Validation des imports dans l'interface ✅
  - Mise à jour requirements.txt avec package openai ✅
  - Mise à jour __init__.py des services ✅
- **Critères de validation** : Tous les tests d'intégration passent ✅
- **Statut** : ✅ **TERMINÉ** - 4/4 tests réussis, prêt pour utilisation

---

## PHASE 7: INTERFACE GRAPHIQUE - FENÊTRE CONSEIL ✅

### 🎯 Objectifs
- Créer une fenêtre conseil avec vue d'ensemble des bulletins ✅
- Conserver l'architecture de la fenêtre d'édition ✅
- Implémenter les fonctionnalités spécifiques au conseil de classe ✅

### 📈 Résumé des réalisations
- **Interface complète** : Fenêtre conseil fonctionnelle avec vue d'ensemble
- **Architecture réutilisée** : Navigation identique à la fenêtre d'édition
- **Vue synthèse** : Tableau des matières avec évolution des moyennes
- **Vue détaillée** : Affichage détaillé par matière avec appréciations
- **Affichage HTML** : Support des balises `<span class="positif/negatif">` avec formatage coloré
- **Intégration réussie** : Lancement depuis la fenêtre principale
- **Tests créés** : Suite de tests unitaires complète (10/10 réussis)

### 📋 Tâches détaillées

#### 7.1 Analyse du fichier exemple conseil ✅
- **Livrable** : Compréhension du format souhaité ✅
- **Actions** :
  - Analyse du fichier Excel `exexmpleconseil.xlsx` ✅
  - Identification de la structure des données ✅
  - Définition de l'interface adaptée ✅
- **Critères de validation** : Structure des données comprise ✅
- **Statut** : ✅ **TERMINÉ** - Format analysé (matières avec moyennes min/max, absences, appréciations)

#### 7.2 Création de la fenêtre conseil ✅
- **Livrable** : `src/gui/conseil_window.py` ✅
- **Actions** :
  - Classe `ConseilWindow` basée sur l'architecture d'édition ✅
  - Panneau navigation (identique à l'édition) ✅
  - Vue conseil avec 2 onglets : Synthèse et Détails ✅
  - Affichage informations élève en en-tête ✅
  - Zone appréciation générale en bas ✅
- **Critères de validation** : Interface fonctionnelle et ergonomique ✅
- **Statut** : ✅ **TERMINÉ** - Fenêtre 1200x800px avec navigation complète

#### 7.3 Vue synthèse des matières ✅
- **Livrable** : Tableau TreeView avec évolution ✅
- **Actions** :
  - Colonnes : Matière, Moy. S1, Moy. S2, Abs. S1, Abs. S2, Évolution ✅
  - Calcul automatique de l'évolution (↗️ ↘️ ➡️) ✅
  - Formatage des données (moyennes, heures d'absence) ✅
  - Scrolling vertical pour nombreuses matières ✅
- **Critères de validation** : Données claires et évolution visible ✅
- **Statut** : ✅ **TERMINÉ** - Vue synthétique avec indicateurs visuels

#### 7.4 Vue détaillée des matières ✅
- **Livrable** : Affichage détaillé par matière ✅
- **Actions** :
  - Zone scrollable avec frame par matière ✅
  - Moyennes S1/S2 et absences S1/S2 par matière ✅
  - Appréciations S1/S2 en zones de texte ✅
  - Gestion dynamique des widgets ✅
- **Critères de validation** : Informations complètes par matière ✅
- **Statut** : ✅ **TERMINÉ** - Vue détaillée complète avec scrolling

#### 7.5 Intégration et navigation ✅
- **Livrable** : Navigation et intégration dans l'app ✅
- **Actions** :
  - Boutons précédent/suivant avec gestion d'état ✅
  - Liste des bulletins avec sélection directe ✅
  - Indicateur de position "Bulletin X / Y" ✅
  - Chargement des données depuis JSON ✅
  - Lancement depuis la fenêtre principale ✅
- **Critères de validation** : Navigation fluide entre tous les bulletins ✅
- **Statut** : ✅ **TERMINÉ** - Navigation complète et intuitive

#### 7.6 Fonctionnalités placeholders ✅
- **Livrable** : Boutons export et impression ✅
- **Actions** :
  - Bouton "📤 Exporter" avec placeholder ✅
  - Bouton "🖨️ Imprimer" avec placeholder ✅
  - Messages informatifs pour futures implémentations ✅
  - Activation/désactivation selon contexte ✅
- **Critères de validation** : Interface préparée pour futures fonctionnalités ✅
- **Statut** : ✅ **TERMINÉ** - Placeholders informatifs implémentés

#### 7.7 Tests et validation ✅
- **Livrable** : `tests/test_conseil_window.py` et intégration ✅
- **Actions** :
  - Suite de tests unitaires complète (8 tests) ✅
  - Tests d'initialisation et navigation ✅
  - Tests des vues synthèse et détaillée ✅
  - Tests de chargement des données ✅
  - Intégration dans la fenêtre principale ✅
  - Mise à jour `__init__.py` pour exports ✅
- **Critères de validation** : Tous les tests passent ✅
- **Statut** : ✅ **TERMINÉ** - 8/8 tests réussis, application fonctionnelle

#### 7.8 Amélioration Post-Phase 7 : Interface Conseil Plein Écran 1080p
- **Date d'implémentation** : 21/01/2025 (mise à jour hauteurs)
- **Fonctionnalité ajoutée** : Optimisation de l'interface conseil pour écran 1080p en mode plein écran
- **Localisation** : `src/gui/conseil_window.py` avec refactorisation complète de l'interface
- **Améliorations clés** :
  - **Mode plein écran automatique** : Activation automatique avec gestion robuste multi-plateforme
  - **Zones d'appréciations matières ajustées** : Height=4 (≈3.5 lignes) pour équilibre espace/lisibilité
  - **Zones d'appréciations générales agrandies** : Height=5 (≈4.5 lignes) pour plus de visibilité
  - **Affichage côte à côte** : S1 et S2 en colonnes séparées dans la vue détaillée
  - **Scrollbars individuelles** : Chaque zone d'appréciation a sa propre scrollbar
  - **Layout compact** : Informations élève compactes, focus sur les appréciations
  - **Police agrandie** : Arial 11 pour une meilleure lisibilité
  - **Navigation améliorée** : Liste des bulletins avec plus de hauteur (25 entrées)
  - **Raccourcis clavier** : Échap et F11 pour basculer le plein écran
  - **Scroll molette** : Support de la molette de souris dans les appréciations
- **Script de démonstration** : `demo_conseil_fullscreen.py` pour tester l'interface
- **Compatibilité** : Gestion robuste Windows/Linux avec fallbacks automatiques
- **Avantage utilisateur** : Équilibre optimal entre espace des appréciations matières et générales

### Amélioration Post-Phase 7 : Configuration Flexible des Modèles OpenAI
- **Date d'implémentation** : 21/01/2025
- **Fonctionnalité ajoutée** : Possibilité de changer facilement le modèle OpenAI utilisé
- **Localisation** : `src/services/openai_service.py` avec variable configurable `DEFAULT_OPENAI_MODEL`
- **Améliorations apportées** :
  - **Variable de configuration** : `DEFAULT_OPENAI_MODEL` en haut du fichier (ligne 15)
  - **Support multi-modèles** : Compatible avec les gammes GPT-4.1 / GPT-5.1 / séries o1-o3 et suivants
  - **Paramètre optionnel** : Possibilité de spécifier le modèle lors de l'initialisation
  - **Documentation complète** : Liste des modèles disponibles avec descriptions
  - **Script de démonstration** : `demo_openai_models.py` pour tester et comprendre les options
  - **Factory function mise à jour** : `get_openai_service(model="...")` support du paramètre
  - **Logging informatif** : Affichage du modèle utilisé lors de l'initialisation
- **Utilisation** :
  - **Changement global** : Modifier `DEFAULT_OPENAI_MODEL` dans le fichier
  - **Changement ponctuel** : `service = get_openai_service(model="gpt-5.1-mini")`
- **Avantage utilisateur** : Flexibilité pour optimiser coût/performance selon les besoins

### Amélioration Post-Phase 7 : Configuration IA Multi-Fournisseurs 🤖
- **Date d'implémentation** : 22/01/2025
- **Fonctionnalité ajoutée** : Interface de configuration pour gérer plusieurs fournisseurs IA (OpenAI, Anthropic, Google Gemini)
- **Localisation** : `src/gui/config_window.py` et `src/services/ai_config_service.py`
- **Problématique** : L'application ne supportait qu'OpenAI, limitant les choix et la flexibilité utilisateur
- **Solution implémentée** :
  - **Service de configuration multi-fournisseurs** : `AIConfigService` avec support OpenAI, Anthropic, Gemini
  - **Interface graphique dédiée** : Fenêtre de configuration avec onglets par fournisseur
  - **Gestion des clés API** : Stockage sécurisé dans fichier `.env` avec masquage d'affichage
  - **Sélection des modèles** : Listes déroulantes avec modèles disponibles par fournisseur
  - **Fournisseur actif** : Checkbox et sélection du fournisseur utilisé pour les requêtes
  - **Validation de configuration** : Vérification automatique des clés API et modèles
  - **Bouton dans fenêtre principale** : "🤖 Configuration IA" accessible depuis la navigation
- **Fonctionnalités techniques** :
  - **Énumération AIProvider** : OPENAI, ANTHROPIC, GEMINI avec modèles prédéfinis
  - **Factory pattern** : `get_ai_config_service()` pour instance singleton
  - **Sauvegarde automatique** : Écriture dans `.env` via python-dotenv
  - **Interface modale** : Fenêtre de configuration non-bloquante avec callback
  - **Gestion d'erreurs** : Validation des modèles et clés API avec messages explicites
  - **Test de connexion** : Placeholder pour validation des clés API par fournisseur
- **Modèles supportés** :
  - **OpenAI** : gpt-5.1, gpt-5.1-mini, gpt-5.1-nano, gpt-4.1, o3-mini, etc.
  - **Anthropic** : claude-3.7-sonnet, claude-3.7-haiku, claude-3.5-sonnet, etc.
  - **Gemini** : gemini-2.0-pro, gemini-2.0-flash, gemini-2.0-flash-lite, etc.
- **Fichier .env structure** :
  ```
  OPENAI_API_KEY=your-openai-api-key-here
  ANTHROPIC_API_KEY=your-anthropic-api-key-here
  GOOGLE_API_KEY=your-google-api-key-here
  OPENAI_MODEL=gpt-5.1-mini
  ANTHROPIC_MODEL=claude-3.7-haiku
  GEMINI_MODEL=gemini-2.0-flash
  AI_ENABLED_PROVIDER=openai
  ```
- **Scripts et tests** :
  - **demo_config_ia.py** : Démonstration complète du système de configuration
  - **tests/test_config_window.py** : Tests unitaires (4/4 réussis)
- **Intégration** :
  - **Fenêtre principale** : Bouton "🤖 Configuration IA" dans section Navigation
  - **Imports mis à jour** : `src/gui/__init__.py` avec export `ConfigWindow`
  - **Callback de changement** : Notification dans log principale lors de modification config
- **Avantage utilisateur** : **Flexibilité totale** pour choisir le fournisseur IA selon besoins/budget

### Amélioration Post-Phase 7 : Anonymisation RGPD pour OpenAI 🔒
- **Date d'implémentation** : 22/01/2025
- **Fonctionnalité ajoutée** : Système d'anonymisation automatique des données personnelles conforme RGPD
- **Localisation** : `src/services/openai_service.py` avec classe `RGPDAnonymizer` et intégration dans `OpenAIService`
- **Problématique RGPD** : Les appréciations scolaires contiennent des noms/prénoms d'élèves envoyés à l'API OpenAI
- **Solution implémentée** :
  - **Classe RGPDAnonymizer** : Gestionnaire bidirectionnel d'anonymisation/désanonymisation
  - **Anonymisation automatique** : Remplacement "Suheda" → "John", "DANLER" → "DOE" avant envoi API
  - **Désanonymisation automatique** : Restauration "John" → "Suheda", "DOE" → "DANLER" dans les réponses
  - **Intégration transparente** : Aucun changement visible pour l'utilisateur final
  - **Activation par défaut** : RGPD activé automatiquement (`enable_rgpd=True`)
  - **Support désactivation** : `get_openai_service(enable_rgpd=False)` pour désactiver si besoin
- **Fonctionnalités techniques** :
  - **Mappings bidirectionnels** : Dictionnaires de correspondance nom ↔ clé anonymisée
  - **Recherche insensible à la casse** : "Ela", "ela", "ELA" tous remplacés par "John"
  - **Word boundaries** : Remplacement exact avec `\b` pour éviter les erreurs partielles
  - **Gestion des accents** : Support des caractères spéciaux (Anesa, Ukësmajli, etc.)
  - **Réversibilité garantie** : Tests unitaires validant la cohérence anonymisation ↔ désanonymisation
- **Integration dans l'application** :
  - **preprocess_appreciation()** : Paramètres `student_nom`, `student_prenom` ajoutés
  - **generate_general_appreciation()** : Anonymisation des appréciations par matière
  - **Interface graphique** : Appels mis à jour automatiquement avec nom/prénom élève
  - **Traitement en masse** : Support complet pour tous les bulletins simultanément
- **Scripts et tests** :
  - **demo_rgpd_anonymization.py** : Démonstration complète du système (187 lignes)
  - **tests/test_rgpd_anonymization.py** : 15 tests unitaires (100% réussite)
  - **Validation temps réel** : Tests avec vrais noms d'élèves du projet
- **Conformité RGPD** :
  - **Pseudonymisation** : Art. 4(5) RGPD - Données personnelles remplacées par identifiants techniques
  - **Minimisation** : Art. 5(1)(c) RGPD - Seuls les identifiants "John DOE" transitent vers OpenAI
  - **Sécurité** : Art. 32 RGPD - Protection des données par anonymisation technique
  - **Traçabilité** : Logs de débogage pour audit des opérations d'anonymisation
- **Avantage utilisateur** : **Confidentialité totale** des données élèves respectant les obligations RGPD

---

## PHASE 8: TESTS ET VALIDATION

### 🎯 Objectifs
- Tests complets de l'application
- Validation avec des données réelles
- Correction des bugs identifiés

### 📋 Tâches détaillées

#### 8.1 Tests unitaires complets
- **Livrable** : Suite de tests complète
- **Actions** :
  - Tests de tous les modules
  - Tests des cas d'erreur
  - Tests de l'intégration API
  - Coverage des tests > 80%
- **Critères de validation** : Tous les tests passent

#### 8.2 Tests d'intégration
- **Livrable** : Tests end-to-end
- **Actions** :
  - Test du workflow complet
  - Test avec des jeux de données variés
  - Test de l'interface graphique
- **Critères de validation** : Workflow complet fonctionnel

#### 8.3 Tests utilisateur
- **Livrable** : Validation utilisateur
- **Actions** :
  - Tests avec l'utilisateur final
  - Collecte de feedback
  - Ajustements d'ergonomie
- **Critères de validation** : Satisfaction utilisateur

#### 8.4 Gestion des erreurs
- **Livrable** : Robustesse de l'application
- **Actions** :
  - Gestion des fichiers manquants/corrompus
  - Gestion des erreurs API
  - Messages d'erreur clairs
- **Critères de validation** : Application stable en cas d'erreur

---

## PHASE 9: DOCUMENTATION ET FINALISATION

### 🎯 Objectifs
- Documentation utilisateur
- Guide d'installation
- Préparation du déploiement

### 📋 Tâches détaillées

#### 9.1 Documentation utilisateur
- **Livrable** : `docs/guide_utilisateur.md`
- **Actions** :
  - Guide d'utilisation pas à pas
  - Captures d'écran de l'interface
  - FAQ et résolution de problèmes
- **Critères de validation** : Documentation complète et claire

#### 9.2 Guide d'installation
- **Livrable** : `README.md` et `INSTALL.md`
- **Actions** :
  - Instructions d'installation détaillées
  - Prérequis système
  - Configuration de l'API OpenAI
- **Critères de validation** : Installation possible par un tiers

#### 9.3 Documentation technique
- **Livrable** : `docs/documentation_technique.md`
- **Actions** :
  - Architecture du code
  - Documentation des API
  - Guide de maintenance
- **Critères de validation** : Code maintenable par un autre développeur

#### 9.4 Package de distribution
- **Livrable** : Application packagée
- **Actions** :
  - Script de build
  - Exécutable standalone (optionnel)
  - Archive de distribution
- **Critères de validation** : Distribution prête à déployer

---

## 📊 SUIVI DU PROJET

### Métriques de suivi
- [x] **Phase 1 - TERMINÉE** (Date: $(date +'%d/%m/%Y'))
  - [x] 1.1 Configuration environnement conda ✅
  - [x] 1.2 Structure du projet ✅
  - [x] 1.3 Installation dépendances ✅
- [x] **Phase 2 - TERMINÉE** (Date: 20/01/2025)
  - [x] 2.1 Analyse des fichiers source ✅
  - [x] 2.2 Création du modèle de données ✅
  - [x] 2.3 Fichier exemple.json (préservé) ✅
  - [x] 2.4 Fichiers de test (complétés) ✅
- [x] **Phase 3 - TERMINÉE** (Date: 17/06/2025)
  - [x] 3.1 Lecteur de fichiers source ✅
  - [x] 3.2 Processeur de bulletins ✅
  - [x] 3.3 Générateur JSON ✅
  - [x] 3.4 Tests unitaires moteur ✅
- [x] **Phase 4 - TERMINÉE** (Date: 20/01/2025)
  - [x] 4.1 Fenêtre principale base ✅
  - [x] 4.2 Sélecteur de dossier ✅
  - [x] 4.3 Lancement création JSON ✅
  - [x] 4.4 Navigation vers autres fenêtres ✅
  - [x] 4.5 Tests et intégration ✅
- [x] **Phase 5 - TERMINÉE** (Date: 21/01/2025)
  - [x] 5.1 Fenêtre d'édition base ✅
  - [x] 5.2 Chargement des bulletins ✅
  - [x] 5.3 Affichage des données bulletin ✅
  - [x] 5.4 Navigation entre bulletins ✅
  - [x] 5.5 Boutons d'action préparatoires ✅
  - [x] 5.6 Intégration et tests ✅
- [x] **Phase 6 - TERMINÉE** (Date: 21/01/2025)
  - [x] 6.1 Configuration API OpenAI ✅
  - [x] 6.2 Prétraitement des appréciations ✅
  - [x] 6.3 Génération d'appréciation générale ✅
  - [x] 6.4 Intégration dans l'interface d'édition ✅
  - [x] 6.5 Sauvegarde des modifications ✅
  - [x] 6.6 Tests et validation ✅
- [x] **Phase 7 - TERMINÉE** (Date: 21/01/2025)
  - [x] 7.1 Analyse du fichier exemple conseil ✅
  - [x] 7.2 Création de la fenêtre conseil ✅
  - [x] 7.3 Vue synthèse des matières ✅
  - [x] 7.4 Vue détaillée des matières ✅
  - [x] 7.5 Intégration et navigation ✅
  - [x] 7.6 Fonctionnalités placeholders ✅
  - [x] 7.7 Tests et validation ✅
- [ ] Phase 8 complétée (Date: _____)
- [ ] Phase 9 complétée (Date: _____)

### Risques identifiés
- **API OpenAI** : Disponibilité et coûts
- **Format des fichiers** : Variations possibles des formats d'entrée (atténué par l'analyse Phase 2)
- **Performance** : Temps de traitement pour de gros volumes
- **Interface** : Utilisabilité pour des utilisateurs non techniques
- **Parsing CSV** : Gestion des caractères spéciaux et encodages (identifié Phase 2)
- **Moyennes min/max** : Calcul automatique par classe et matière (solution Phase 2)
- **Consistance données** : Correspondance entre source.xlsx et fichiers CSV

### Leçons apprises (Phase 2)
- **Séparation nom/prénom** : Méthode basée sur la casse fonctionne bien
- **Parsing flexible** : Fonctions utilitaires robustes pour formats français
- **Tests essentiels** : Validation complète évite les régressions
- **Structure modulaire** : Classes dataclass facilitent la maintenance
- **Documentation** : Analyse préalable accélère le développement

### Leçons apprises (Phase 4)
- **Imports relatifs** : Problématique complexe nécessitant des imports conditionnels
- **Threading GUI** : Essentiel pour éviter le blocage de l'interface lors du traitement
- **Validation en temps réel** : Analyse immédiate du dossier améliore l'UX
- **Feedback utilisateur** : Messages colorés et timestamp améliorent la lisibilité
- **Structure modulaire GUI** : Séparation claire des responsabilités facilite la maintenance
- **Tests GUI** : Mocking nécessaire pour tester les interfaces tkinter

### Leçons apprises (Phase 5)
- **Architecture onglets** : ttk.Notebook excellent pour organiser interfaces complexes
- **TreeView avancé** : Composant puissant pour données tabulaires avec sélection
- **Synchronisation état** : Navigation multi-modes (boutons + liste) nécessite coordination soignée
- **Gestion fichiers JSON** : Validation robuste et gestion d'erreurs critiques pour UX
- **Sauvegarde incrementale** : Persistance immédiate des modifications utilisateur
- **Tests interfaces** : Mocking tkinter permet validation logique métier sans affichage
- **Préparation OpenAI** : Placeholders informatifs facilitent développement itératif

### Leçons apprises (Phase 6)
- **Intégration API externe** : Threading essentiel pour éviter blocage interface lors d'appels réseau
- **Gestion prompts** : Localisation centralisée dans `openai_service.py` facilite maintenance
- **UX progression** : Barres de progression et boutons annuler critiques pour longues opérations
- **Fallback robuste** : Retour au texte original en cas d'erreur API préserve données utilisateur
- **Architecture modulaire** : Service dédié OpenAI permet tests et maintenance séparés
- **Configuration flexible** : Variables d'environnement pour clés API sécurisent déploiement
- **Fonctionnalités duales** : Actions globales ET individuelles répondent aux besoins utilisateur

### Leçons apprises (Phase 7)
- **Réutilisation architecture** : Baser une nouvelle fenêtre sur l'existante accélère développement
- **Interface conseil dédiée** : Vue synthèse + détails répond aux besoins spécifiques du conseil de classe
- **Calculs d'évolution** : Indicateurs visuels (↗️ ↘️ ➡️) améliorent la lisibilité des données  
- **Vues duales** : Synthèse pour vision globale, détails pour analyse approfondie
- **Gestion modèles** : Structure dictionnaire `matieres` plus flexible que liste pour accès direct
- **Tests interface** : Mocking avancé tkinter nécessaire pour tester widgets complexes
- **Placeholders préparatoires** : Boutons avec messages informatifs facilitent développement itératif
- **Scrolling dynamique** : Canvas + Frame scrollable essentiel pour contenu variable
- **Affichage HTML** : Interprétation des balises via regex et tags tkinter sans dépendances externes
- **Formatage dynamique** : Balises `<span class="positif/negatif">` permettent mise en forme contextuelle

### Amélioration Post-Phase 7 : Interface Conseil Plein Écran 1080p
- **Date d'implémentation** : 21/01/2025
- **Fonctionnalité ajoutée** : Optimisation de l'interface conseil pour écran 1080p en mode plein écran
- **Localisation** : `src/gui/conseil_window.py` avec refactorisation complète de l'interface
- **Améliorations clés** :
  - **Mode plein écran automatique** : Activation automatique avec gestion robuste multi-plateforme
  - **Zones d'appréciations optimisées** : Hauteur passée de 2 à 6 lignes (3x plus d'espace)
  - **Affichage côte à côte** : S1 et S2 en colonnes séparées dans la vue détaillée
  - **Scrollbars individuelles** : Chaque zone d'appréciation a sa propre scrollbar
  - **Layout compact** : Informations élève et appréciations générales plus compactes
  - **Police agrandie** : Arial 11 pour une meilleure lisibilité
  - **Navigation améliorée** : Liste des bulletins avec plus de hauteur (25 entrées)
  - **Raccourcis clavier** : Échap et F11 pour basculer le plein écran
  - **Scroll molette** : Support de la molette de souris dans les appréciations
- **Script de démonstration** : `demo_conseil_fullscreen.py` pour tester l'interface
- **Compatibilité** : Gestion robuste Windows/Linux avec fallbacks automatiques
- **Avantage utilisateur** : Utilisation optimale de l'espace écran pour la lecture des appréciations

### Nouvelle Fonctionnalité : Configuration IA Multi-Fournisseurs avec Tests de Connexion
- **Date d'implémentation** : 01/07/2025
- **Fonctionnalité ajoutée** : Interface de configuration complète pour OpenAI, Anthropic Claude et Google Gemini avec tests de connexion en temps réel
- **Localisation** : 
  - `src/gui/config_window.py` - Interface de configuration avec onglets
  - `src/services/ai_config_service.py` - Service de gestion des configurations IA
  - `src/services/ai_connection_test_service.py` - Service de test de connexion IA
- **Améliorations clés** :
  - **Interface multi-fournisseurs** : Onglets dédiés pour OpenAI, Anthropic et Google Gemini
  - **Gestion des clés API** : Champs masqués avec bouton afficher/masquer pour la sécurité
  - **Sélection de modèles** : Listes déroulantes avec modèles prédéfinis pour chaque fournisseur
  - **Boutons radio exclusifs** : Sélection du fournisseur actif (un seul à la fois)
  - **Tests de connexion réels** : Validation en temps réel des clés API et modèles
  - **Feedback détaillé** : Messages d'erreur spécifiques selon le type d'erreur (clé invalide, modèle non trouvé, etc.)
  - **Gestion d'erreurs robuste** : Détection automatique des clients manquants avec instructions d'installation
  - **Threading asynchrone** : Tests en arrière-plan sans blocage de l'interface
  - **Stockage sécurisé** : Configuration sauvegardée dans fichier `.env` local
- **Dépendances mises à jour** :
  - `openai>=1.56.0` - Client OpenAI avec endpoint responses
  - `anthropic>=0.39.0` - Client officiel Claude 3.7
  - `google-generativeai>=0.8.7` - Client officiel Gemini 2.0
- **Modèles supportés** :
  - **OpenAI** : gpt-5.1, gpt-5.1-mini, gpt-5.1-nano, gpt-4.1, o3-mini
  - **Anthropic** : claude-3.7-sonnet, claude-3.7-haiku, claude-3.5-sonnet, claude-3.5-haiku
  - **Google Gemini** : gemini-2.0-pro, gemini-2.0-flash, gemini-2.0-flash-lite, gemini-1.5-pro
- **Scripts de démonstration** :
  - `demo_config_ia.py` - Test de l'interface de configuration
  - `demo_test_connexion_ia.py` - Démonstration complète des tests de connexion
- **Tests unitaires** : `tests/test_connection_service.py` - 15 tests unitaires (100% de réussite)
- **Documentation** : `README_CONFIG_IA.md` - Guide utilisateur complet
- **Intégration interface** : Bouton "🤖 Configuration IA" ajouté dans la fenêtre principale
- **Avantage utilisateur** : Configuration simplifiée multi-fournisseurs avec validation immédiate des clés API

### Configuration IA Multi-Fournisseurs
- **Fichier de configuration** : `.env` à la racine du projet contenant les clés API et modèles
- **Interface de configuration** : Fenêtre dédiée accessible via bouton "🤖 Configuration IA" dans la fenêtre principale
- **Fournisseurs supportés** : OpenAI, Anthropic Claude, Google Gemini
- **Sécurité** : Fichier `.env` ajouté au `.gitignore` pour éviter le partage accidentel des clés API
- **Variables d'environnement** :
  - `OPENAI_API_KEY` : Clé API OpenAI
  - `ANTHROPIC_API_KEY` : Clé API Anthropic
  - `GOOGLE_API_KEY` : Clé API Google Gemini
  - `OPENAI_MODEL` : Modèle OpenAI sélectionné
  - `ANTHROPIC_MODEL` : Modèle Anthropic sélectionné
  - `GEMINI_MODEL` : Modèle Gemini sélectionné
  - `AI_ENABLED_PROVIDER` : Fournisseur actif (openai/anthropic/gemini)
- **Configuration manuelle** : Éditer directement le fichier `.env` ou utiliser l'interface graphique
- **Tests de connexion** : Validation automatique des clés API et modèles via l'interface
- **Services principaux** :
  - `src/services/ai_config_service.py` : Gestion centralisée des configurations
  - `src/services/ai_connection_test_service.py` : Tests de connexion en temps réel
  - `src/services/openai_service.py` : Service OpenAI existant (prétraitement et génération)
- **Dépendances requises** : Clients officiels installés automatiquement via `requirements.txt`

### Points de validation utilisateur requis
- [x] Validation de la structure des données (Phase 2) ✅
- [ ] Validation de l'interface principale (Phase 4)
- [ ] Validation de l'interface d'édition (Phase 5)
- [ ] Définition des besoins fenêtre conseil (Phase 7)
- [ ] Tests utilisateur final (Phase 8)

---

## 🧊 BACKLOG / À REVENIR PLUS TARD

### Support des LLM locaux (Ollama) — RETIRÉ temporairement
- **Date du retrait** : 13/06/2026
- **Décision** : Le support des LLM locaux (provider `LOCAL` / Ollama) a été **retiré** lors de
  la refonte multi-fournisseurs orientée publication (OpenAI + Anthropic + Gemini uniquement).
- **Raison** : Hors périmètre de la version publique actuelle ; à réintégrer proprement plus tard.
- **Éléments supprimés** :
  - `demo_test_local_provider.py` (démo d'intégration Ollama)
  - `demo_config_local.py` (démo de configuration LOCAL)
  - `README_LOCAL_PROVIDER.md` (documentation du provider local)
  - Valeur `AIProvider.LOCAL` de l'énumération (déjà absente du code `src/`)
- **Pour réintégrer** (TODO futur) :
  - Ajouter `LOCAL = "local"` dans `AIProvider` (`src/services/ai_config_service.py`)
  - Modèles/URL par défaut (ex. `http://localhost:11434`, `llama3.x`) + gestion `base_url`
  - Backend d'appel dans `AIService` (`src/services/openai_service.py`) :
    soit client OpenAI-compatible Ollama, soit appels HTTP directs
  - Test de connexion dédié dans `ai_connection_test_service.py`
  - Récupération dynamique des modèles via l'API Ollama (`/api/tags`)
  - Onglet correspondant dans `config_window.py` (généré automatiquement via l'enum)
  - Restaurer les démos/README supprimés (historiques disponibles dans git)

---

## 📦 PACKAGING & CI (13/06/2026)

### Build portable (PyInstaller, fichier unique)
- **Spec** `build_config/pyconseil.spec` mis à jour :
  - SDK Gemini : `google.generativeai` → `google.genai` (+ `google.genai.types`)
  - Collecte automatique des sous-modules (`collect_submodules`) pour `google.genai`,
    `anthropic`, `openai` ; ajout de `openpyxl` (lecture `.xlsx`)
  - Toujours un binaire **onefile** (Windows `.exe`, Linux ELF embarqué dans l'AppImage)
- **`.env` portable** : `resolve_env_path()` (`ai_config_service.py`) recherche le `.env`
  - à côté du `.AppImage` (variable `APPIMAGE`),
  - sinon à côté de l'exécutable PyInstaller (`sys.frozen`),
  - sinon à la racine du projet (mode source).

### GitHub Actions (`.github/workflows/build-and-release.yml`)
- 2 jobs de build : **AppImage Linux** + **EXE Windows portable**, Python 3.11.
- AppImage construit avec `APPIMAGE_EXTRACT_AND_RUN=1` (évite la dépendance FUSE).
- `permissions: contents: write` + `concurrency` (annule les runs obsolètes).
- Job `create-release` (sur tag `v*`) publie AppImage + EXE + checksums `.sha256`
  via `softprops/action-gh-release@v2`.

### Dépendances
- `requirements.txt` (runtime) : ajout de `pandas` et `openpyxl` (lecture des bulletins).
- `build_config/requirements_build.txt` : aligné sur `google-genai`, `openpyxl`, `pyinstaller>=6.6`.

---

**Document version 1.7 - Packaging PyInstaller onefile + CI (AppImage Linux / EXE Windows), .env portable (13/06/2026)**
**Document version 1.6 - Refonte multi-fournisseurs (OpenAI/Anthropic/Gemini), deux modèles par rôle, sécurisation des secrets ; LLM locaux retirés et mis en backlog (13/06/2026)**