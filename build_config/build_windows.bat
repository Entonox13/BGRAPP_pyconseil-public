@echo off
REM Script de build pour Windows - BGRAPP Pyconseil
REM Crée un exécutable portable (.exe) sans installation requise

echo.
echo ========================================
echo  BGRAPP Pyconseil - Build Windows
echo ========================================
echo.

REM Vérification que nous sommes dans le bon répertoire
if not exist "..\main.py" (
    echo ERREUR: Ce script doit être exécuté depuis le dossier build_config
    echo Le fichier main.py doit être présent dans le répertoire parent
    pause
    exit /b 1
)

REM Création d'un environnement virtuel de build
echo [1/5] Création de l'environnement virtuel de build...
python -m venv build_env
if %errorlevel% neq 0 (
    echo ERREUR: Impossible de créer l'environnement virtuel
    pause
    exit /b 1
)

REM Activation de l'environnement virtuel
echo [2/5] Activation de l'environnement virtuel...
call build_env\Scripts\activate.bat

REM Installation des dépendances de build
echo [3/5] Installation des dépendances...
pip install --upgrade pip
pip install -r requirements_build.txt
if %errorlevel% neq 0 (
    echo ERREUR: Impossible d'installer les dépendances
    pause
    exit /b 1
)

REM Nettoyage des anciens builds
echo [4/5] Nettoyage des anciens builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Construction de l'exécutable
echo [5/7] Construction de l'exécutable avec PyInstaller...
pyinstaller --clean pyconseil.spec
if %errorlevel% neq 0 (
    echo ERREUR: Échec de la construction avec PyInstaller
    pause
    exit /b 1
)

REM Vérification du résultat
if exist "dist\BGRAPP_Pyconseil.exe" (
    echo.
    echo ✅ SUCCESS: Exécutable créé avec succès !
    echo.
    echo 📁 Emplacement: %cd%\dist\BGRAPP_Pyconseil.exe
    echo 💾 Taille: 
    for %%A in ("dist\BGRAPP_Pyconseil.exe") do echo    %%~zA octets
    echo.
    
    REM Création du dossier releases et copie
    echo [6/7] Préparation de la release...
    if not exist "..\releases" mkdir "..\releases"
    if not exist "..\releases\latest" mkdir "..\releases\latest"
    
    REM Copie vers le dossier releases avec nom standardisé
    copy "dist\BGRAPP_Pyconseil.exe" "..\releases\latest\BGRAPP_Pyconseil_Latest_Windows.exe"
    
    REM Génération du checksum
    echo Génération du checksum SHA256...
    certutil -hashfile "..\releases\latest\BGRAPP_Pyconseil_Latest_Windows.exe" SHA256 > "..\releases\latest\BGRAPP_Pyconseil_Latest_Windows.exe.sha256"
    
    echo.
    echo 🎉 Release Windows prête !
    echo 📦 Fichier final: ..\releases\latest\BGRAPP_Pyconseil_Latest_Windows.exe
    echo 🔒 Checksum: ..\releases\latest\BGRAPP_Pyconseil_Latest_Windows.exe.sha256
    echo.
    echo L'exécutable est portable et peut être distribué sans installation.
    echo.
) else (
    echo.
    echo ❌ ERREUR: L'exécutable n'a pas été créé
    echo Vérifiez les logs ci-dessus pour plus d'informations
    echo.
)

REM Désactivation de l'environnement virtuel
call build_env\Scripts\deactivate.bat

echo.
echo Appuyez sur une touche pour continuer...
pause > nul 