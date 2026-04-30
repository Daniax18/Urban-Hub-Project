# Pipeline CI/CD - ms6-validateur-capteur

Ce document decrit le workflow GitHub Actions defini dans `.github/workflows/ms6-validateur.yml` pour le microservice `ms6-validateur-capteur`.

Le pipeline suit l'ordre suivant :

```text
tests -> quality -> build -> deploying-staging
```

Chaque job depend du precedent. Si une etape echoue, les suivantes ne sont pas executées.

## 1. Declencheurs du workflow

Le workflow est declenché automatiquement dans les cas suivants :

| Evenement | Branche | Conditions sur les fichiers |
|---|---|---|
| `push` | `main`, `develop` | Modification dans `ms6-validateur-capteur/**`, `docker-compose.yml` ou `.github/workflows/ms6-validateur.yml` |
| `pull_request` | `main` | Modification dans `ms6-validateur-capteur/**`, `docker-compose.yml` ou `.github/workflows/ms6-validateur.yml` |

Cette configuration évite de lancer le pipeline MS6 quand une modification ne concerne pas ce microservice.

## 2. Job `tests`

### Objectif

Le job `tests` vérifie que le microservice fonctionne correctement avant de passer aux contrôles qualité.

### Configuration

| Element | Valeur |
|---|---|
| Runner | `ubuntu-latest` |
| Repertoire de travail | `ms6-validateur-capteur` |
| Variable `PYTHONPATH` | `${{ github.workspace }}/ms6-validateur-capteur` |

### Etapes executees

1. Récuperation du depot avec `actions/checkout@v4`.
2. Installation de Python avec `actions/setup-python@v5`.
3. Installation des dépendances applicatives et de développement.
4. Execution des tests avec Pytest et géneration de la couverture.

### Installation des dépendances

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Fichiers utilisés :

- `requirements.txt` : dépendances du microservice.
- `requirements-dev.txt` : outils de test et qualité, comme `pytest`, `pytest-cov`, `flake8`.

### Execution des tests

```bash
pytest test \
  --junitxml=report_tests.xml \
  --cov=src \
  --cov-report=xml:coverage.xml \
  --cov-report=term-missing \
  --cov-fail-under=80 | tee rapport_tests.txt
```

Paramètres importants :

| Paramètre | Role |
|---|---|
| `--junitxml=report_tests.xml` | Genere un rapport de tests au format JUnit |
| `--cov=src` | Mesure la couverture du code dans `src` |
| `--cov-report=xml:coverage.xml` | Genere un rapport de couverture exploitable par SonarCloud pour le coverage|
| `--cov-report=term-missing` | Affiche les lignes non couvertes dans la sortie console |
| `--cov-fail-under=80` | Echoue si la couverture est inferieure a 80 % |
| `tee rapport_tests.txt` | Sauvegarde la sortie dans un fichier texte |

Rapport obtenu apres correction :

- `4 passed`
- couverture totale : `100%`
- seuil minimal de `80%` atteint

Artefacts publiés :

- `coverage.xml`
- `report_tests.xml`
- `rapport_tests.txt`

## 3. Job `quality`

### Objectif

Le job `quality` contrôle la qualite du code et la sécurite des dépendances. Il demarre uniquement si le job `tests` est réussi.

```yaml
needs: tests
```

### Configuration

| Element | Valeur |
|---|---|
| Runner | `ubuntu-latest` |
| Repertoire de travail | `ms6-validateur-capteur` |
| Checkout | `fetch-depth: 0` pour permettre une analyse SonarCloud complete |

#### a. SonarCloud

##### Rôle

SonarCloud analyse la qualite du code : maintenabilité, bugs potentiels, couverture de tests.

##### Configuration du projet

La configuration se trouve dans `ms6-validateur-capteur/sonar-project.properties`.

```properties
sonar.projectKey=Daniax18_Urban-Hub-Project
sonar.organization=daniax18
sonar.sources=src
sonar.tests=test
sonar.exclusions=**/__pycache__/**,**/*.pyc
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=report_tests.xml
sonar.python.flake8.reportPaths=flake8-report.txt
sonar.sourceEncoding=UTF-8
```

##### Paramètres GitHub Actions

```yaml
- name: SonarCloud Scan
  uses: SonarSource/sonarqube-scan-action@fd88b7d7ccbaefd23d8f36f73b59db7a3d246602
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: ${{ startsWith(secrets.SONAR_HOST_URL, 'http') && secrets.SONAR_HOST_URL || 'https://sonarcloud.io' }}
  with:
    projectBaseDir: ms6-validateur-capteur
```

Secrets GitHub utilisés :

