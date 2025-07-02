# Tests du projet

Ce dossier contient tous les tests pour le projet BGRAPP Pyconseil.

## Structure prévue

- `test_models/` - Tests des modèles de données
- `test_services/` - Tests des services métier
- `test_gui/` - Tests de l'interface graphique
- `test_integration/` - Tests d'intégration end-to-end
- `conftest.py` - Configuration pytest commune

## Framework utilisé

- **pytest 8.3.4** - Framework de tests principal
- Tests unitaires pour chaque module
- Tests d'intégration pour les workflows complets
- Objectif de couverture : >80%

## Exécution des tests

```bash
# Activer l'environnement
conda activate BGRAPP_pyconseil

# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=src
``` 