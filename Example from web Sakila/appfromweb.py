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

# Route to add new customer
@app.route('/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        address_id = request.form['address_id']  # Assume address_id is a foreign key here

        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO customer (first_name, last_name, email, address_id, create_date)
        VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(insert_query, (first_name, last_name, email, address_id))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('display_customers'))
    return render_template('add_customer.html')

if __name__ == '__main__':
    app.run(debug=True)
