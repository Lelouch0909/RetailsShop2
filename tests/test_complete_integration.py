#!/usr/bin/env python3
"""
Test complet de l'intégration front/back/base de données
Vérifie :
1. Authentification (login/register)
2. Gestion des accès selon les rôles (user/admin)
3. Accès au panier
4. Commandes et affichage côté admin
5. Structure de la base de données
"""

import sys
import os
import time
from flask import Flask

# Ajouter le dossier parent au path pour importer l'app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    from RetailShop.db_helper import execute_query, get_db
    from RetailShop import mysql
    print("✓ Import de l'application réussi")
except ImportError as e:
    print(f"✗ Erreur d'import: {e}")
    sys.exit(1)

class IntegrationTester:
    def __init__(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        
    def test_database_connection(self):
        """Test de connexion à la base de données"""
        print("\n=== TEST DE CONNEXION BASE DE DONNÉES ===")
        try:
            with self.app.app_context():
                # Test de la connexion
                result = execute_query("SELECT 1 as test", fetchone=True)
                if result and result['test'] == 1:
                    print("✓ Connexion à la base de données OK")
                    return True
                else:
                    print("✗ Problème de connexion à la base de données")
                    return False
        except Exception as e:
            print(f"✗ Erreur de connexion à la base de données: {e}")
            return False
    
    def test_database_tables(self):
        """Vérification de l'existence des tables principales"""
        print("\n=== TEST DES TABLES DE LA BASE DE DONNÉES ===")
        required_tables = ['users', 'admin', 'products', 'orders', 'cart']
        
        try:
            with self.app.app_context():
                for table in required_tables:
                    result = execute_query(f"SHOW TABLES LIKE '{table}'", fetchone=True)
                    if result:
                        print(f"✓ Table '{table}' existe")
                    else:
                        print(f"✗ Table '{table}' manquante")
                        return False
                return True
        except Exception as e:
            print(f"✗ Erreur lors de la vérification des tables: {e}")
            return False
    
    def test_authentication_routes(self):
        """Test des routes d'authentification"""
        print("\n=== TEST DES ROUTES D'AUTHENTIFICATION ===")
        
        # Test de la page de login
        try:
            response = self.client.get('/login')
            if response.status_code == 200:
                print("✓ Route /login accessible")
            else:
                print(f"✗ Route /login erreur: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Erreur route /login: {e}")
            return False
        
        # Test de la page de register
        try:
            response = self.client.get('/register')
            if response.status_code == 200:
                print("✓ Route /register accessible")
            else:
                print(f"✗ Route /register erreur: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Erreur route /register: {e}")
            return False
        
        return True
    
    def test_admin_access_protection(self):
        """Test de la protection des routes admin"""
        print("\n=== TEST DE PROTECTION DES ROUTES ADMIN ===")
        
        # Test d'accès sans être connecté en tant qu'admin
        try:
            response = self.client.get('/admin', follow_redirects=False)
            if response.status_code == 302:  # Redirection vers login admin
                print("✓ Route /admin protégée (redirection)")
            else:
                print(f"✗ Route /admin non protégée: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Erreur test protection admin: {e}")
            return False
        
        # Test de la page de login admin
        try:
            response = self.client.get('/admin_login')
            if response.status_code == 200:
                print("✓ Route /admin_login accessible")
            else:
                print(f"✗ Route /admin_login erreur: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Erreur route /admin_login: {e}")
            return False
        
        return True
    
    def test_cart_access_protection(self):
        """Test de la protection de l'accès au panier"""
        print("\n=== TEST DE PROTECTION DU PANIER ===")
        
        # Test d'accès au panier sans être connecté
        try:
            response = self.client.get('/cart', follow_redirects=False)
            if response.status_code == 302:  # Redirection vers login
                print("✓ Route /cart protégée (redirection)")
            else:
                print(f"✗ Route /cart non protégée: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Erreur test protection cart: {e}")
            return False
        
        return True
    
    def test_product_display(self):
        """Test de l'affichage des produits"""
        print("\n=== TEST D'AFFICHAGE DES PRODUITS ===")
        
        # Test de la page d'accueil
        try:
            response = self.client.get('/')
            if response.status_code == 200:
                print("✓ Page d'accueil accessible")
                # Vérifier si des produits sont affichés (basique)
                if b'product' in response.data or b'tshirt' in response.data:
                    print("✓ Produits détectés sur la page d'accueil")
                else:
                    print("⚠ Aucun produit détecté sur la page d'accueil")
            else:
                print(f"✗ Page d'accueil erreur: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Erreur page d'accueil: {e}")
            return False
        
        # Test des pages de catégorie
        categories = ['tshirt', 'wallet', 'belt', 'shoes']
        for category in categories:
            try:
                response = self.client.get(f'/{category}')
                if response.status_code == 200:
                    print(f"✓ Page catégorie /{category} accessible")
                else:
                    print(f"✗ Page catégorie /{category} erreur: {response.status_code}")
            except Exception as e:
                print(f"✗ Erreur page {category}: {e}")
        
        return True
    
    def test_database_sample_data(self):
        """Vérification de la présence de données de test"""
        print("\n=== TEST DES DONNÉES DE LA BASE ===")
        
        try:
            with self.app.app_context():
                # Vérifier qu'il y a des produits
                products = execute_query("SELECT COUNT(*) as count FROM products", fetchone=True)
                if products and products['count'] > 0:
                    print(f"✓ {products['count']} produits trouvés dans la base")
                else:
                    print("⚠ Aucun produit dans la base de données")
                
                # Vérifier qu'il y a un admin
                admin = execute_query("SELECT COUNT(*) as count FROM admin", fetchone=True)
                if admin and admin['count'] > 0:
                    print(f"✓ {admin['count']} admin(s) trouvé(s) dans la base")
                else:
                    print("⚠ Aucun admin dans la base de données")
                
                return True
        except Exception as e:
            print(f"✗ Erreur lors de la vérification des données: {e}")
            return False
    
    def test_session_functionality(self):
        """Test basique du système de session"""
        print("\n=== TEST DU SYSTÈME DE SESSION ===")
        
        try:
            with self.client.session_transaction() as sess:
                # Test d'ajout d'une variable de session
                sess['test_var'] = 'test_value'
            
            # Vérifier que la session fonctionne
            with self.client.session_transaction() as sess:
                if sess.get('test_var') == 'test_value':
                    print("✓ Système de session fonctionnel")
                    return True
                else:
                    print("✗ Problème avec le système de session")
                    return False
        except Exception as e:
            print(f"✗ Erreur test session: {e}")
            return False
    
    def check_email_functionality(self):
        """Vérification de la présence de fonctionnalités email"""
        print("\n=== VÉRIFICATION DES FONCTIONNALITÉS EMAIL ===")
        
        # Chercher des imports ou fonctions liés à l'email
        email_imports = ['flask_mail', 'smtplib', 'email']
        email_found = False
        
        try:
            # Vérifier les imports dans les fichiers Python
            import inspect
            from RetailShop import routes
            
            source = inspect.getsource(routes)
            for email_import in email_imports:
                if email_import in source:
                    email_found = True
                    print(f"✓ Import email détecté: {email_import}")
            
            if not email_found:
                print("⚠ Aucune fonctionnalité d'envoi d'email détectée")
                print("  Recommandation: Implémenter Flask-Mail pour les confirmations")
            
            return True
        except Exception as e:
            print(f"✗ Erreur vérification email: {e}")
            return False
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🔍 DÉBUT DES TESTS D'INTÉGRATION FRONT/BACK/DATABASE")
        print("=" * 60)
        
        tests = [
            self.test_database_connection,
            self.test_database_tables,
            self.test_authentication_routes,
            self.test_admin_access_protection,
            self.test_cart_access_protection,
            self.test_product_display,
            self.test_database_sample_data,
            self.test_session_functionality,
            self.check_email_functionality
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"✗ Erreur dans le test {test.__name__}: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 RÉSULTATS: {passed}/{total} tests réussis")
        
        if passed == total:
            print("🎉 Tous les tests sont passés ! L'intégration semble correcte.")
        elif passed >= total * 0.8:
            print("⚠️  La plupart des tests sont passés. Quelques ajustements nécessaires.")
        else:
            print("❌ Plusieurs problèmes détectés. Vérification approfondie nécessaire.")
        
        return passed == total

if __name__ == "__main__":
    tester = IntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
