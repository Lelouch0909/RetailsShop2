from flask import Flask
from flask_pymysql import MySQL
import sys
import flask
import importlib.metadata
import pymysql

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'webapp'
app.config['MYSQL_PASSWORD'] = 'motdepassefort'
app.config['MYSQL_DB'] = 'shoptub'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Debug: Afficher les versions
print(f"Flask version: {flask.__version__}")
try:
    pymysql_version = pymysql.__version__
    print(f"PyMySQL version: {pymysql_version}")
except Exception as e:
    print(f"Impossible d'obtenir la version de PyMySQL: {e}")

# Initialize MySQL
mysql = MySQL(app)

# Test connection
try:
    with app.app_context():
        conn = mysql.connection
        if conn is None:
            print("MySQL connection failed: connection object is None (mysql.connection is None)")
            print("Vérifiez que le module PyMySQL est bien installé et compatible avec votre version de Python.")
            sys.exit(1)
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()['DATABASE()']
        print(f"Successfully connected to database: {db_name}")
        cursor.close()
except Exception as e:
    print(f"Error connecting to MySQL: {e}")
    print("Please check if MySQL server is running and the credentials are correct.")
    print("Database: shoptub, User: webapp, Password: motdepassefort")
    sys.exit(1)

print("Database connection test completed successfully.")
