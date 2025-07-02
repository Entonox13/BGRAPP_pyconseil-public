# PHASE 2 - ANALYSE ET MODÉLISATION DES DONNÉES

## 📊 Analyse des fichiers sources

### Fichier source.xlsx
**Structure identifiée :**
- **Colonnes :** 
  - `Élève` : Nom complet au format "NOM Prenom" (ex: "ARAZAD Nada")
  - `Appreciation S1` : Appréciation générale du premier semestre
- **Nombre d'élèves :** 24 élèves dans l'exemple
- **Format :** Excel (.xlsx) avec en-têtes en première ligne

### Fichiers CSV par matière
**Structure commune :**
- `Élève` : Nom complet de l'élève
- `H.Abs.` : Heures d'absence (format "3h00", "1h30", etc.)
- `Ret.` : Retards (numérique)
- `Evol.` : Évolution (HTML avec balises div)
- `Rappel de la période précédente : S1` : Données du S1 avec moyennes et appréciations
- `N.Notes` : Nombre de notes (format "8 sur 8")
- `Moy. S2` : Moyenne du second semestre (format "14,50")
- `Année` : Moyenne annuelle
- `Eval.` : Évaluations détaillées
- `App. A : Appréciations` : Appréciations du second semestre

**Matières disponibles :**
- ✅ `Anglais LV1.csv` (existant)
- ✅ `Arts Plastiques.csv` (existant)
- ✅ `Allemand LV2.csv` (existant)
- ✅ `mathematiques.csv` (créé)
- ✅ `francais.csv` (créé)
- ✅ `histoire.csv` (créé)

## 🏗️ Modèles de données créés

### Classe `Eleve`
```python
@dataclass
class Eleve:
    nom: str
    prenom: str
    classe: Optional[str] = None
```
**Fonctionnalités :**
- Création depuis nom complet avec `from_full_name()`
- Séparation automatique nom/prénom basée sur la casse
- Support des noms composés

### Classe `AppreciationMatiere`
```python
@dataclass  
class AppreciationMatiere:
    matiere: str
    heures_absence_s1: Optional[int] = None
    heures_absence_s2: Optional[int] = None
    moyenne_s1: Optional[float] = None
    moyenne_s2: Optional[float] = None
    moyenne_s1_max: Optional[float] = None
    moyenne_s1_min: Optional[float] = None
    moyenne_s2_max: Optional[float] = None  
    moyenne_s2_min: Optional[float] = None
    appreciation_s1: Optional[str] = None
    appreciation_s2: Optional[str] = None
```
**Fonctionnalités :**
- Conversion vers/depuis dictionnaire JSON
- Gestion des valeurs optionnelles
- Support des moyennes min/max de classe

### Classe `Bulletin`
```python
@dataclass
class Bulletin:
    eleve: Eleve
    appreciation_generale_s1: Optional[str] = None
    appreciation_generale_s2: Optional[str] = None
    matieres: Dict[str, AppreciationMatiere] = field(default_factory=dict)
```
**Fonctionnalités :**
- Gestion des appréciations générales S1 et S2
- Collection de matières avec dictionnaire
- Sérialisation/désérialisation JSON complète
- Méthodes d'ajout et récupération de matières

## 🔧 Fonctions utilitaires

### `parse_heures_absence(heures_str)`
Parse les heures d'absence depuis format texte ("3h00" → 3)

### `parse_moyenne(moyenne_str)`
Parse les moyennes depuis format français ("14,50" → 14.5)
Gère les cas spéciaux comme "N.Not"

## 📁 Structure JSON cible

**Format conforme à `exemple.json` :**
```json
{
  "Nom": "DUPONT",
  "Prenom": "Alice", 
  "AppreciationGeneraleS1": "Bon travail d'ensemble",
  "AppreciationGeneraleS2": "Des efforts constants",
  "Matieres": {
    "Mathematiques": {
      "HeuresAbsenceS1": 3,
      "HeuresAbsenceS2": 2,
      "MoyenneS1": 14.5,
      "MoyenneS2": 13.0,
      "MoyenneS1Max": 18.5,
      "MoyenneS1Min": 9.0,
      "AppreciationS1": "Bon travail d'ensemble",
      "AppreciationS2": "Des efforts constants"
    }
  }
}
```

## ✅ Validation

### Tests unitaires
- **16 tests créés** dans `tests/test_models.py`
- **Couverture complète** des classes et fonctions
- **Tous les tests passent** ✅

### Fichiers d'exemple
- ✅ **source.xlsx** : 24 élèves avec appréciations S1
- ✅ **exemple.json** : Structure de référence (préservée)
- ✅ **CSV matières** : 6 matières avec données complètes

## 📋 Relations entre données identifiées

1. **Élève → Bulletin** : Un bulletin par élève
2. **Bulletin → Matières** : Plusieurs matières par bulletin  
3. **Source.xlsx → Appréciations générales S1**
4. **CSV matières → Appréciations par matière S1 et S2**
5. **Calculs automatiques** : Min/Max de moyennes par classe et matière

## 🎯 Prochaines étapes (Phase 3)

La modélisation est complète et validée. La Phase 3 pourra :
- Utiliser ces modèles pour lire les fichiers sources
- Implémenter la logique de traitement des données
- Générer le fichier `output.json` conforme

---

**Phase 2 - TERMINÉE** ✅
- [x] 2.1 Analyse des fichiers source
- [x] 2.2 Création du modèle de données  
- [x] 2.3 Fichier exemple.json (préservé)
- [x] 2.4 Fichiers de test (complétés) 