#!/usr/bin/env python3
# Test script pour vérifier que l'application fonctionne avec MySQL

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, '/home/lelouch/Retail')

try:
    print("🔄 Test de chargement de l'application...")
    from RetailShop import app, mysql
    print("✅ Application chargée avec succès!")
    
    print("🔄 Test de connexion MySQL...")
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as count FROM products")
        result = cur.fetchone()
        cur.close()
        print(f"✅ MySQL connecté! Nombre de produits: {result['count']}")
    
    print("🔄 Test des routes...")
    from RetailShop.routes import *
    print("✅ Routes chargées avec succès!")
    
    print("\n🎉 TOUS LES TESTS RÉUSSIS!")
    print("L'application est prête à fonctionner avec MySQL uniquement.")
    print("\nPour lancer l'application:")
    print("export FLASK_APP=app.py")
    print("flask run")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)
