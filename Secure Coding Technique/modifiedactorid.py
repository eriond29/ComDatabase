#!/usr/bin/python3

from flask import Flask, request
import mysql.connector
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def showTable():
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=os.getenv('SQL_HOST', 'localhost'),
            user=os.getenv('SQL_USER', 'stephen'),
            password=os.getenv('SQL_PWD', 'database'),
            db=os.getenv('SQL_DB', 'sakila')
        )
        
        mycursor = connection.cursor()
        
        # Get the 'id' parameter from the query string
        id = request.args.get('id')
        
        if id:
            # Prepare and execute a parameterized query for a specific actor
            sqlstring = "SELECT * FROM actor WHERE actor_id = %s"
            print("Executing query:", sqlstring % id)  # Debugging
            mycursor.execute(sqlstring, (id,))
        else:
            # Prepare and execute a query to return all actors
            sqlstring = "SELECT * FROM actor"
            print("Executing query:", sqlstring)  # Debugging
            mycursor.execute(sqlstring)

        myresult = mycursor.fetchall()

        # Close cursor and connection
        mycursor.close()
        connection.close()
        
        # Check if we got results
        if not myresult:
            return "No results found for the provided ID."
        
        # Format the output for display
        output = "<br />\n".join([str(row) for row in myresult])
        return output
    
    except mysql.connector.Error as err:
        # Handle and display database errors
        print("Database error:", err)
        return f"Database error: {err}"
    
    except Exception as e:
        # Catch any other exceptions
        print("An error occurred:", e)
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(port=8000, debug=True, host="0.0.0.0")
