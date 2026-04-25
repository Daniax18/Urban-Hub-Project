"""
Point d'entrée du microservice Journalisation
"""
import json
from src.domain.log import Log
from src.application.process_log_use_case import ProcessLogUseCase
from src.adapters.database.log_repository_adapter import InMemoryLogRepository
from src.adapters.database.log_validator_adapter import LogValidator
from src.adapters.rabbitmq.log_consumer_adapter import RabbitMQLogConsumer, MockLogConsumer
from src.adapters.api.log_api_adapter import LogApiAdapter


def main():
    """Point d'entrée principal du microservice"""

    # Initialisation des adapters
    log_repository = InMemoryLogRepository()
    log_validator = LogValidator()

    # Initialisation du use case
    process_log_use_case = ProcessLogUseCase(log_repository, log_validator)

    # Initialisation de l'API
    log_api = LogApiAdapter(process_log_use_case)

    # Initialisation du consumer RabbitMQ
    # (Utilise MockLogConsumer pour le développement)
    log_consumer = MockLogConsumer()

    def handle_message(message: str) -> None:
        """Traite un message reçu de RabbitMQ"""
        try:
            log_data = json.loads(message)
            success, msg, log_id = process_log_use_case.execute(log_data)
            if success:
                print(f"✓ Log processed: {log_id}")
            else:
                print(f"✗ Error: {msg}")
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON: {e}")
        except Exception as e:
            print(f"✗ Error processing message: {e}")

    # Démarrage du consumer
    print("Starting Log Microservice...")
    log_consumer.start(handle_message)

    # Exemple de publication de messages
    print("\nPublishing sample logs...")
    sample_logs = [
        {
            "service": "MS Alerte",
            "event_type": "notification_sent",
            "message": "Email envoyé avec succès",
            "level": "INFO"
        },
        {
            "service": "MS Analyse",
            "event_type": "analysis_completed",
            "message": "Analyse complétée",
            "level": "INFO"
        },
        {
            "service": "MS Collecte",
            "event_type": "error_occurred",
            "message": "Erreur lors de la collecte",
            "level": "ERROR"
        }
    ]

    for log_data in sample_logs:
        log_consumer.publish_message(json.dumps(log_data))

    # Affichage des logs via l'API
    print("\nAll logs:")
    result = log_api.get_all_logs()
    print(json.dumps(result, indent=2))

    print("\nError logs:")
    result = log_api.get_logs_by_level("ERROR")
    print(json.dumps(result, indent=2))

    log_consumer.stop()
    print("\nLog Microservice stopped.")


if __name__ == "__main__":
    main()
