# 🆘 Dépannage et FAQ

## Installation et configuration

### Q1: Comment installer le projet ?

**R:** Suivez ces étapes:

```bash
# 1. Clone du projet
cd urbanhubEC03

# 2. Créer un environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Sur Windows:
venv\Scripts\activate
# Sur Linux/Mac:
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Vérifier l'installation
python verify_setup.py
```

---

### Q2: Erreur "ModuleNotFoundError: No module named 'src'"

**R:** Assurez-vous que:

1. Vous êtes dans le bon répertoire:
```bash
cd urbanhubEC03
```

2. La variable PYTHONPATH est définie:
```bash
# Windows
set PYTHONPATH=%CD%
# Linux/Mac
export PYTHONPATH="${PWD}"
```

3. Exécutez les tests correctement:
```bash
# ✓ Correct
python -m pytest tests/unit/

# ✓ Correct
python src/main.py
```

---

### Q3: Erreur "No module named 'pytest'"

**R:** Installez les dépendances:

```bash
pip install -r requirements.txt
```

Ou installez pytest directement:

```bash
pip install pytest
```

---

### Q4: Erreur "No module named 'pika'"

**R:** Installez pika:

```bash
pip install pika
```

Ceci est utile si vous voulez utiliser RabbitMQ réel. Pour les tests, MockLogConsumer n'a pas besoin de pika.

---

## Tests

### Q5: Comment exécuter les tests ?

**R:** Plusieurs options:

```bash
# Tous les tests
pytest

# Verbose (affiche plus de détails)
pytest -v

# Tests spécifiques
pytest tests/unit/domain/

# Avec couverture
pytest --cov=src --cov-report=html

# Tests rapides
pytest -x  # Stop au premier échec
```

---

### Q6: Comment exécuter un test spécifique ?

**R:** Utilisez le chemin du fichier et le nom du test:

```bash
# Un fichier
pytest tests/unit/domain/test_log.py

# Une classe
pytest tests/unit/domain/test_log.py::TestLogEntity

# Une méthode
pytest tests/unit/domain/test_log.py::TestLogEntity::test_log_creation_with_defaults

# Par pattern
pytest -k "test_log_creation"
```

---

### Q7: Les tests prennent du temps, comment les accélérer ?

**R:** Plusieurs options:

```bash
# Stop au premier échec
pytest -x

# Stop après N échecs
pytest --maxfail=3

# Tests en parallèle (avec pytest-xdist)
pip install pytest-xdist
pytest -n auto

# Seulement les tests qui ont échoué
pytest --lf

# Seulement les tests récents
pytest --ff
```

---

## Utilisation du microservice

### Q8: Comment utiliser le microservice dans mon code ?

**R:** Importez et utilisez les composants:

```python
from src.application.process_log_use_case import ProcessLogUseCase
from src.adapters.database.log_repository_adapter import InMemoryLogRepository
from src.adapters.database.log_validator_adapter import LogValidator

# Initialisation
repository = InMemoryLogRepository()
validator = LogValidator()
use_case = ProcessLogUseCase(repository, validator)

# Traiter un log
log_data = {
    "service": "MS Test",
    "event_type": "test_event",
    "message": "Test message"
}

success, message, log_id = use_case.execute(log_data)

# Récupérer les logs
logs = use_case.get_all_logs()
```

Consultez `EXAMPLES.py` pour plus d'exemples.

---

### Q9: Comment utiliser SQLite au lieu de la mémoire ?

**R:** Changez le repository:

```python
from src.adapters.database.log_repository_adapter import SQLiteLogRepository

# Au lieu de InMemoryLogRepository
repository = SQLiteLogRepository("logs.db")

use_case = ProcessLogUseCase(repository, validator)
```

Les logs seront persistés dans `logs.db`.

---

### Q10: Comment utiliser la vraie RabbitMQ ?

**R:** Utilisez RabbitMQLogConsumer au lieu de MockLogConsumer:

```python
from src.adapters.rabbitmq.log_consumer_adapter import RabbitMQLogConsumer

consumer = RabbitMQLogConsumer(
    host="localhost",
    queue_name="logs_queue",
    port=5672
)

# Définir un callback
def handle_message(message: str):
    # Traiter le message
    pass

# Démarrer
consumer.start(handle_message)
```

Assurez-vous que RabbitMQ est installé et en cours d'exécution.

---

### Q11: Comment utiliser l'API REST ?

**R:** Utilisez LogApiAdapter:

```python
from src.adapters.api.log_api_adapter import LogApiAdapter

api = LogApiAdapter(use_case)

# Récupérer tous les logs
result = api.get_all_logs()

# Récupérer un log par ID
result = api.get_log_by_id(log_id)

# Récupérer par service
result = api.get_logs_by_service("MS Alerte")

# Récupérer par niveau
result = api.get_logs_by_level("ERROR")

# Récupérer les erreurs
result = api.get_errors()

# Tous les résultats ont le format:
# {
#   "status": "success" ou "error",
#   "data": [...] ou "message": "..."
# }
```

---

## Validation

### Q12: Comment valider un log avant le traitement ?

**R:** Utilisez LogValidator:

```python
from src.adapters.database.log_validator_adapter import LogValidator

validator = LogValidator()

log_data = {
    "service": "MS Test",
    "event_type": "test",
    "message": "message"
}

is_valid, errors = validator.validate(log_data)

if not is_valid:
    print(f"Erreurs de validation: {errors}")
```

---

### Q13: Quels sont les champs obligatoires ?

**R:** Les champs obligatoires sont:
- `service`: Nom du microservice (non vide)
- `event_type`: Type d'événement (non vide)
- `message`: Message du log (non vide)

Les champs optionnels sont:
- `level`: INFO, WARNING, ERROR, DEBUG, CRITICAL (défaut: INFO)
- `timestamp`: Format ISO (défaut: maintenant)
- `metadata`: Dictionnaire (défaut: {})

---

### Q14: Quels sont les niveaux de log valides ?

**R:** Les niveaux valides sont:
- `DEBUG`: Informations de debug
- `INFO`: Informations générales (par défaut)
- `WARNING`: Avertissements
- `ERROR`: Erreurs
- `CRITICAL`: Erreurs critiques

---

## Architecture

### Q15: Pourquoi utiliser l'architecture hexagonale ?

**R:** L'architecture hexagonale (Ports & Adapters) offre:

1. **Testabilité**: Facile de tester avec des mocks
2. **Découplage**: Sépare la logique métier des détails techniques
3. **Flexibilité**: Changer d'implémentation sans toucher le cœur
4. **Maintenabilité**: Code organisé et compréhensible

---

### Q16: Comment ajouter une nouvelle implémentation de Repository ?

**R:** Créez une classe qui implémente LogRepositoryPort:

```python
from src.ports.log_repository_port import LogRepositoryPort
from src.domain.log import Log
from typing import List, Optional

class PostgreSQLLogRepository(LogRepositoryPort):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def save(self, log: Log) -> str:
        # Implémenter la sauvegarde
        pass

    def find_by_id(self, log_id: str) -> Optional[Log]:
        # Implémenter la récupération
        pass

    # Implémenter les autres méthodes...
```

Ensuite, utilisez-le:

```python
from my_impl import PostgreSQLLogRepository

repository = PostgreSQLLogRepository("postgresql://...")
use_case = ProcessLogUseCase(repository, validator)
```

---

## Problèmes courants

### Q17: Comment déboguer un log qui n'est pas traité ?

**R:** Vérifiez:

1. Les données sont valides:
```python
is_valid, errors = validator.validate(log_data)
if not is_valid:
    print(f"Erreurs: {errors}")
```

2. Le traitement a réussi:
```python
success, message, log_id = use_case.execute(log_data)
if not success:
    print(f"Erreur: {message}")
```

3. Le log est bien en base:
```python
log = use_case.get_log_by_id(log_id)
if log:
    print(f"Log trouvé: {log.to_dict()}")
```

---

### Q18: Comment debugger les tests ?

**R:** Utilisez pytest avec des options de debug:

```bash
# Verbose
pytest -v

# Très verbose
pytest -vv

# Affiche les prints
pytest -s

# Arrête au premier échec
pytest -x

# Debug interactif avec pdb
pytest --pdb

# Affiche les variables locales
pytest -l
```

Ou ajoutez breakpoints dans le code:

```python
def test_something():
    # ... code ...
    breakpoint()  # Pause here
    # ... code ...
```

---

### Q19: Comment voir la couverture de code ?

**R:** Utilisez pytest-cov:

```bash
# Rapport terminal
pytest --cov=src --cov-report=term

# Rapport HTML
pytest --cov=src --cov-report=html

# Ouvrir le rapport
# Ouvrez htmlcov/index.html dans un navigateur
```

---

### Q20: Comment mesurer les performances ?

**R:** Utilisez pytest-benchmark:

```bash
pip install pytest-benchmark

# Créer un benchmark test
def test_performance(benchmark):
    def execute():
        use_case.execute(log_data)
    
    result = benchmark(execute)
```

Ou mesurez manuellement:

```python
import time

start = time.time()
success, msg, log_id = use_case.execute(log_data)
elapsed = time.time() - start

print(f"Temps d'exécution: {elapsed * 1000:.2f}ms")
```

---

## Scripts utilitaires

### Q21: Comment utiliser les scripts de démarrage ?

**R:** Utilisez le script approprié:

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

Ces scripts offrent un menu interactif pour:
- Exécuter les tests
- Générer les rapports de couverture
- Lancer le microservice

---

### Q22: Comment vérifier que tout est configuré ?

**R:** Utilisez le script de vérification:

```bash
python verify_setup.py
```

Ce script vérifie:
- Version de Python
- Structure du projet
- Imports des modules
- Dépendances
- Tests fonctionnels

---

## Documentation

### Q23: Où trouver la documentation ?

**R:** Consultez ces fichiers:

- `README.md`: Vue d'ensemble et guide d'utilisation
- `PROJET_RESUME.md`: Résumé complet du projet
- `EXAMPLES.py`: 15 exemples pratiques
- `rule.md`: Spécifications initiales
- Ce fichier: FAQ et dépannage
- Docstrings: Documentation du code

---

### Q24: Comment générer la documentation du code ?

**R:** Utilisez sphinx (optionnel):

```bash
pip install sphinx
sphinx-quickstart docs
make html  # Génère la doc HTML
```

---

## Contact et support

### Q25: Comment contribuer ou signaler un bug ?

**R:** Consultez:

1. Vérifiez d'abord que c'est vraiment un bug avec `verify_setup.py`
2. Consultez les tests pour comprendre le comportement attendu
3. Signalez le bug avec:
   - Description claire du problème
   - Étapes pour reproduire
   - Résultat attendu vs obtenu
   - Version de Python et de l'OS

---

## Ressources

### Liens utiles

- [Python](https://www.python.org/)
- [pytest](https://docs.pytest.org/)
- [RabbitMQ](https://www.rabbitmq.com/)
- [SQLite](https://www.sqlite.org/)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

---

**Dernière mise à jour:** 2026-04-21

Si vous avez d'autres questions, consultez les tests (`tests/unit/`) pour des exemples concrets d'utilisation.
