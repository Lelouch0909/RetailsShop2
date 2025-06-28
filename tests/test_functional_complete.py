#!/usr/bin/env python3
"""
Test fonctionnel complet du workflow utilisateur et admin
Simule un parcours utilisateur complet et vérifie la cohérence des données
"""

import sys
import os
import time
from datetime import datetime

# Ajouter le dossier parent au path pour importer l'app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    from RetailShop.db_helper import execute_query
    from passlib.hash import sha256_crypt
    print("✓ Import de l'application réussi")
except ImportError as e:
    print(f"✗ Erreur d'import: {e}")
    sys.exit(1)

class FunctionalTester:
    def __init__(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.test_user_id = None
        self.test_product_id = None
        
    def cleanup_test_data(self):
        """Nettoyer les données de test"""
        try:
            with self.app.app_context():
                if self.test_user_id:
                    execute_query("DELETE FROM cart WHERE user_id = %s", (self.test_user_id,), commit=True)
                    execute_query("DELETE FROM orders WHERE uid = %s", (self.test_user_id,), commit=True)
                    execute_query("DELETE FROM users WHERE id = %s", (self.test_user_id,), commit=True)
                print("✓ Données de test nettoyées")
        except Exception as e:
            print(f"⚠ Erreur lors du nettoyage: {e}")
    
    def test_user_registration_flow(self):
        """Test du workflow complet d'inscription utilisateur"""
        print("\n=== TEST DU WORKFLOW D'INSCRIPTION ===")
        
        try:
            with self.app.app_context():
                # Données de test
                test_data = {
                    'name': 'Test User Functional',
                    'email': f'test_functional_{int(time.time())}@example.com',
                    'username': f'testfunc{int(time.time())}',
                    'password': 'testpassword123',
                    'mobile': '1234567890'
                }
                
                # 1. Simuler l'inscription
                password_hash = sha256_crypt.encrypt(test_data['password'])
                execute_query(
                    "INSERT INTO users(name, email, username, password, mobile) VALUES(%s, %s, %s, %s, %s)",
                    (test_data['name'], test_data['email'], test_data['username'], password_hash, test_data['mobile']),
                    commit=True
                )
                
                # 2. Vérifier que l'utilisateur est créé
                user = execute_query(
                    "SELECT * FROM users WHERE username = %s", 
                    (test_data['username'],), 
                    fetchone=True
                )
                
                if user:
                    self.test_user_id = user['id']
                    print(f"✓ Utilisateur créé avec ID: {self.test_user_id}")
                    
                    # 3. Vérifier la validation du mot de passe
                    if sha256_crypt.verify(test_data['password'], user['password']):
                        print("✓ Validation du mot de passe OK")
                        return True
                    else:
                        print("✗ Erreur de validation du mot de passe")
                        return False
                else:
                    print("✗ Erreur création utilisateur")
                    return False
                    
        except Exception as e:
            print(f"✗ Erreur dans le test d'inscription: {e}")
            return False
    
    def test_login_session_flow(self):
        """Test du workflow de connexion et session"""
        print("\n=== TEST DU WORKFLOW DE CONNEXION ===")
        
        if not self.test_user_id:
            print("✗ Pas d'utilisateur de test disponible")
            return False
        
        try:
            with self.app.app_context():
                # Récupérer les données utilisateur
                user = execute_query(
                    "SELECT * FROM users WHERE id = %s", 
                    (self.test_user_id,), 
                    fetchone=True
                )
                
                if not user:
                    print("✗ Utilisateur de test non trouvé")
                    return False
                
                # Simuler une session utilisateur
                with self.client.session_transaction() as sess:
                    sess['logged_in'] = True
                    sess['uid'] = self.test_user_id
                    sess['s_name'] = user['name']
                
                # Vérifier l'accès aux pages protégées
                response = self.client.get('/cart')
                if response.status_code == 200:
                    print("✓ Accès au panier autorisé pour utilisateur connecté")
                else:
                    print(f"✗ Problème d'accès au panier: {response.status_code}")
                    return False
                
                # Mettre à jour le statut en ligne
                execute_query("UPDATE users SET online = '1' WHERE id = %s", (self.test_user_id,), commit=True)
                print("✓ Statut utilisateur mis à jour")
                
                return True
                
        except Exception as e:
            print(f"✗ Erreur dans le test de connexion: {e}")
            return False
    
    def test_product_cart_flow(self):
        """Test du workflow d'ajout au panier"""
        print("\n=== TEST DU WORKFLOW PANIER ===")
        
        if not self.test_user_id:
            print("✗ Pas d'utilisateur de test disponible")
            return False
        
        try:
            with self.app.app_context():
                # Récupérer un produit disponible
                product = execute_query(
                    "SELECT * FROM products WHERE available > 0 LIMIT 1", 
                    fetchone=True
                )
                
                if not product:
                    print("✗ Aucun produit disponible pour le test")
                    return False
                
                self.test_product_id = product['id']
                print(f"✓ Produit de test sélectionné: {product['pName']} (ID: {self.test_product_id})")
                
                # S'assurer que la table cart existe
                execute_query("""
                    CREATE TABLE IF NOT EXISTS cart (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        product_id INT NOT NULL,
                        quantity INT NOT NULL DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE KEY unique_user_product (user_id, product_id)
                    )
                """, (), commit=True)
                
                # Ajouter au panier
                execute_query(
                    "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (self.test_user_id, self.test_product_id, 2),
                    commit=True
                )
                
                # Vérifier l'ajout
                cart_item = execute_query(
                    "SELECT * FROM cart WHERE user_id = %s AND product_id = %s",
                    (self.test_user_id, self.test_product_id),
                    fetchone=True
                )
                
                if cart_item and cart_item['quantity'] == 2:
                    print("✓ Produit ajouté au panier avec succès")
                    
                    # Test de récupération des items du panier
                    cart_items = execute_query("""
                        SELECT c.id, c.quantity, p.pName, p.price, p.available
                        FROM cart c
                        JOIN products p ON c.product_id = p.id
                        WHERE c.user_id = %s
                    """, (self.test_user_id,), fetchall=True)
                    
                    if cart_items and len(cart_items) > 0:
                        print(f"✓ Récupération panier OK: {len(cart_items)} article(s)")
                        return True
                    else:
                        print("✗ Erreur récupération panier")
                        return False
                else:
                    print("✗ Erreur ajout au panier")
                    return False
                    
        except Exception as e:
            print(f"✗ Erreur dans le test panier: {e}")
            return False
    
    def test_order_placement_flow(self):
        """Test du workflow de commande"""
        print("\n=== TEST DU WORKFLOW DE COMMANDE ===")
        
        if not self.test_user_id or not self.test_product_id:
            print("✗ Données de test manquantes")
            return False
        
        try:
            with self.app.app_context():
                # Récupérer le produit et l'utilisateur
                product = execute_query(
                    "SELECT * FROM products WHERE id = %s", 
                    (self.test_product_id,), 
                    fetchone=True
                )
                user = execute_query(
                    "SELECT * FROM users WHERE id = %s", 
                    (self.test_user_id,), 
                    fetchone=True
                )
                
                if not product or not user:
                    print("✗ Produit ou utilisateur non trouvé")
                    return False
                
                # Simuler une commande
                order_data = {
                    'uid': self.test_user_id,
                    'pid': self.test_product_id,
                    'ofname': user['name'],
                    'mobile': user['mobile'] or '1234567890',
                    'oplace': 'Adresse de test, 12345 Test City',
                    'quantity': 1,
                    'ddate': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Insérer la commande
                execute_query(
                    "INSERT INTO orders(uid, pid, ofname, mobile, oplace, quantity, ddate) VALUES(%s, %s, %s, %s, %s, %s, %s)",
                    (order_data['uid'], order_data['pid'], order_data['ofname'], 
                     order_data['mobile'], order_data['oplace'], order_data['quantity'], order_data['ddate']),
                    commit=True
                )
                
                # Vérifier la commande
                order = execute_query(
                    "SELECT * FROM orders WHERE uid = %s AND pid = %s ORDER BY id DESC LIMIT 1",
                    (self.test_user_id, self.test_product_id),
                    fetchone=True
                )
                
                if order:
                    print(f"✓ Commande créée avec ID: {order['id']}")
                    
                    # Vérifier que la commande est visible côté admin
                    all_orders = execute_query("SELECT * FROM orders", fetchall=True)
                    admin_can_see = any(o['id'] == order['id'] for o in (all_orders or []))
                    
                    if admin_can_see:
                        print("✓ Commande visible côté admin")
                        return True
                    else:
                        print("✗ Commande non visible côté admin")
                        return False
                else:
                    print("✗ Erreur création commande")
                    return False
                    
        except Exception as e:
            print(f"✗ Erreur dans le test de commande: {e}")
            return False
    
    def test_admin_access_flow(self):
        """Test du workflow d'accès admin"""
        print("\n=== TEST DU WORKFLOW ADMIN ===")
        
        try:
            with self.app.app_context():
                # Vérifier qu'il y a des admins
                admin = execute_query("SELECT * FROM admin LIMIT 1", fetchone=True)
                
                if not admin:
                    print("✗ Aucun admin trouvé dans la base")
                    return False
                
                print(f"✓ Admin trouvé: {admin['email']}")
                
                # Simuler une session admin
                with self.client.session_transaction() as sess:
                    sess['admin_logged_in'] = True
                    sess['admin_uid'] = admin['id']
                    sess['admin_name'] = f"{admin['firstName']} {admin['lastName']}"
                
                # Test d'accès aux pages admin
                admin_pages = ['/admin', '/orders', '/users']
                
                for page in admin_pages:
                    response = self.client.get(page)
                    if response.status_code == 200:
                        print(f"✓ Accès page admin {page} OK")
                    else:
                        print(f"✗ Erreur accès page admin {page}: {response.status_code}")
                        return False
                
                # Vérifier la visibilité des commandes
                orders = execute_query("SELECT * FROM orders", fetchall=True)
                if orders and len(orders) > 0:
                    print(f"✓ Admin peut voir {len(orders)} commande(s)")
                else:
                    print("⚠ Aucune commande visible pour l'admin")
                
                return True
                
        except Exception as e:
            print(f"✗ Erreur dans le test admin: {e}")
            return False
    
    def test_data_consistency(self):
        """Test de cohérence des données"""
        print("\n=== TEST DE COHÉRENCE DES DONNÉES ===")
        
        try:
            with self.app.app_context():
                # Vérifier les relations entre tables
                
                # 1. Commandes avec utilisateurs valides
                orphan_orders = execute_query("""
                    SELECT o.* FROM orders o 
                    LEFT JOIN users u ON o.uid = u.id 
                    WHERE o.uid IS NOT NULL AND u.id IS NULL
                """, fetchall=True)
                
                if orphan_orders:
                    print(f"⚠ {len(orphan_orders)} commande(s) avec utilisateur invalide")
                else:
                    print("✓ Toutes les commandes ont des utilisateurs valides")
                
                # 2. Commandes avec produits valides
                orphan_product_orders = execute_query("""
                    SELECT o.* FROM orders o 
                    LEFT JOIN products p ON o.pid = p.id 
                    WHERE p.id IS NULL
                """, fetchall=True)
                
                if orphan_product_orders:
                    print(f"⚠ {len(orphan_product_orders)} commande(s) avec produit invalide")
                else:
                    print("✓ Toutes les commandes ont des produits valides")
                
                # 3. Panier avec utilisateurs et produits valides
                orphan_cart = execute_query("""
                    SELECT c.* FROM cart c 
                    LEFT JOIN users u ON c.user_id = u.id 
                    LEFT JOIN products p ON c.product_id = p.id
                    WHERE u.id IS NULL OR p.id IS NULL
                """, fetchall=True)
                
                if orphan_cart:
                    print(f"⚠ {len(orphan_cart)} article(s) panier avec références invalides")
                else:
                    print("✓ Tous les articles du panier ont des références valides")
                
                # 4. Statistiques générales
                stats = {
                    'users': execute_query("SELECT COUNT(*) as count FROM users", fetchone=True),
                    'products': execute_query("SELECT COUNT(*) as count FROM products", fetchone=True),
                    'orders': execute_query("SELECT COUNT(*) as count FROM orders", fetchone=True),
                    'admin': execute_query("SELECT COUNT(*) as count FROM admin", fetchone=True),
                    'cart_items': execute_query("SELECT COUNT(*) as count FROM cart", fetchone=True)
                }
                
                print("\n📊 STATISTIQUES DE LA BASE:")
                for table, result in stats.items():
                    count = result['count'] if result else 0
                    print(f"   {table}: {count}")
                
                return True
                
        except Exception as e:
            print(f"✗ Erreur dans le test de cohérence: {e}")
            return False
    
    def run_functional_tests(self):
        """Exécuter tous les tests fonctionnels"""
        print("🔍 DÉBUT DES TESTS FONCTIONNELS COMPLETS")
        print("=" * 60)
        
        tests = [
            ("Inscription utilisateur", self.test_user_registration_flow),
            ("Connexion et session", self.test_login_session_flow),
            ("Ajout au panier", self.test_product_cart_flow),
            ("Placement de commande", self.test_order_placement_flow),
            ("Accès admin", self.test_admin_access_flow),
            ("Cohérence des données", self.test_data_consistency)
        ]
        
        passed = 0
        total = len(tests)
        
        try:
            for test_name, test_func in tests:
                print(f"\n🧪 Test: {test_name}")
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} - RÉUSSI")
                else:
                    print(f"❌ {test_name} - ÉCHOUÉ")
        
        finally:
            # Nettoyer les données de test
            print("\n🧹 Nettoyage des données de test...")
            self.cleanup_test_data()
        
        print("\n" + "=" * 60)
        print(f"📊 RÉSULTATS FONCTIONNELS: {passed}/{total} tests réussis")
        
        if passed == total:
            print("🎉 TOUS LES TESTS FONCTIONNELS SONT PASSÉS !")
            print("✅ L'application est prête pour la production")
        elif passed >= total * 0.8:
            print("⚠️  La plupart des tests fonctionnels sont passés")
            print("🔧 Quelques ajustements mineurs nécessaires")
        else:
            print("❌ Plusieurs problèmes fonctionnels détectés")
            print("🛠️  Révision approfondie nécessaire")
        
        return passed == total

if __name__ == "__main__":
    tester = FunctionalTester()
    success = tester.run_functional_tests()
    sys.exit(0 if success else 1)
