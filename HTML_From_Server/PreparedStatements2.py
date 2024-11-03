#!/usr/bin/python3

from flask import Flask, render_template, request
import mysql.connector
import json
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def showSpeakers():
    # Load credentials
    with open('/home/googlabill/ComDatabase/HTML_From_Server/secrets.json', 'r') as secretFile:
        creds = json.load(secretFile)['mysqlCredentials']

    # Establish a database connection
    connection = mysql.connector.connect(**creds)
    mycursor = connection.cursor()

    try:
        # Get 'CharacterID', 'firstname', 'lastname', and 'monicker' from query parameters if available
        newCharacterID = request.args.get('characterid')
        newFirst = request.args.get('firstname')
        newLast = request.args.get('lastname')
        newMonicker = request.args.get('monicker')  # Optional field for monicker

        # Insert new values if all necessary fields are provided
        if newCharacterID and newFirst and newLast and newMonicker:
            insert_query = "INSERT INTO ComicCharacter (CharacterID, FirstName, LastName, Monicker) VALUES (%s, %s, %s, %s)"
            mycursor.execute(insert_query, (newCharacterID, newFirst, newLast, newMonicker))
            connection.commit()

        # Fetch all records from ComicCharacter table
        mycursor.execute("SELECT CharacterID, FirstName, LastName, Monicker FROM ComicCharacter")
        myresult = mycursor.fetchall()

    finally:
        # Ensure the cursor and connection are closed
        mycursor.close()
        connection.close()

    # Render the template with fetched data
    return render_template('actor-list.html', collection=myresult)

if __name__ == '__main__':
    app.run(port=8000, debug=True, host="0.0.0.0")