| Secret | Rôle |
|---|---|
| `SONAR_TOKEN` | Jeton d'authentification SonarCloud |
| `SONAR_HOST_URL` | URL du serveur Sonar, avec repli sur `https://sonarcloud.io` |

##### Démarche avant / apres correction

Avant correction, l'analyse permet d'identifier les problemes de qualité

Commande locale possible :

```bash
sonar-scanner > sonar-report-avant.txt
```

Apres correction du code et des tests, l'analyse est relancée :

```bash
sonar-scanner > sonar-report-apres.txt
```

Dans le pipeline, SonarCloud utilise aussi les fichiers génerés par Pytest :

- `coverage.xml`
- `report_tests.xml`

#### b. Snyk

##### Role

Snyk contrôle les vulnerabilités connues dans les dependances Python du microservice.

##### Configuration GitHub Actions

Le CLI Snyk est installé avec :

```yaml
- name: Set up Snyk CLI
  uses: snyk/actions/setup@master
```

Le scan est ensuite lancé avec :

```bash
snyk test --file=requirements.txt --package-manager=pip | tee snyk-report.txt
```

Paramètres :

| Paramètre | Role |
|---|---|
| `--file=requirements.txt` | Cible le fichier de dependances Python |
| `--package-manager=pip` | Force l'analyse comme projet `pip` |
| `tee snyk-report.txt` | Sauvegarde le rapport dans un fichier |

Secret GitHub utilise :

| Secret | Rôle |
|---|---|
| `SNYK_TOKEN` | Jeton d'authentification Snyk |

Le rapport est publié comme artefact :

- `snyk-report.txt`

##### Démarche avant / après correction

Avant correction, le scan était lance pour produire un rapport initial :

```bash
snyk test --file=requirements.txt --package-manager=pip > snyk-report-avant.txt
```

Le rapport `snyk-report-avant.txt` indiquait 2 vulnerabilités liées a `starlette@0.41.3`, introduite par `fastapi@0.115.6` :

- vulnerabilite de severité `Medium`
- vulnerabilite de severité `High`

Apres correction des versions dans `requirements.txt`, le scan a ete relancé :

```bash
snyk test --file=requirements.txt --package-manager=pip > snyk-report-apres.txt
```

Le rapport après correction indique :

```text
Tested 13 dependencies for known issues, no vulnerable paths found.
```

Dans le depot, le fichier existant `snyk-report-avant_2.txt` correspond au rapport apres correction.

#### c. Flake8

##### Rôle

Flake8 vérifie le respect des regles de style Python et détecte certaines erreurs simples.

##### Commande du pipeline

```bash
flake8 src test
```

Le pipeline échoue si Flake8 retourne au moins une erreur.

##### Demarche avant / après correction

Avant correction, la commande a ete lancée avec redirection vers un rapport :

```bash
flake8 src test > flake8_avant.txt
```

Le rapport initial contenait des erreurs :

```text
src/validator.py:8:1: E302 expected 2 blank lines, found 1
src/validator.py:12:1: E305 expected 2 blank lines after class or function definition, found 1
src/validator.py:20:1: E302 expected 2 blank lines, found 1
test/test_validator.py:7:1: E302 expected 2 blank lines, found 1
```

Après correction du formatage, la commande a ete relancée :

```bash
flake8 src test > flake8_apres.txt
```

Le rapport apres correction indique `0`, ce qui signifie qu'il n'y a plus d'erreur Flake8.

## 3. Job `build`

### Objectif

Le job `build` vérifie que le microservice peut être compilé sous forme d'image Docker. Il demarre uniquement si le job `quality` est reussi.

```yaml
needs: quality
```

### Etapes executées

1. Récuperation du depot avec `actions/checkout@v4`.
2. Construction de l'image Docker.

Commande executée :

```bash
docker build -t ms6-validateur-capteur:ci ./ms6-validateur-capteur
```

Cette étape valide notamment :

- la présence du `Dockerfile` ;
- l'installation des dépendances Python ;
- la copie du code source ;
- l'éxposition du port `8000` ;
- le démarrage possible avec `uvicorn`.

Image produite :

```text
ms6-validateur-capteur:ci
```

## 4. Job `deploying-staging`

### Objectif

Le job `deploying-staging` simule ou execute le deploiement du microservice en environnement de staging. Il demarre uniquement si le job `build` est reussi.

```yaml
needs: build
```

### Etapes executées

1. Récuperation du depot avec `actions/checkout@v4`.
2. Lancement du service MS6 avec Docker Compose.

Commande executée :

```bash
docker compose up -d ms6
```

Dans `docker-compose.yml`, le service `ms6` correspond au conteneur :

```text
ms6-validateur-capteur
```

Il expose le port :

```text
8000:8000
```

Le service demarre avec :

```bash
uvicorn src.validator:app --host 0.0.0.0 --port 8000
```
