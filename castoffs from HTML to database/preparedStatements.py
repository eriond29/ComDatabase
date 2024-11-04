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
    newFirst = request.args.get('firstname')
    newLast = request.args.get('lastname')
    newLast = request.args.get('lastname')
    newLast = request.args.get('lastname')
    if newFirst is not None and newLast is not None:
        mycursor.execute("INSERT into ComicCharacter (CharacterID, FirstName, LastName, Monicker) values (%s, %s)", (CharacterID, FirstName, LastName, Monicker))
        connection.commit()

    # Fetch the current values of the speaker table
    mycursor.execute("Select CharacterID, FirstName, LastName, Monicker FROM ComicCharacter")
    myresult = mycursor.fetchall()
    mycursor.close()
    connection.close()
    return render_template('actor-list.html', collection=myresult)
    #return "Hello world"


if __name__ == '__main__':
    app.run(port=8000, debug=True, host="0.0.0.0")