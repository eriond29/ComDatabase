from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'stephen',
    'password': 'database',
    'database': 'sakila'
}

# Helper function to connect to the database
def get_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
    except Error as e:
        print(f"Error: '{e}'")
    return connection

# Route to display table data
@app.route('/')
def display_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customer")  # Adjust this query as needed
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('customers.html', customers=customers)
    
if __name__ == '__main__':
    app.run(debug=True)
