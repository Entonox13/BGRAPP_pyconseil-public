# 🤖 Configuration IA Multi-Fournisseurs - Guide d'utilisation

## 📋 Vue d'ensemble

La fonctionnalité de **Configuration IA Multi-Fournisseurs** permet à l'application BGRAPP Pyconseil de supporter plusieurs fournisseurs d'intelligence artificielle :

- **OpenAI** (GPT-4, GPT-3.5, etc.)
- **Anthropic Claude** (Claude-3.5 Sonnet, Haiku, etc.)  
- **Google Gemini** (Gemini-1.5 Pro, Flash, etc.)

## ⚡ Accès rapide

### 1. Ouvrir la configuration
- Lancer l'application : `python main.py`
- Cliquer sur le bouton **"🤖 Configuration IA"** dans la section Navigation

### 2. Configurer un fournisseur
1. Sélectionner l'onglet du fournisseur souhaité
2. Renseigner votre **clé API**
3. Choisir le **modèle** dans la liste déroulante
4. Cocher **"Utiliser [Fournisseur]"** pour le définir comme actif
5. Cliquer **"💾 Sauvegarder"**

> **Note** : Les boutons radio permettent de sélectionner un seul fournisseur actif à la fois. Le fournisseur sélectionné sera automatiquement utilisé par l'application.

## 🔑 Obtenir les clés API

### OpenAI
- Site : https://platform.openai.com/api-keys
- Créer un compte OpenAI
- Générer une nouvelle clé API
- Format : `sk-...` (commence par sk-)

### Anthropic Claude  
- Site : https://console.anthropic.com/
- Créer un compte Anthropic
- Aller dans "API Keys" 
- Générer une nouvelle clé
- Format : `sk-ant-...`

### Google Gemini
- Site : https://makersuite.google.com/app/apikey
- Connexion avec compte Google
- Créer une clé API pour Gemini
- Format : `AI...`

## 🎯 Modèles recommandés

### Pour un usage équilibré (performance/coût)
- **OpenAI** : `gpt-4o-mini-2024-07-18`
- **Anthropic** : `claude-3-5-haiku-20241022`
- **Gemini** : `gemini-1.5-flash`

### Pour une performance maximale
- **OpenAI** : `gpt-4o`
- **Anthropic** : `claude-3-5-sonnet-20241022`
- **Gemini** : `gemini-1.5-pro`

## �� Configuration fichier .env

Le fichier `.env` est automatiquement créé et géré par l'interface. Structure :

```bash
# Clés API des fournisseurs
OPENAI_API_KEY=sk-votre-clé-openai-ici
ANTHROPIC_API_KEY=sk-ant-votre-clé-anthropic-ici
GOOGLE_API_KEY=votre-clé-google-ici

# Modèles configurés
OPENAI_MODEL=gpt-4o-mini-2024-07-18
ANTHROPIC_MODEL=claude-3-5-haiku-20241022
GEMINI_MODEL=gemini-1.5-flash

# Fournisseur actif
AI_ENABLED_PROVIDER=openai
```

## 🔒 Sécurité

### Protection des clés API
- ✅ Stockage local uniquement (fichier `.env`)
- ✅ Masquage dans l'interface (`****`)
- ✅ Exclusion du contrôle de version (`.gitignore`)
- ✅ Aucun envoi vers des serveurs externes

## 🧪 Test et validation

### Script de démonstration
```bash
python demo_config_ia.py
```

### Tests unitaires
```bash
python -m pytest tests/test_config_window.py -v
```

## 📞 Support

### Fichiers concernés
- **Interface** : `src/gui/config_window.py`
- **Service** : `src/services/ai_config_service.py`
- **Tests** : `tests/test_config_window.py`
- **Démo** : `demo_config_ia.py`

---

**Version** : 1.0 (22/01/2025)  
**Compatibilité** : BGRAPP Pyconseil Phase 7+
