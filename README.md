# PHASES DU PROJET REPETCENTER 
## Jour-1
### 1. Creation d un depot sur github
### 2. Creation d un environnement virtuel 
```bash
python3 -m venv virtuel

source virtuel/bin/activate
```
### 3. Installation des dependances 
```bash 
pip install django psycopg2-binary djangorestframework \
  djangorestframework-simplejwt python-decouple \
  pillow weasyprint
```
### 4. Configuration du projet et des applications 
```bash
``Projet :``
django-admin startproject config . 

``Applivation :``
python3 manage.py startapp accounts      # M1 - Auth & utilisateurs
python3 manage.py startapp centre        # M2 - Configuration du centre
python3 manage.py startapp apprenants    # M3 - Gestion apprenants
python3 manage.py startapp enseignants   # M4 - Gestion enseignants
python3 manage.py startapp emploidutemps # M5 - EDT
python3 manage.py startapp presences     # M6 - Présences
python3 manage.py startapp paiements     # M7 - Paiements & factures
python3 manage.py startapp notes         # M8 - Notes & bulletins
python3 manage.py startapp messagerie    # M9 - Messagerie interne
python3 manage.py startapp notifications # M10 - Notifications

```
### 5. Configuration de la base de donnee 
### 6. Configurer le simplejwt
### 7. Configuration du fichier .env
### 8. Realiser les migrations 
### 9. Configurer tailwindcss 
### 10. configuration du fichier input et du fichier output
