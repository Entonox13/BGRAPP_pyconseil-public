# 🔒 DONNÉES ANONYMISÉES - PROTECTION RGPD

## ⚠️ IMPORTANT - CONFIDENTIALITÉ DES DONNÉES

Ce dossier `exemples/` ne contient **plus** de données personnelles réelles d'élèves pour des raisons de **conformité RGPD**.

### 🗂️ Fichiers supprimés pour protection

Les fichiers suivants ont été supprimés car ils contenaient de vrais noms d'élèves :
- `source.xlsx` (liste des élèves)
- `*.csv` (appréciations par matière)
- `output.json` (bulletins générés)
- `exempleconseil.xlsx` (exemple conseil)

### ✅ Fichiers conservés (sécurisés)

- `exemple.json` : Structure JSON avec noms anonymisés (MARTIN Sarah)

## 🚀 UTILISATION AVEC VOS DONNÉES RÉELLES

### 1. Préparation de votre dossier de données

Créez un dossier **privé** (non versionné) avec vos fichiers :

```
mon_dossier_prive/
├── source.xlsx           # Votre liste d'élèves
├── mathematiques.csv     # Vos données de maths
├── francais.csv         # Vos données de français
├── histoire.csv         # Vos données d'histoire
├── Anglais LV1.csv      # Vos données d'anglais
└── ...                  # Autres matières
```

### 2. Lancement de l'application

1. **Lancez l'application principale** :
   ```bash
   python main.py
   ```

2. **Sélectionnez votre dossier privé** via le bouton "Choisir dossier de travail"

3. **Générez le JSON** avec le bouton "Créer JSON"

4. **Utilisez les fenêtres d'édition et conseil** normalement

### 3. Anonymisation automatique RGPD 🔒

L'application intègre un système d'**anonymisation automatique** :

- ✅ **Avant envoi OpenAI** : "Suheda" → "John"
- ✅ **Après réception** : "John" → "Suheda"  
- ✅ **Transparence totale** : Vous voyez toujours les vrais noms
- ✅ **Conformité RGPD** : Seuls des pseudonymes transitent vers OpenAI

**Aucun nom réel d'élève n'est envoyé à l'API OpenAI.**

## 🛡️ SÉCURITÉ DE VOS DONNÉES

### Fichiers automatiquement ignorés par Git

Le fichier `.gitignore` a été mis à jour pour **ignorer automatiquement** :
- `output*.json` (vos bulletins générés)
- `source*.xlsx` (vos listes d'élèves) 
- `*.csv` (vos appréciations par matière)
- Dossiers `donnees_reelles/` et `data_personnelles/`

### Recommandations

1. **Créez un dossier privé** en dehors du repository Git
2. **Sauvegardez vos données** de manière sécurisée
3. **Ne partagez jamais** les fichiers contenant de vrais noms
4. **Utilisez l'anonymisation OpenAI** (activée par défaut)

## 🧪 TESTS ET DÉMONSTRATIONS

Tous les scripts de démonstration utilisent des **données anonymisées** :

- `demo_rgpd_anonymization.py` : Utilise de vrais noms **uniquement** pour démontrer l'anonymisation
- `demo_html_conseil.py` : Utilise MARTIN Alice, DUPONT Paul (anonymisés)
- `demo_conseil_fullscreen.py` : Références aux fichiers utilisateur (sécurisés)

## 🔧 DÉVELOPPEMENT

Si vous développez des fonctionnalités :

1. **Toujours utiliser des noms fictifs** dans vos tests
2. **Vérifier le .gitignore** avant commit
3. **Tester l'anonymisation RGPD** avec de vrais noms localement

## 📞 SUPPORT

En cas de question sur la protection des données ou l'utilisation :
- Consultez la documentation principale
- Vérifiez les tests unitaires d'anonymisation
- Contactez l'équipe de développement

---

**🔒 Cette application respecte le RGPD et protège automatiquement les données personnelles de vos élèves.** 