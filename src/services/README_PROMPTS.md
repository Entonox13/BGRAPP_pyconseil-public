# 📝 Gestion des Prompts IA

## Emplacement

Les prompts utilisés pour les appels API IA sont maintenant centralisés dans le fichier :
- **`src/services/prompts.py`**

## Prompts disponibles

### 1. Prompt de prétraitement (`PROMPT_PREPROCESS_APPRECIATION`)

**Utilisation** : Ajoute des balises HTML aux appréciations par matière pour mettre en évidence les aspects positifs et négatifs.

**Fonction** : `get_preprocess_prompt()`

**Emplacement dans le code** : Utilisé dans `AIService.preprocess_appreciation()`

### 2. Prompt de génération générale (`PROMPT_GENERATE_GENERAL_APPRECIATION_TEMPLATE`)

**Utilisation** : Génère l'appréciation générale S2 à partir des appréciations par matière.

**Fonction** : `get_generate_general_prompt(appreciations_text: str, semester_label: str = "Semestre 2")`

**Emplacement dans le code** : Utilisé dans `AIService.generate_general_appreciation()`

## Modification des prompts

Pour modifier un prompt :

1. **Ouvrir** `src/services/prompts.py`
2. **Modifier** la constante correspondante :
   - `PROMPT_PREPROCESS_APPRECIATION` pour le prétraitement
   - `PROMPT_GENERATE_GENERAL_APPRECIATION_TEMPLATE` pour la génération générale
3. **Sauvegarder** le fichier
4. **Redémarrer** l'application pour que les changements prennent effet

## Structure des prompts

### Prompt de prétraitement

Le prompt de prétraitement doit :
- Demander d'ajouter des balises HTML `<span class="positif">` et `<span class="negatif">`
- Ne pas modifier le contenu du texte
- Répondre uniquement par le texte traité (sans explications)

### Prompt de génération générale

Le prompt de génération utilise un template avec placeholder `{appreciations_text}` qui sera remplacé par les appréciations par matière.

Le prompt doit :
- Demander une synthèse des appréciations par matière
- Respecter un style formel de conseil de classe
- Limiter la longueur (actuellement 255 caractères)
- Répondre uniquement par l'appréciation (sans explications)
- Accepter un libellé de semestre afin de contextualiser correctement la consigne (S1 ou S2)

## Exemple de modification

```python
# Dans src/services/prompts.py

# Modifier la limite de caractères pour l'appréciation générale
PROMPT_GENERATE_GENERAL_APPRECIATION_TEMPLATE = """Tu es un professeur principal rédigeant l'appréciation générale pour un conseil de classe.

À partir des appréciations suivantes par matière, rédige une appréciation générale synthétique:

{appreciations_text}

Consignes:
- Style formel de conseil de classe
- Maximum 300 caractères  # ← Modifié de 255 à 300
- Synthèse globale des points forts et axes de progrès
- Encouragements constructifs
- Évite les répétitions
- Ton bienveillant mais objectif

IMPORTANT: Réponds UNIQUEMENT par l'appréciation générale rédigée, sans titre, préambule, explication ou formatage supplémentaire. Le texte sera inséré tel quel dans le bulletin.

Appréciation générale:"""
```

## Notes importantes

- ⚠️ **Ne pas supprimer** les instructions "IMPORTANT" qui garantissent que l'IA répond uniquement avec le texte attendu
- ⚠️ **Tester** les modifications avec quelques appréciations avant de les utiliser en production
- ⚠️ **Conserver** le placeholder `{appreciations_text}` dans le template de génération générale
- ✅ Les prompts sont alignés avec l'intégration OpenAI (Responses API)

## Historique

- **Avant** : Les prompts étaient directement dans `src/services/openai_service.py` (lignes 323-336 et 384-400)
- **Maintenant** : Centralisés dans `src/services/prompts.py` pour faciliter la modification

---

**📁 Fichier des prompts** : `src/services/prompts.py`

