# 📋 Structure du fichier source.xlsx

## Vue d'ensemble

Le fichier `source.xlsx` est le fichier de référence qui contient la liste des élèves et leurs appréciations générales. Il doit être placé dans votre dossier de travail avec les fichiers CSV des matières.

## Structure requise

### Colonnes obligatoires

| Colonne | Description | Format | Exemple |
|---------|-------------|--------|---------|
| `Élève` | Nom complet de l'élève | "NOM Prenom" | "DUPONT Alice" |

### Colonnes optionnelles

| Colonne | Description | Format | Exemple |
|---------|-------------|--------|---------|
| `AppreciationGeneraleS1` | Appréciation générale du 1er semestre | Texte libre | "Élève sérieuse et appliquée." |
| `Appreciation S1` | Variante acceptée pour S1 | Texte libre | "Bon travail d'ensemble." |
| `AppreciationS1` | Variante acceptée pour S1 | Texte libre | "Travail satisfaisant." |
| `AppreciationGeneraleS2` | Appréciation générale du 2e semestre | Texte libre | "Des efforts constants." |
| `Appreciation S2` | Variante acceptée pour S2 | Texte libre | "Très bonne progression." |
| `AppreciationS2` | Variante acceptée pour S2 | Texte libre | "Excellente année." |

## Format du nom d'élève

Le nom doit être au format **"NOM Prenom"** (majuscules pour le nom, première lettre en majuscule pour le prénom) :

- ✅ **Correct** : "DUPONT Alice", "MARTIN Pierre", "BERNARD Sophie"
- ❌ **Incorrect** : "Dupont Alice", "MARTIN pierre", "Bernard Sophie"

L'application sépare automatiquement le nom et le prénom en se basant sur la casse.

## Exemple de fichier

Un fichier `source.xlsx` exemple est disponible dans ce dossier (`exemples/source.xlsx`) avec la structure complète.

### Contenu exemple

```
Élève              | AppreciationGeneraleS1                          | AppreciationGeneraleS2
-------------------|------------------------------------------------|-----------------------
DUPONT Alice       | Élève sérieuse et appliquée. Bon travail.      | (vide ou None)
MARTIN Pierre      | Bon élève, participation active en cours.     | (vide ou None)
BERNARD Sophie     | Travail satisfaisant, peut encore progresser.| (vide ou None)
```

## Utilisation

1. **Créer votre fichier source.xlsx** avec Excel ou un tableur compatible
2. **Placer la colonne "Élève" en première colonne** (recommandé)
3. **Remplir les appréciations S1** si vous avez déjà les données du semestre précédent
4. **Laisser S2 vide** si vous souhaitez que l'IA génère les appréciations générales S2

## Cas spécifiques Semestre 1

Lorsqu'on prépare le premier semestre :

- Il est normal que `AppreciationGeneraleS1` soit vide dans `source.xlsx`. L'application ne l'exigera pas.
- Les fichiers CSV Pronote contiennent généralement les colonnes `Moy. S1`, `H.Abs.` et `App. A : Appréciations`. Ces colonnes seront automatiquement mappées sur les champs S1 des bulletins.
- Aucun historique S2 n'étant disponible, les interfaces (édition + conseil) masquent les colonnes Évolution/S2 pour éviter tout bruit visuel.
- Le semestre détecté est indiqué dans le bloc `_metadata` du `output.json`, ce qui permet de rouvrir le fichier en conservant la configuration S1.

## Notes importantes

- Le fichier doit être au format **Excel (.xlsx)**
- La première ligne doit contenir les **en-têtes de colonnes**
- La colonne `Élève` est **obligatoire** et doit être présente
- Les autres colonnes sont **optionnelles** mais recommandées
- Les noms d'élèves doivent correspondre exactement à ceux dans les fichiers CSV des matières

## Compatibilité avec les fichiers CSV

Les noms d'élèves dans `source.xlsx` doivent **correspondre exactement** aux noms dans les fichiers CSV des matières pour que l'application puisse faire le lien entre les données.

Exemple de correspondance :
- `source.xlsx` : "DUPONT Alice"
- `mathematiques.csv` : "DUPONT Alice" ✅
- `francais.csv` : "DUPONT Alice" ✅

## Génération automatique des appréciations S2

Si la colonne `AppreciationGeneraleS2` est vide ou absente, l'application peut générer automatiquement les appréciations générales S2 à partir des appréciations par matière du S2 en utilisant l'IA configurée.

---

**📁 Fichier exemple disponible** : `exemples/source.xlsx`

