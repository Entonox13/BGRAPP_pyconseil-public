# 🤖 Configuration IA - Guide d'utilisation

## Vue d'ensemble

L'application supporte **plusieurs fournisseurs d'IA** :
- **OpenAI** : appels via la **Responses API**
- **Anthropic (Claude)** : appels via la **Messages API**
- **Google (Gemini)** : appels via **google-genai**

Pour chaque fournisseur, vous configurez une clé API et **deux modèles** :
- un modèle de **prétraitement** (mise en forme HTML des appréciations par matière) ;
- un modèle d'**appréciation** (rédaction de l'appréciation générale).

Cela permet par exemple d'utiliser un modèle économique pour le prétraitement et
un modèle plus qualitatif pour l'appréciation finale. Un seul fournisseur est
actif à la fois (sélectionné dans l'interface).

## Configuration rapide

1. Copier `env.example` vers `.env` à la racine du projet :
   ```bash
   cp env.example .env
   ```
2. Ouvrir l'application (`python main.py`)
3. Cliquer sur **"🤖 Configuration IA"**
4. Dans l'onglet du fournisseur souhaité : saisir la clé API et choisir le modèle
5. Cocher le fournisseur à utiliser (fournisseur actif)
6. Tester la connexion
7. Sauvegarder

> Important : le code lit uniquement le fichier `.env` (jamais `env.example`).

## Obtenir une clé API

- OpenAI : https://platform.openai.com/api-keys (format `sk-...`)
- Anthropic (Claude) : https://console.anthropic.com/settings/keys (format `sk-ant-...`)
- Google (Gemini) : https://aistudio.google.com/app/apikey

## Exemple de `.env`

```bash
# Fournisseur actif : openai | anthropic | gemini
AI_ENABLED_PROVIDER=openai

OPENAI_API_KEY=
OPENAI_MODEL_PREPROCESS=gpt-5-mini
OPENAI_MODEL_GENERATION=gpt-5-mini

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL_PREPROCESS=claude-sonnet-4-6
ANTHROPIC_MODEL_GENERATION=claude-sonnet-4-6

GEMINI_API_KEY=
GEMINI_MODEL_PREPROCESS=gemini-2.5-flash
GEMINI_MODEL_GENERATION=gemini-2.5-flash
```

> Astuce : l'ancienne variable unique (`OPENAI_MODEL`, etc.) reste prise en
> compte comme valeur de repli si les variables par rôle ne sont pas définies.

Un `env.example` est fourni à la racine du projet.

## Dépendances

```bash
pip install -r requirements.txt
```

Les clients installés : `openai`, `anthropic`, `google-genai`.

## Sécurité

- stockage local dans `.env` (ignoré par git, ne jamais le committer)
- clé masquée dans l'interface
- aucune transmission hors de l'appel API du fournisseur choisi
