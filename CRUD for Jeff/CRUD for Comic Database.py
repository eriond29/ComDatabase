#!/usr/bin/python3

from flask import Flask, render_template, request, redirect, url_for
import mysql.connector, os, json

# Load MySQL credentials
with open('/home/googlabill/ComDatabase/CRUD for Jeff/secrets.json', 'r') as secretFile:
    creds = json.load(secretFile)['mysqlCredentials']

connection = mysql.connector.connect(**creds)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def showActors():
    mycursor = connection.cursor()

    # If there are name and desc 'GET' variables, insert the new value into the database
    newCharacterID = request.args.get('characterid')
    newFirst = request.args.get('firstname')
    newLast = request.args.get('lastname')
    newMonicker = request.args.get('monicker')
    if newCharacterID and newFirst and newLast and newMonicker is not None:
        insert_query = "INSERT INTO ComicCharacter (CharacterID, FirstName, LastName, Monicker) VALUES (%s, %s, %s, %s)"
        mycursor.execute(insert_query, (newCharacterID, newFirst, newLast, newMonicker))
        connection.commit()
    elif request.args.get('delete') == 'true':
        deleteID = request.args.get('id')
        mycursor.execute("DELETE FROM ComicCharacter WHERE CharacterID=%s", (deleteID,))
        connection.commit()

    # Fetch the current values of the ComicCharacter table
    mycursor.execute("SELECT * FROM ComicCharacter")
    myresult = mycursor.fetchall()
    mycursor.close()
    return render_template('ComicCharacter.html', collection=myresult)

@app.route("/ComicCharacter-update")
def updateCharacter():
    id = request.args.get('id')
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    monicker = request.args.get('monicker')

    if id is None:
        return "Error, id not specified"
    elif first_name is not None and last_name is not None:
        mycursor = connection.cursor()
        mycursor.execute("UPDATE ComicCharacter SET FirstName=%s, LastName=%s, Monicker=%s WHERE CharacterID=%s", 
                         (first_name, last_name, monicker, id))
        mycursor.close()
        connection.commit()
        return redirect(url_for('showActors'))

    mycursor = connection.cursor()
    mycursor.execute("SELECT CharacterID, FirstName, LastName, Monicker FROM ComicCharacter WHERE CharacterID=%s;", (id,))
    existingCharacter = mycursor.fetchone()
    mycursor.close()
    if existingCharacter:
        id, existingFirst, existingLast, existingMonicker = existingCharacter
        return render_template('ComicCharacter-update.html', id=id, existingFirst=existingFirst, 
                               existingLast=existingLast, existingMonicker=existingMonicker)
    else:
        return "Error, character not found"

if __name__ == '__main__':
    app.run(port=4000, debug=True, host="0.0.0.0")
