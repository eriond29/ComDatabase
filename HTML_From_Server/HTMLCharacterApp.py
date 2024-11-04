#!/usr/bin/python3

from flask import Flask, render_template, request
import mysql.connector, os
import json


app = Flask(__name__)


@app.route('/', methods=['GET'])

def showSpeakers():
    with open('/home/googlabill/ComDatabase/HTML_From_Server/secrets.json', 'r') as secretFile:
        creds = json.load(secretFile)['mysqlCredentials']

    connection = mysql.connector.connect(**creds)
    
    mycursor = connection.cursor()

    # If there is a name and desc 'GET' variable, insert the new value into the database
    newCharacterID = request.args.get('characterid')
    newFirst = request.args.get('firstname')
    newLast = request.args.get('lastname')
    newMonicker = request.args.get('monicker')  # Optional field for monicker
    if newCharacterID and newFirst and newLast and newMonicker is not None:
        insert_query = "INSERT INTO ComicCharacter (CharacterID, FirstName, LastName, Monicker) VALUES (%s, %s, %s, %s)"
        mycursor.execute(insert_query, (newCharacterID, newFirst, newLast, newMonicker))
        connection.commit()

    # Fetch the current values of the speaker table
    mycursor.execute("SELECT CharacterID, FirstName, LastName, Monicker FROM ComicCharacter")
    myresult = mycursor.fetchall()
    mycursor.close()
    connection.close()
    return render_template('Comic Characters.html', collection=myresult)

if __name__ == '__main__':
    app.run(port=8000, debug=True, host="0.0.0.0")
