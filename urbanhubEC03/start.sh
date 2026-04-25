#!/bin/bash
# Script de démarrage du microservice Journalisation sur Linux/Mac

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Microservice Journalisation - UrbanHub                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python n'est pas installé"
    exit 1
fi

echo "✓ Python détecté: $(python3 --version)"
echo ""

# Vérifier les dépendances
echo "Vérification des dépendances..."
if ! python3 -m pip list | grep -q "pytest"; then
    echo "⚠️  Installation des dépendances en cours..."
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Erreur lors de l'installation des dépendances"
        exit 1
    fi
fi

echo "✓ Dépendances OK"
echo ""

# Menu
echo "Que voulez-vous faire ?"
echo ""
echo "1. Exécuter tous les tests"
echo "2. Exécuter les tests avec couverture"
echo "3. Exécuter les tests du domain"
echo "4. Exécuter les tests de l'application"
echo "5. Exécuter les tests des adapters"
echo "6. Lancer le microservice"
echo "7. Quitter"
echo ""

read -p "Entrez votre choix (1-7): " choice

case $choice in
    1)
        echo ""
        echo "🧪 Exécution de tous les tests..."
        python3 -m pytest tests/unit/ -v --tb=short
        ;;
    2)
        echo ""
        echo "📊 Exécution des tests avec couverture..."
        python3 -m pytest tests/unit/ --cov=src --cov-report=html --cov-report=term-missing -v
        echo ""
        echo "📁 Rapport de couverture généré : htmlcov/index.html"
        ;;
    3)
        echo ""
        echo "🧪 Exécution des tests du domain..."
        python3 -m pytest tests/unit/domain/ -v
        ;;
    4)
        echo ""
        echo "🧪 Exécution des tests de l'application..."
        python3 -m pytest tests/unit/application/ -v
        ;;
    5)
        echo ""
        echo "🧪 Exécution des tests des adapters..."
        python3 -m pytest tests/unit/adapters/ -v
        ;;
    6)
        echo ""
        echo "🚀 Démarrage du microservice..."
        echo ""
        export PYTHONPATH="${PWD}"
        python3 -m src.main
        ;;
    7)
        echo "Au revoir !"
        exit 0
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac
