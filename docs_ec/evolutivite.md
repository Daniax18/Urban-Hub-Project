# Évolutivité - ms6-validateur-capteur

Ce document explique comment faire évoluer le microservice `ms6-validateur-capteur`, comment l'intégrer dans l'environnement Docker Compose du groupe et comment cette évolution s'inscrit dans le BC04 de déploiement cloud.

## 1. Ajouter un nouveau capteur dans le validateur

Les capteurs acceptés par le MS6 sont déclarés dans le fichier :

```text
ms6-validateur-capteur/src/validator.py
```

Le dictionnaire concerné est `THRESHOLDS`.

Procédure pas à pas :

1. Ouvrir `ms6-validateur-capteur/src/validator.py`.
2. Rechercher le dictionnaire `THRESHOLDS`.
3. Ajouter une nouvelle entrée avec le nom du capteur.
4. Définir les seuils `moderate` et `critical`.
5. Définir l'unité avec la clé `unit`.
6. Ajouter ou adapter un test dans `ms6-validateur-capteur/test/test_validator.py`.
7. Relancer les tests locaux.
8. Tester manuellement l'endpoint `/validate`.

Exemple avec un capteur `wind` :

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

Règles à respecter :

- le nom du capteur doit correspondre exactement à la valeur envoyée dans le champ JSON `sensor` ;
- `moderate` doit être inférieur à `critical` ;
- l'unité doit être claire et stable ;
- un test doit couvrir au minimum un cas `normal`, `moderate` ou `critical` pour le nouveau capteur.

Exemple de requête attendue :

```bash
curl -X POST http://127.0.0.1:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"sensor":"wind","value":60}'
```

Réponse attendue :

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

## 2. Ajouter ou modifier un seuil

Les seuils sont aussi modifiés dans `ms6-validateur-capteur/src/validator.py`, dans `THRESHOLDS`.

Structure d'un seuil :

```python
"nom_du_capteur": {
    "moderate": valeur_moderate,
    "critical": valeur_critical,
    "unit": "unite",
}
```

Exemple de modification du seuil `co2` :

```python
"co2": {"moderate": 750, "critical": 950, "unit": "ppm"},
```

Effet dans le code :

- si `value >= critical`, le niveau retourné est `critical` ;
- si `value >= moderate` et `value < critical`, le niveau retourné est `moderate` ;
- si `value < moderate`, le niveau retourné est `normal` ;
- si le capteur n'existe pas dans `THRESHOLDS`, le niveau retourné est `unknown`.

Après chaque modification de seuil, mettre à jour les tests correspondants dans :

```text
ms6-validateur-capteur/test/test_validator.py
```

Commande de vérification :

```bash
pytest test --cov=src --cov-report=term-missing --cov-fail-under=80
```

Résultat attendu :

```text
4 passed
Required test coverage of 80% reached
```

Si un seuil change, les assertions sur `level` et `threshold` doivent être ajustées dans les tests.

## 3. Intégration dans le Docker Compose du groupe

Le MS6 à intégrer dans le fichier Docker Compose du groupe :

```text
docker-compose.yml
```

Service à ajouter :

```yaml
ms6:
  build:
    context: ./ms6-validateur-capteur
  container_name: ms6-validateur-capteur
  ports:
    - "8000:8000"
  command: ["uvicorn", "src.validator:app", "--host", "0.0.0.0", "--port", "8000"]
  restart: unless-stopped
```

Détails d'intégration :

- nom du service Docker Compose : `ms6` ;
- nom du conteneur : `ms6-validateur-capteur` ;
- répertoire de build : `./ms6-validateur-capteur` ;
- port exposé : `8000` ;
- mapping local : `8000:8000` ;
- commande de démarrage : `uvicorn src.validator:app --host 0.0.0.0 --port 8000`.

Commande de lancement depuis la racine du dépôt :

```bash
docker compose up --build ms6
```

Résultat attendu :

- l'image Docker du MS6 est construite ;
- le conteneur `ms6-validateur-capteur` démarre ;
- l'API est disponible sur `http://localhost:8000`.

## 4. Lien avec le BC04 : déploiement cloud

Le document global `docs/evolutivite.md` positionne UrbanHub comme une architecture microservices devant pouvoir évoluer vers un déploiement cloud. Le MS6 suit cette logique car il est déjà :

- isolé dans son propre répertoire ;
- conteneurisé avec un `Dockerfile` dédié ;
- intégré dans `docker-compose.yml` ;
- contrôlé par un pipeline CI/CD avec tests, qualité, sécurité et build Docker.

Dans le cadre du BC04, le MS6 peut être déployé dans une infrastructure cloud en suivant la trajectoire globale du projet :

- standardiser le service avec Docker ;
- héberger les services applicatifs sur des instances cloud, par exemple `EC2` ;
- permettre l'auto-scaling horizontal si le volume de validations augmente ;
- utiliser `Amazon RDS` pour les bases relationnelles des autres services ;
- utiliser `Amazon S3` comme zone d'archivage ou data lake pour les données IoT, exports, historiques et traces.

Le MS6 n'a pas de base de données propre actuellement. Son déploiement cloud est donc plus simple que celui des services avec stockage : il peut être lancé comme service stateless (Lambda), puis scale horizontalement si plusieurs instances doivent traiter plus de requêtes de validation.


## 5. Pistes d'amélioration pour les versions futures

Plusieurs évolutions peuvent améliorer la maintenabilité et la robustesse du MS6.

### 5.1 Externaliser les seuils

Aujourd'hui, les seuils sont codés directement dans `validator.py`. Une version future pourrait les charger depuis :

- un fichier JSON ou YAML ;
- une variable d'environnement ;
- une base de données ;
- un service de configuration centralisé.

Cela permettrait de modifier les seuils sans redéployer le code.

### 5.2 Ajouter une validation metier plus complete

Le modele actuel verifie seulement que `sensor` n'est pas vide et que `value` est un nombre.

Ameliorations possibles :

- interdire les valeurs impossibles selon le type de capteur ;
- ajouter des bornes minimales et maximales ;
- normaliser les noms de capteurs ;
- retourner un message d'erreur plus explicite pour les capteurs inconnus.

### 5.3 Exposer les capteurs disponibles

Ajouter un endpoint de lecture faciliterait l'integration avec les autres services :

```text
GET /thresholds
```

Cet endpoint pourrait retourner la liste des capteurs, leurs seuils et leurs unites.

### 5.4 Ajouter une observabilite plus complete

Pour un deploiement cloud, il serait utile d'ajouter :

- un endpoint `GET /health` ;
- des logs structures ;
- des metriques Prometheus ;
- un suivi du nombre de validations par capteur ;
- un suivi du nombre de niveaux `normal`, `moderate`, `critical` et `unknown`.

