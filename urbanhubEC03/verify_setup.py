#!/usr/bin/env python3
"""
Script de vérification du projet
Valide que tout est correctement installé et configuré
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Vérifie la version de Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} (minimum requis: 3.8)")
        return False

def check_project_structure():
    """Vérifie la structure du projet"""
    required_dirs = [
        "src/domain",
        "src/application",
        "src/ports",
        "src/adapters/database",
        "src/adapters/rabbitmq",
        "src/adapters/api",
        "tests/unit/domain",
        "tests/unit/application",
        "tests/unit/adapters"
    ]

    required_files = [
        "requirements.txt",
        "pytest.ini",
        "README.md",
        "rule.md",
        "src/main.py",
        "src/domain/log.py",
        "src/application/process_log_use_case.py",
        "src/adapters/database/log_repository_adapter.py",
        "src/adapters/database/log_validator_adapter.py",
        "src/adapters/rabbitmq/log_consumer_adapter.py",
        "src/adapters/api/log_api_adapter.py",
        "tests/unit/domain/test_log.py",
        "tests/unit/application/test_process_log_use_case.py",
        "tests/unit/adapters/test_adapters.py"
    ]

    all_ok = True
    project_root = Path(".")

    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"✓ Répertoire {dir_path}")
        else:
            print(f"✗ Répertoire manquant: {dir_path}")
            all_ok = False

    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists() and full_path.is_file():
            print(f"✓ Fichier {file_path}")
        else:
            print(f"✗ Fichier manquant: {file_path}")
            all_ok = False

    return all_ok

def check_imports():
    """Vérifie que les imports fonctionnent"""
    try:
        from src.domain.log import Log, LogLevel
        print("✓ Import src.domain.log")

        from src.application.process_log_use_case import ProcessLogUseCase
        print("✓ Import src.application.process_log_use_case")

        from src.ports.log_repository_port import LogRepositoryPort
        print("✓ Import src.ports.log_repository_port")

        from src.ports.log_consumer_port import LogConsumerPort
        print("✓ Import src.ports.log_consumer_port")

        from src.ports.log_validator_port import LogValidatorPort
        print("✓ Import src.ports.log_validator_port")

        from src.adapters.database.log_repository_adapter import (
            InMemoryLogRepository, SQLiteLogRepository
        )
        print("✓ Import src.adapters.database.log_repository_adapter")

        from src.adapters.database.log_validator_adapter import LogValidator
        print("✓ Import src.adapters.database.log_validator_adapter")

        from src.adapters.rabbitmq.log_consumer_adapter import (
            RabbitMQLogConsumer, MockLogConsumer
        )
        print("✓ Import src.adapters.rabbitmq.log_consumer_adapter")

        from src.adapters.api.log_api_adapter import LogApiAdapter
        print("✓ Import src.adapters.api.log_api_adapter")

        return True

    except ImportError as e:
        print(f"✗ Erreur d'import: {e}")
        return False

def check_pytest():
    """Vérifie que pytest est installé"""
    try:
        import pytest
        print(f"✓ pytest {pytest.__version__}")
        return True
    except ImportError:
        print("✗ pytest not installed")
        return False

def check_dependencies():
    """Vérifie que les dépendances sont installées"""
    dependencies = ["pika", "pytest", "dotenv"]
    all_ok = True

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} manquant")
            all_ok = False

    return all_ok

def run_quick_tests():
    """Exécute quelques tests rapides"""
    try:
        from src.domain.log import Log
        from src.adapters.database.log_repository_adapter import InMemoryLogRepository
        from src.adapters.database.log_validator_adapter import LogValidator
        from src.application.process_log_use_case import ProcessLogUseCase

        # Créer les composants
        repo = InMemoryLogRepository()
        validator = LogValidator()
        use_case = ProcessLogUseCase(repo, validator)

        # Test: créer un log
        log_data = {
            "service": "MS Test",
            "event_type": "test",
            "message": "test"
        }

        success, msg, log_id = use_case.execute(log_data)
        if not success:
            print(f"✗ Erreur lors du traitement du log: {msg}")
            return False

        # Test: récupérer le log
        log = use_case.get_log_by_id(log_id)
        if not log:
            print("✗ Log non trouvé après sauvegarde")
            return False

        print("✓ Tests fonctionnels OK")
        return True

    except Exception as e:
        print(f"✗ Erreur lors des tests: {e}")
        return False

def main():
    """Fonction principale"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   Vérification du Microservice Journalisation              ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    all_ok = True

    print("1. Vérification de Python")
    print("-" * 60)
    if not check_python_version():
        all_ok = False
    print()

    print("2. Vérification de la structure du projet")
    print("-" * 60)
    if not check_project_structure():
        all_ok = False
    print()

    print("3. Vérification des imports")
    print("-" * 60)
    if not check_imports():
        all_ok = False
    print()

    print("4. Vérification des dépendances")
    print("-" * 60)
    if not check_dependencies():
        all_ok = False
    print()

    print("5. Vérification de pytest")
    print("-" * 60)
    if not check_pytest():
        print("  Pour installer pytest: pip install pytest")
        all_ok = False
    print()

    print("6. Tests fonctionnels")
    print("-" * 60)
    if not run_quick_tests():
        all_ok = False
    print()

    print("=" * 60)
    if all_ok:
        print("✓ TOUT EST OK - Prêt à utiliser !")
        return 0
    else:
        print("✗ Des problèmes ont été détectés")
        print("\nPour installer les dépendances:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
