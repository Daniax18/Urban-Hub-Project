# Présentation du microservice Validateur de données

## 1. Rôle du microservice

Le microservice `ms6-validateur-capteur` joue le rôle de **validateur de données** dans Urban Hub.

Son objectif est de contrôler les mesures issues des capteurs IoT avant leur exploitation par les services de traitement. Il vérifie le type de capteur, compare la valeur reçue avec des seuils métier, puis qualifie la mesure avec un niveau de gravité.

Les niveaux retournés sont :

- `normal` : la valeur reste dans la plage attendue.
- `moderate` : la valeur dépasse un seuil d'attention.
- `critical` : la valeur dépasse un seuil critique.
- `unknown` : le type de capteur n'est pas reconnu par le service.

Ce microservice permet donc d'isoler la logique de validation et de classification des données environnementales.

## 2. Positionnement dans la chaîne

Le validateur se place entre la collecte IoT et le traitement d'événements :

```text
Collecte IoT -> Validateur de données -> Traitement d'événements
```

Dans cette chaîne :

- `ms-collecte-iot` collecte et normalise les données reçues depuis les capteurs.
- `ms6-validateur-capteur` valide la mesure et détermine son niveau de criticité.
- Le service de traitement d'événements exploite le résultat de validation pour créer ou ignorer un événement métier.

Le validateur ne décide pas seul de toutes les actions à exécuter. Il fournit un résultat fiable et structuré qui permet au service suivant de déclencher un événement en cas de dépassement.

## 3. Contrat d'interface

### Endpoint

| Élément | Valeur |
|---|---|
| Méthode | `POST` |
| Route | `/validate` |
| Content-Type | `application/json` |

### Donnée reçue en entrée

```json
{
  "sensor": "co2",
  "value": 850.0
}
```

Champs attendus :

| Champ | Type | Description |
|---|---|---|
| `sensor` | `string` | Type du capteur à valider. |
| `value` | `number` | Valeur mesurée par le capteur. |

### Donnée retournée en sortie

```json
{
  "valid": true,
  "level": "moderate",
  "sensor": "co2",
  "value": 850.0,
  "threshold": 1000,
  "timestamp": "2026-04-30T08:15:30.000000+00:00"
}
```

## 4. Seuils de validation

Le service prend actuellement en charge les capteurs suivants :

| Capteur | Seuil `moderate` | Seuil `critical` | Unité |
|---|---:|---:|---|
| `co2` | 800 | 1000 | ppm |
| `temperature` | 35 | 40 | °C |
| `noise` | 70 | 85 | dB |
| `pm25` | 25 | 590 | µg/m³ |
| `humidity_air` | 10 | 40 | % |

Les seuils sont définis dans le code du service, dans le dictionnaire `THRESHOLDS`.

## 5. Lien avec les exigences

Le microservice répond aux exigences du cahier des charges suivantes :

| Exigence | Description | Couverture par le validateur |
|---|---|---|
| `EX-ENV-02` | Des seuils de pollution doivent être configurables. | Le service centralise les seuils de validation par type de capteur. |
| `EX-ENV-03` | Les dépassements doivent générer des événements. | Le service identifie les dépassements via les niveaux `moderate` et `critical`, transmis au traitement d'événements. |
| `EX-INC-02` | Les incidents doivent être horodatés et catégorisés. | Le service retourne un `timestamp` et une catégorie de gravité via `level`. |


## 6. Technologies utilisées

| Élément | Technologie | Version |
|---|---|---|
| Langage | Python | `3.11` |
| Framework API | FastAPI | `0.121.0` |
| Serveur ASGI | Uvicorn | `0.34.0` |
| Validation de schéma | Pydantic | `2.10.4` |
| Image Docker | `python:3.11-slim` | - |
| Tests | Pytest | `8.3.4` |

## 7. Prérequis pour faire tourner le microservice

### Avec Docker Compose

Prérequis :

- Docker installé.
- Docker Compose disponible.

Commande de lancement depuis la racine du projet :

```bash
docker compose up --build ms6
```

Le service est ensuite disponible sur :

```text
http://localhost:8000/validate
```

### Exemple d'appel

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"sensor":"co2","value":850}'
```

### En local sans Docker

Prérequis :

- Python `3.11`.
- `pip`.
- Les dependances du fichier `requirements.txt`.

Commandes :

```bash
cd ms6-validateur-capteur
pip install -r requirements.txt
uvicorn src.validator:app --host 0.0.0.0 --port 8000
```
