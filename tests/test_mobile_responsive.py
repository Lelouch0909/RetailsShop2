#!/usr/bin/env python3
"""
Test de vérification de la responsivité mobile
Ce script vérifie que tous les fichiers nécessaires sont présents et bien configurés
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Vérifie qu'un fichier existe"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - MANQUANT")
        return False

def check_css_content(file_path, keywords):
    """Vérifie que le CSS contient les mots-clés nécessaires"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        missing_keywords = []
        for keyword in keywords:
            if keyword not in content:
                missing_keywords.append(keyword)
        
        if not missing_keywords:
            print(f"✅ CSS Mobile: Tous les styles nécessaires présents")
            return True
        else:
            print(f"❌ CSS Mobile: Styles manquants: {', '.join(missing_keywords)}")
            return False
    except Exception as e:
        print(f"❌ Erreur lecture CSS: {e}")
        return False

def check_js_content(file_path, keywords):
    """Vérifie que le JS contient les fonctionnalités nécessaires"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        missing_keywords = []
        for keyword in keywords:
            if keyword not in content:
                missing_keywords.append(keyword)
        
        if not missing_keywords:
            print(f"✅ JS Mobile: Toutes les fonctionnalités présentes")
            return True
        else:
            print(f"❌ JS Mobile: Fonctionnalités manquantes: {', '.join(missing_keywords)}")
            return False
    except Exception as e:
        print(f"❌ Erreur lecture JS: {e}")
        return False

def check_template_content(file_path, keywords):
    """Vérifie que le template contient les éléments nécessaires"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        missing_keywords = []
        for keyword in keywords:
            if keyword not in content:
                missing_keywords.append(keyword)
        
        if not missing_keywords:
            print(f"✅ Template: {file_path} - Éléments mobiles présents")
            return True
        else:
            print(f"⚠️  Template: {file_path} - Éléments optionnels manquants: {', '.join(missing_keywords)}")
            return True  # Non bloquant pour les templates
    except Exception as e:
        print(f"❌ Erreur lecture template: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🔍 Vérification de la responsivité mobile - Retail Shop")
    print("=" * 60)
    
    base_path = "/home/lelouch/Retail"
    all_tests_passed = True
    
    # 1. Vérification des fichiers principaux
    print("\n📁 Vérification des fichiers...")
    
    files_to_check = [
        (f"{base_path}/RetailShop/static/css/mobile-responsive.css", "CSS Mobile"),
        (f"{base_path}/RetailShop/static/js/mobile-responsive.js", "JS Mobile"),
        (f"{base_path}/RetailShop/templates/layout.html", "Layout principal"),
        (f"{base_path}/RetailShop/templates/includes/_modern_navbar.html", "Navbar"),
        (f"{base_path}/MOBILE_RESPONSIVE_GUIDE.md", "Guide responsive")
    ]
    
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_tests_passed = False
    
    # 2. Vérification du contenu CSS
    print("\n🎨 Vérification du CSS mobile...")
    
    css_keywords = [
        "@media (max-width: 768px)",
        ".mobile-menu-toggle",
        ".nav-menu-container",
        ".product-grid",
        ".auth-form",
        "--mobile-breakpoint"
    ]
    
    css_path = f"{base_path}/RetailShop/static/css/mobile-responsive.css"
    if not check_css_content(css_path, css_keywords):
        all_tests_passed = False
    
    # 3. Vérification du contenu JavaScript
    print("\n⚡ Vérification du JS mobile...")
    
    js_keywords = [
        "mobile-menu-toggle",
        "addEventListener",
        "isMobile()",
        "touchstart",
        "resize"
    ]
    
    js_path = f"{base_path}/RetailShop/static/js/mobile-responsive.js"
    if not check_js_content(js_path, js_keywords):
        all_tests_passed = False
    
    # 4. Vérification des templates
    print("\n📄 Vérification des templates...")
    
    # Layout
    layout_keywords = ["mobile-responsive.css", "mobile-responsive.js", "viewport"]
    layout_path = f"{base_path}/RetailShop/templates/layout.html"
    check_template_content(layout_path, layout_keywords)
    
    # Navbar
    navbar_keywords = ["mobile-menu-toggle", "hamburger-line", "nav-menu-container"]
    navbar_path = f"{base_path}/RetailShop/templates/includes/_modern_navbar.html"
    check_template_content(navbar_path, navbar_keywords)
    
    # Auth templates
    auth_keywords = ["auth-container", "auth-form", "auth-card"]
    auth_templates = [
        f"{base_path}/RetailShop/templates/login.html",
        f"{base_path}/RetailShop/templates/register.html"
    ]
    
    for template_path in auth_templates:
        if os.path.exists(template_path):
            check_template_content(template_path, auth_keywords)
    
    # 5. Vérification de la structure des media queries
    print("\n📱 Vérification des media queries...")
    
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        media_queries = [
            "@media (max-width: 768px)",
            "@media (max-width: 480px)",
            "@media (orientation: landscape)"
        ]
        
        found_queries = []
        for query in media_queries:
            if query in css_content:
                found_queries.append(query)
        
        if len(found_queries) >= 2:
            print(f"✅ Media queries: {len(found_queries)} trouvées")
        else:
            print(f"⚠️  Media queries: Seulement {len(found_queries)} trouvées")
            
    except Exception as e:
        print(f"❌ Erreur vérification media queries: {e}")
    
    # 6. Résumé final
    print("\n" + "=" * 60)
    
    if all_tests_passed:
        print("🎉 SUCCÈS: Tous les tests de responsivité mobile sont passés!")
        print("\n📋 Prochaines étapes:")
        print("1. Démarrez l'application Flask")
        print("2. Testez sur différentes tailles d'écran")
        print("3. Vérifiez le menu hamburger mobile")
        print("4. Testez les formulaires sur mobile")
        print("5. Validez la grille de produits responsive")
        
        print("\n🔧 Commandes de test:")
        print("- Ouvrez Chrome DevTools (F12)")
        print("- Activez le mode responsive (Ctrl+Shift+M)")
        print("- Testez différentes tailles: 375px, 768px, 1024px")
        
    else:
        print("❌ ÉCHEC: Certains tests ont échoué")
        print("⚠️  Vérifiez les fichiers manquants avant de continuer")
        
    print("\n📖 Documentation: Consultez MOBILE_RESPONSIVE_GUIDE.md")
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main())
