# database.py
import mysql.connector
from PyQt6.QtWidgets import QMessageBox

def create_connection():
    """Establishes a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="K@$hif.@139",  # <--- REPLACE WITH YOUR ACTUAL PASSWORD
            database="store_db"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None