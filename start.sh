#!/bin/bash

# Démarrer le serveur pour MetaLLM
python start_metallm.py &

# Démarrer le serveur Django
python manage.py runserver 
