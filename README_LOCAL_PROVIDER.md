# 🦙 Provider LOCAL - Guide d'utilisation

## Vue d'ensemble

Le **provider LOCAL** permet d'utiliser des modèles de langage (LLM) qui tournent localement sur votre machine. Cette fonctionnalité offre plusieurs avantages :

- 🔒 **Confidentialité totale** : Vos données ne quittent jamais votre machine
- 💰 **Aucun coût d'API** : Pas de frais d'utilisation comme avec les services cloud
- 🎛️ **Contrôle total** : Choix du modèle, paramètres personnalisés
- 🚀 **Latence réduite** : Pas de délai de réseau
- 🌐 **Disponibilité offline** : Fonctionne sans connexion internet

## Solutions supportées

Le provider LOCAL est compatible avec toute solution exposant une **API compatible OpenAI** :

### 🦙 Ollama (Recommandé)
- **URL par défaut** : `http://localhost:11434`
- **Installation** : [ollama.ai](https://ollama.ai/)
- **Avantages** : Simple, léger, gestion automatique des modèles
- **Commandes de base** :
  ```bash
  # Installation d'un modèle
  ollama pull llama3.2
  
  # Démarrage interactif
  ollama run llama3.2
  
  # Démarrage en arrière-plan
  ollama serve
  ```

### 🖥️ LM Studio
- **URL par défaut** : `http://localhost:1234`
- **Installation** : [lmstudio.ai](https://lmstudio.ai/)
- **Avantages** : Interface graphique, gestion facile des modèles

### 🐍 Text Generation WebUI (oobabooga)
- **URL par défaut** : `http://localhost:5000` (ou custom)
- **Installation** : [GitHub](https://github.com/oobabooga/text-generation-webui)
- **Avantages** : Interface web complète, nombreux paramètres

## Configuration

### 1. Installation du serveur local

**Option A - Ollama (Recommandé pour débutants)** :
```bash
# Télécharger depuis https://ollama.ai/
# Puis installer un modèle
ollama pull llama3.2
ollama run llama3.2
```

**Option B - LM Studio** :
1. Télécharger depuis [lmstudio.ai](https://lmstudio.ai/)
2. Télécharger un modèle depuis l'interface
3. Démarrer le serveur local

### 2. Configuration dans BGRAPP Pyconseil

1. **Lancer l'interface de configuration** :
   ```bash
   python demo_config_local.py
   ```

2. **Dans l'interface** :
   - Sélectionner l'onglet **"LLM Local"**
   - Configurer l'**URL du serveur** (ex: `http://localhost:11434`)
   - Choisir le **modèle** installé
   - Cocher **"Utiliser LLM Local"**
   - Cliquer sur **"Tester la connexion"**
   - **Sauvegarder** la configuration

### 3. Modèles recommandés

| Modèle | Taille | RAM requise | Vitesse | Qualité |
|--------|---------|-------------|---------|---------|
| `llama3.2` | 3B | 4 GB | ⚡⚡⚡ | ⭐⭐⭐ |
| `llama3.1` | 8B | 8 GB | ⚡⚡ | ⭐⭐⭐⭐ |
| `mistral` | 7B | 8 GB | ⚡⚡ | ⭐⭐⭐⭐ |
| `qwen2.5` | 7B | 8 GB | ⚡⚡ | ⭐⭐⭐⭐ |
| `codellama` | 7B | 8 GB | ⚡⚡ | ⭐⭐⭐⭐⭐ |

## Test et validation

### Test automatique
```bash
# Test complet de l'intégration
python demo_test_local_provider.py

# Démonstration avec interface
python demo_config_local.py
```

### Test manuel
1. **Vérifier que le serveur local tourne** :
   ```bash
   curl http://localhost:11434/api/version  # Pour Ollama
   curl http://localhost:1234/v1/models    # Pour LM Studio
   ```

2. **Tester dans l'interface** :
   - Ouvrir l'interface de configuration
   - Aller sur l'onglet "LLM Local"
   - Cliquer sur "Tester la connexion"

## Utilisation

Une fois configuré, le provider LOCAL fonctionne exactement comme les autres providers :

```python
from src.services.openai_service import get_ai_service
from src.services.ai_config_service import AIProvider

# Obtenir le service IA configuré pour LOCAL
ai_service = get_ai_service(provider=AIProvider.LOCAL)

# Utiliser comme un service IA standard
appreciation = ai_service.preprocess_appreciation(
    "L'élève fait de bons efforts en mathématiques.",
    student_nom="Dupont",
    student_prenom="Marie"
)
```

## Dépannage

### ❌ "Impossible de se connecter au serveur local"
- **Vérifiez que le serveur est démarré** : `ollama list` ou vérifier LM Studio
- **Vérifiez l'URL** : Par défaut `http://localhost:11434` pour Ollama
- **Vérifiez le port** : Peut être occupé par un autre processus

### ❌ "Modèle non trouvé"
- **Ollama** : `ollama pull nom_du_modele`
- **LM Studio** : Télécharger le modèle via l'interface
- **Vérifiez le nom exact** : `ollama list` pour voir les modèles disponibles

### ❌ "Client OpenAI non installé"
```bash
pip install openai>=1.0.0
```

### ❌ Performances lentes
- **Vérifiez la RAM disponible** : Fermez les applications inutiles
- **Utilisez un modèle plus petit** : `llama3.2` au lieu de `llama3.1`
- **GPU** : Certaines solutions supportent l'accélération GPU

## Avantages vs inconvénients

### ✅ Avantages
- **Confidentialité maximale** : Données privées
- **Pas de coûts d'API** : Utilisation illimitée
- **Latence faible** : Pas de réseau
- **Contrôle total** : Paramètres personnalisables
- **Disponibilité offline** : Fonctionne sans internet

### ⚠️ Inconvénients
- **Ressources locales** : Nécessite RAM/CPU suffisants
- **Configuration initiale** : Plus complexe que les APIs cloud
- **Qualité variable** : Dépend du modèle choisi
- **Maintenance** : Mises à jour manuelles des modèles

## Sécurité et confidentialité

Le provider LOCAL garantit une **confidentialité totale** :

- ✅ **Aucune donnée transmise** vers des serveurs externes
- ✅ **Traitement 100% local** sur votre machine
- ✅ **Conformité RGPD native** : Les données ne quittent pas votre environnement
- ✅ **Pas de logs externes** : Aucun historique chez des tiers
- ✅ **Contrôle total** sur le stockage et le traitement

## Support et communauté

- 📖 **Documentation Ollama** : [docs.ollama.ai](https://docs.ollama.ai/)
- 💬 **Communauté Ollama** : [GitHub Discussions](https://github.com/ollama/ollama/discussions)
- 🐛 **Signaler un bug** : Créer une issue dans le projet BGRAPP
- 💡 **Suggestions** : Proposer des améliorations

---

*Le provider LOCAL transforme votre machine en une puissante plateforme IA privée et gratuite ! 🚀* 