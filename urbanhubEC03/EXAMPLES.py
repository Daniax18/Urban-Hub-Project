"""
EXEMPLES D'UTILISATION DU MICROSERVICE JOURNALISATION

Ce fichier contient des exemples pratiques pour utiliser le microservice.
"""

# ============================================================================
# EXEMPLE 1 : Initialisation de base
# ============================================================================

from src.application.process_log_use_case import ProcessLogUseCase
from src.adapters.database.log_repository_adapter import InMemoryLogRepository
from src.adapters.database.log_validator_adapter import LogValidator

# Initialisation des composants
repository = InMemoryLogRepository()  # En mémoire pour tests
validator = LogValidator()
use_case = ProcessLogUseCase(repository, validator)

print("✓ Microservice initialisé")


# ============================================================================
# EXEMPLE 2 : Traiter un log simple
# ============================================================================

log_data = {
    "service": "MS Alerte",
    "event_type": "notification_sent",
    "message": "Email envoyé avec succès"
}

success, message, log_id = use_case.execute(log_data)

if success:
    print(f"✓ Log traité avec succès: {log_id}")
else:
    print(f"✗ Erreur: {message}")


# ============================================================================
# EXEMPLE 3 : Traiter un log avec tous les paramètres
# ============================================================================

from datetime import datetime

log_data_complete = {
    "service": "MS Analyse",
    "event_type": "analysis_completed",
    "message": "Analyse des données terminée",
    "level": "INFO",
    "timestamp": datetime.now().isoformat(),
    "metadata": {
        "user_id": "user-123",
        "request_id": "req-456",
        "duration_ms": 1234
    }
}

success, message, log_id = use_case.execute(log_data_complete)
print(f"Log complete traité: {log_id}")


# ============================================================================
# EXEMPLE 4 : Traiter plusieurs logs
# ============================================================================

logs = [
    {
        "service": "MS Collecte",
        "event_type": "data_collected",
        "message": "100 données collectées"
    },
    {
        "service": "MS Alerte",
        "event_type": "alert_triggered",
        "message": "Alerte critique",
        "level": "ERROR"
    },
    {
        "service": "MS Authentification",
        "event_type": "user_login",
        "message": "Utilisateur connecté",
        "level": "DEBUG"
    }
]

processed_logs = []
for log_data in logs:
    success, msg, log_id = use_case.execute(log_data)
    if success:
        processed_logs.append(log_id)

print(f"✓ {len(processed_logs)} logs traités")


# ============================================================================
# EXEMPLE 5 : Récupérer un log par ID
# ============================================================================

log = use_case.get_log_by_id(processed_logs[0])
if log:
    print(f"Log trouvé: {log.service} - {log.event_type}")
    print(f"Détails: {log.to_dict()}")


# ============================================================================
# EXEMPLE 6 : Récupérer les logs d'un service
# ============================================================================

alerte_logs = use_case.get_logs_by_service("MS Alerte")
print(f"✓ {len(alerte_logs)} logs de MS Alerte")

for log in alerte_logs:
    print(f"  - {log.event_type}: {log.message}")


# ============================================================================
# EXEMPLE 7 : Récupérer les logs par niveau
# ============================================================================

error_logs = use_case.get_logs_by_level("ERROR")
print(f"✓ {len(error_logs)} logs d'erreur")

debug_logs = use_case.get_logs_by_level("DEBUG")
print(f"✓ {len(debug_logs)} logs de debug")


# ============================================================================
# EXEMPLE 8 : Récupérer tous les logs
# ============================================================================

all_logs = use_case.get_all_logs()
print(f"✓ Total de {len(all_logs)} logs en base")


# ============================================================================
# EXEMPLE 9 : Utiliser l'API REST
# ============================================================================

from src.adapters.api.log_api_adapter import LogApiAdapter

api = LogApiAdapter(use_case)

# Récupérer tous les logs
result = api.get_all_logs()
print(f"API - Tous les logs: {len(result['data'])} trouvés")

# Récupérer les erreurs
errors = api.get_errors()
print(f"API - Erreurs: {len(errors['data'])} erreurs")

# Récupérer par service
logs_by_service = api.get_logs_by_service("MS Collecte")
print(f"API - Logs MS Collecte: {len(logs_by_service['data'])} logs")


# ============================================================================
# EXEMPLE 10 : Valider les données avant de traiter
# ============================================================================

# Cas valide
valid_log = {
    "service": "MS Test",
    "event_type": "test_event",
    "message": "Message de test"
}
is_valid, errors = validator.validate(valid_log)
print(f"Validation valide: {is_valid}")

# Cas invalide
invalid_log = {
    "service": "MS Test",
    "event_type": "",  # Vide
    "message": "Message"
}
is_valid, errors = validator.validate(invalid_log)
print(f"Validation invalide: {is_valid}, Erreurs: {errors}")


# ============================================================================
# EXEMPLE 11 : Utiliser la base de données SQLite
# ============================================================================

