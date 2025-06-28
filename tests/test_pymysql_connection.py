import pymysql

HOST = '127.0.0.1'
USER = 'webapp'
PASSWORD = 'motdepassefort'
DB = 'shoptub'
PORT = 3306

try:
    print(f"Test de connexion PyMySQL vers {DB}...")
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DB, port=PORT)
    with conn.cursor() as cursor:
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()[0]
        print(f"Connexion réussie à la base : {db_name}")
    conn.close()
    print("Test PyMySQL terminé avec succès.")
except Exception as e:
    print(f"Erreur de connexion PyMySQL : {e}")
    print("Vérifiez que le serveur MariaDB/MySQL est bien lancé et que les identifiants sont corrects.")

