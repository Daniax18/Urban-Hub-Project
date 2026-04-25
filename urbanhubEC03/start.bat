@echo off
REM Script de démarrage du microservice Journalisation sur Windows

echo ╔════════════════════════════════════════════════════════════╗
echo ║   Microservice Journalisation - UrbanHub                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou n'est pas dans le PATH
    pause
    exit /b 1
)

echo ✓ Python détecté
echo.

REM Vérifier les dépendances
echo Vérification des dépendances...
python -m pip list | find "pytest" >nul
if errorlevel 1 (
    echo ⚠️  Installation des dépendances en cours...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Erreur lors de l'installation des dépendances
        pause
        exit /b 1
    )
)

echo ✓ Dépendances OK
echo.

REM Menu
echo Que voulez-vous faire ?
echo.
echo 1. Exécuter tous les tests
echo 2. Exécuter les tests avec couverture
echo 3. Exécuter les tests du domain
echo 4. Exécuter les tests de l'application
echo 5. Exécuter les tests des adapters
echo 6. Lancer le microservice
echo 7. Quitter
echo.

set /p choice="Entrez votre choix (1-7): "

if "%choice%"=="1" (
    echo.
    echo 🧪 Exécution de tous les tests...
    python -m pytest tests/unit/ -v --tb=short
) else if "%choice%"=="2" (
    echo.
    echo 📊 Exécution des tests avec couverture...
    python -m pytest tests/unit/ --cov=src --cov-report=html --cov-report=term-missing -v
    echo.
    echo 📁 Rapport de couverture généré : htmlcov/index.html
) else if "%choice%"=="3" (
    echo.
    echo 🧪 Exécution des tests du domain...
    python -m pytest tests/unit/domain/ -v
) else if "%choice%"=="4" (
    echo.
    echo 🧪 Exécution des tests de l'application...
    python -m pytest tests/unit/application/ -v
) else if "%choice%"=="5" (
    echo.
    echo 🧪 Exécution des tests des adapters...
    python -m pytest tests/unit/adapters/ -v
) else if "%choice%"=="6" (
    echo.
    echo 🚀 Démarrage du microservice...
    echo.
    set PYTHONPATH=%CD%
    python -m src.main
) else if "%choice%"=="7" (
    echo Au revoir !
    exit /b 0
) else (
    echo ❌ Choix invalide
    exit /b 1
)

pause
