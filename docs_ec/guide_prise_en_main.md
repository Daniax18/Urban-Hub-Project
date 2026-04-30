# Guide de prise en main - ms6-validateur-capteur

Ce guide permet à un nouveau développeur de reprendre le microservice `ms6-validateur-capteur` sans assistance.

## 1. Cloner le dépôt et se positionner sur la bonne branche

Cloner le dépôt :

```bash
git clone https://github.com/[MI202619-org]/Urban-Hub-Project.git
cd Urban-Hub-Project
```

Se positionner sur la branche de développement :

```bash
git checkout develop
git pull origin develop
```

Aller dans le répertoire du microservice :

```bash
cd ms6-validateur-capteur
```

## 2. Installer les dépendances

Version Python utilisée par le pipeline GitHub Actions : `3.12.3`.

Créer un environnement virtuel :

```bash
python -m venv .venv
```

Activer l'environnement virtuel sous Windows PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
```

Activer l'environnement virtuel sous Linux/macOS :

```bash
source .venv/bin/activate
```

Mettre à jour `pip` :

```bash
python -m pip install --upgrade pip
```

Installer les dépendances applicatives et de développement :

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Dépendances principales du microservice :

- `fastapi==0.121.0`
- `starlette==0.49.1`
- `uvicorn==0.34.0`
- `pydantic==2.10.4`
- `pika==1.3.2`

## 3. Lancer les tests en local

Depuis le répertoire `ms6-validateur-capteur`, lancer :

```bash
pytest test \
  --junitxml=report_tests.xml \
  --cov=src \
  --cov-report=xml:coverage.xml \
  --cov-report=term-missing \
  --cov-fail-under=80
```

Sous Windows PowerShell, utiliser la version sur une seule ligne :

```powershell
pytest test --junitxml=report_tests.xml --cov=src --cov-report=xml:coverage.xml --cov-report=term-missing --cov-fail-under=80
```

Résultat attendu :

```text
4 passed
Required test coverage of 80% reached. Total coverage: 100.00%
```

Le rapport actuel indique :

- `4 passed`
- couverture totale : `100%`
- seuil minimal de couverture : `80%`

## 4. Lancer le microservice en local

Depuis le répertoire `ms6-validateur-capteur`, lancer l'API FastAPI avec Uvicorn :

```bash
python -m uvicorn src.validator:app --host 127.0.0.1 --port 8000 --reload
```

Résultat attendu dans le terminal :

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

Tester l'endpoint `/validate` avec `curl` :

```bash
curl -X POST http://127.0.0.1:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"sensor":"co2","value":500}'
```

Résultat attendu :

```json
{
  "valid": true,
  "level": "normal",
  "sensor": "co2",
  "value": 500,
  "threshold": 800,
  "timestamp": "..."
}
```

Il est aussi possible de lancer le service avec Docker Compose depuis la racine du dépôt :

```bash
docker compose up --build ms6
```

Résultat attendu :

- construction de l'image `ms6-validateur-capteur` ;
- conteneur `ms6-validateur-capteur` démarre ;
- API disponible sur `http://localhost:8000`.

## 5. Secrets GitHub requis

Les secrets sont utilisés par le workflow `.github/workflows/ms6-validateur.yml`.

| Secret | Rôle |
|---|---|
| `SONAR_TOKEN` | Jeton d'authentification utilisé par SonarCloud pour lancer l'analyse qualité du code. |
| `SONAR_HOST_URL` | URL du serveur Sonar. Si le secret n'est pas défini ou ne contient pas une URL valide, le workflow utilise `https://sonarcloud.io` comme valeur de repli. |
| `SNYK_TOKEN` | Jeton d'authentification Snyk utilisé pour scanner les dépendances Python et détecter les vulnérabilités connues. |

Ne jamais mettre les valeurs de ces secrets dans le code source, dans les logs ou dans la documentation.

Procédure pour ajouter un secret dans GitHub :

1. Ouvrir le dépôt sur GitHub : `[MI202619-org]/Urban-Hub-Project`.
2. Aller dans `Settings`.
3. Aller dans `Secrets and variables`.
4. Cliquer sur `Actions`.
5. Cliquer sur `New repository secret`.
6. Renseigner le nom du secret, par exemple `SNYK_TOKEN`.
7. Coller la valeur du secret dans le champ `Secret`.
8. Cliquer sur `Add secret`.

Répéter la procédure pour chaque secret requis.

## 6. Ajouter un nouveau capteur dans `THRESHOLDS`

Les seuils des capteurs sont définis dans `ms6-validateur-capteur/src/validator.py`, dans le dictionnaire `THRESHOLDS`.

Structure attendue pour un capteur :

```python
"nom_du_capteur": {
    "moderate": valeur_seuil_moderate,
    "critical": valeur_seuil_critical,
    "unit": "unite",
}
```

Exemple d'ajout d'un capteur `wind` :

```python
THRESHOLDS = {
    "co2": {"moderate": 800, "critical": 1000, "unit": "ppm"},
    "temperature": {"moderate": 35, "critical": 40, "unit": "C"},
    "noise": {"moderate": 70, "critical": 85, "unit": "dB"},
    "pm25": {"moderate": 25, "critical": 590, "unit": "ug/m"},
    "humidity_air": {"moderate": 10, "critical": 40, "unit": "%"},
    "wind": {"moderate": 50, "critical": 80, "unit": "km/h"},
}
```

Regles a respecter :

- le nom du capteur doit etre une chaine non vide ;
- `moderate` doit etre inferieur a `critical` ;
- l'unite doit etre explicite ;
- le nom utilise dans les requetes doit correspondre exactement a la cle du dictionnaire.

Ajouter ensuite un test dans `ms6-validateur-capteur/test/test_validator.py`.

Relancer les tests :

```bash
pytest test --cov=src --cov-report=term-missing --cov-fail-under=80
```

Tester ensuite manuellement le nouveau capteur :

```bash
curl -X POST http://127.0.0.1:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"sensor":"wind","value":60}'
```

Resultat attendu :

```json
{
  "valid": true,
  "level": "moderate",
  "sensor": "wind",
  "value": 60,
  "threshold": 80,
  "timestamp": "..."
}
```

Si le capteur n'est pas ajoute dans `THRESHOLDS`, l'API retournera :

```json
{
  "valid": false,
  "level": "unknown",
  "sensor": "wind",
  "value": 60,
  "threshold": null,
  "timestamp": "..."
}
```