from src.adapters.database.log_repository_adapter import SQLiteLogRepository

# Créer un repository SQLite
sqlite_repo = SQLiteLogRepository("logs_production.db")

# Créer un use case avec le repository SQLite
production_use_case = ProcessLogUseCase(sqlite_repo, validator)

# Traiter des logs qui seront persistés
log_data = {
    "service": "MS Production",
    "event_type": "production_event",
    "message": "Événement de production"
}

success, message, log_id = production_use_case.execute(log_data)
print(f"Log persisté en SQLite: {log_id}")


# ============================================================================
# EXEMPLE 12 : Utiliser le Mock Consumer pour tests
# ============================================================================

import json
from src.adapters.rabbitmq.log_consumer_adapter import MockLogConsumer

# Créer un mock consumer
consumer = MockLogConsumer()

# Définir un callback pour traiter les messages
def handle_log_message(message: str):
    try:
        log_data = json.loads(message)
        success, msg, log_id = use_case.execute(log_data)
        if success:
            print(f"✓ Message traité: {log_id}")
    except Exception as e:
        print(f"✗ Erreur: {e}")

# Démarrer le consumer
consumer.start(handle_log_message)

# Publier un message
consumer.publish_message(json.dumps({
    "service": "MS Test",
    "event_type": "test",
    "message": "Message de test"
}))

# Arrêter le consumer
consumer.stop()


# ============================================================================
# EXEMPLE 13 : Gestion des erreurs
# ============================================================================

# Logs invalides
invalid_logs = [
    # Manque service
    {"event_type": "event", "message": "msg"},
    # Manque message
    {"service": "MS Test", "event_type": "event"},
    # Niveau invalide
    {"service": "MS Test", "event_type": "event", "message": "msg", "level": "INVALID"},
]

for i, log_data in enumerate(invalid_logs, 1):
    success, message, log_id = use_case.execute(log_data)
    if not success:
        print(f"Log {i} rejeté: {message}")


# ============================================================================
# EXEMPLE 14 : Cas d'usage réaliste - Monitoring d'un système
# ============================================================================

# Simuler des événements d'un système distribué
system_events = [
    {
        "service": "MS Authentification",
        "event_type": "user_login",
        "message": "Utilisateur alice connecté",
        "level": "INFO"
    },
    {
        "service": "MS Collecte",
        "event_type": "data_collection_started",
        "message": "Collecte de données commencée"
    },
    {
        "service": "MS Analyse",
        "event_type": "analysis_started",
        "message": "Analyse des données commencée"
    },
    {
        "service": "MS Collecte",
        "event_type": "data_collection_error",
        "message": "Erreur lors de la collecte de données",
        "level": "ERROR"
    },
    {
        "service": "MS Alerte",
        "event_type": "alert_sent",
        "message": "Alerte d'erreur envoyée à l'administrateur",
        "level": "WARNING"
    }
]

print("\n=== MONITORING - Traitement des événements système ===\n")

for event in system_events:
    success, message, log_id = use_case.execute(event)
    status = "✓" if success else "✗"
    level = event.get("level", "INFO")
    print(f"{status} [{level}] {event['service']}: {event['event_type']}")

# Récupérer les statistiques
print("\n=== STATISTIQUES ===\n")
all_logs = use_case.get_all_logs()
print(f"Total de logs: {len(all_logs)}")

for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    count = len(use_case.get_logs_by_level(level))
    if count > 0:
        print(f"  {level}: {count}")

services = set(log.service for log in all_logs)
print(f"\nServices: {len(services)}")
for service in sorted(services):
    count = len(use_case.get_logs_by_service(service))
    print(f"  {service}: {count} logs")


# ============================================================================
# EXEMPLE 15 : Architecture hexagonale - Découplage
# ============================================================================

"""
L'architecture hexagonale permet de :

1. Changer facilement de repository (en mémoire -> SQLite -> PostgreSQL)
2. Changer le source des logs (RabbitMQ -> Kafka -> Direct)
3. Changer la validation (simple -> complexe avec règles métier)
4. Tester avec des mocks sans dépendances externes

Cela se fait sans modifier le cœur métier (Use Case et Domain).
"""

# On peut remplacer le repository à la volée
from src.adapters.database.log_repository_adapter import InMemoryLogRepository

# Repository en mémoire
in_memory_repo = InMemoryLogRepository()
dev_use_case = ProcessLogUseCase(in_memory_repo, validator)

# Repository SQLite
sqlite_repo = SQLiteLogRepository("logs.db")
prod_use_case = ProcessLogUseCase(sqlite_repo, validator)

# Les deux use cases fonctionnent exactement de la même façon
# mais avec des implémentations différentes de repository

print("\nArchitecture hexagonale permet la flexibilité:")
print("- Même interface pour toutes les implémentations")
print("- Facile à tester avec des mocks")
print("- Facile à déployer dans différents environnements")
