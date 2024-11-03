#!/usr/bin/python3

from flask import Flask, render_template, request
import mysql.connector, os
import json


app = Flask(__name__)


@app.route('/', methods=['GET'])


def index():
    return render_template('character-get.html')


def showSpeakers():
    with open('/home/googlabill/ComDatabase/HTML_From_Server/secrets.json', 'r') as secretFile:
        creds = json.load(secretFile)['mysqlCredentials']



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
    return render_template('Comic Characters.html', collection=myresult)

if __name__ == '__main__':
    app.run(port=8000, debug=True, host="0.0.0.0")
