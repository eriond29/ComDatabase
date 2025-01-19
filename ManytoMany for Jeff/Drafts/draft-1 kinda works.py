#!/usr/bin/python3

from flask import Flask, render_template, request, redirect, url_for
import mysql.connector, os, json

with open('secrets.json', 'r') as secretFile:
    creds = json.load(secretFile)['mysqlCredentials']

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/showCharacters', methods=['GET'])
def showComicCharacters():
    connection = mysql.connector.connect(**creds)
    mycursor = connection.cursor()

    # If there is an issue_id 'GET' variable, use this to refine the query
    issueID = request.args.get('issue_id')
    if issueID is not None:
        mycursor.execute("""SELECT ComicCharacter.CharacterID, FirstName, LastName, IssueNumber 
                            FROM ComicCharacter
                            JOIN Issue_Character ON ComicCharacter.id = Issue_Character.CharacterID
                            JOIN Issue ON IssueID = Issue_Character.IssueID
                            WHERE IssueID = %s""", (issueID,))
        myresult = mycursor.fetchall()
        if len(myresult) >= 1:
            title = myresult[0][3]
            issueNumber = myresult[0][4]
        else:
            title = issueNumber = "Unknown"
        pageTitle = f"Showing all comic characters in issue {issueID}, {title} ({issueNumber})"
    else:
        mycursor.execute("SELECT CharacterID, FirstName, LastName, Monicker FROM ComicCharacter")
        pageTitle = "Showing all comic characters"
        myresult = mycursor.fetchall()

    mycursor.close()
    connection.close()
    return render_template('Characters.html', ComicCharacterList=myresult, pageTitle=pageTitle)

@app.route('/showIssues', methods=['GET'])
def showIssues():
    connection = mysql.connector.connect(**creds)
    mycursor = connection.cursor()

    # If there is a character_id 'GET' variable, use this to refine the query
    characterID = request.args.get('character_id')
    if characterID is not None:
        # Check if the character is being added to a new issue
        registerIssueID = request.args.get('register_issue_id')
        if registerIssueID is not None:
            mycursor.execute("""INSERT INTO Issue_Character (CharacterID, IssueID) VALUES (%s, %s)
                             """, (characterID, registerIssueID))
            connection.commit()

        mycursor.execute("""SELECT IssueID, SeriesID, IssueNumber, FirstName, LastName 
                            FROM ComicCharacter
                            JOIN Issue_Character ON ComicCharacter.id = Issue_Character.CharacterID
                            JOIN Issue ON IssueID = Issue_Character.IssueID
                            WHERE ComicCharacter.id = %s""", (characterID,))
        issues = mycursor.fetchall()
        print(issues)
        if len(issues) >= 1:
            comicCharacterName = issues[0][3] + " " + issues[0][4]
            mycursor.execute("""SELECT IssueID, SeriesID, IssueNumber
                                FROM Issue
                                WHERE IssueID NOT IN (
                                    SELECT IssueID
                                    FROM Issue_Character
                                    WHERE Issue_Character.CharacterID = %s
                                )
                             """, (characterID,))
            otherIssues = mycursor.fetchall()
            print(otherIssues)
        else:
            comicCharacterName = "Unknown"
            otherIssues = None
        pageTitle = f"Showing all issues for comic character: {comicCharacterName}"
    else:
        mycursor.execute("""SELECT IssueID, IssueNumber FROM Issue""")
        pageTitle = "Showing all issues"
        issues = mycursor.fetchall()
        otherIssues = None

    mycursor.close()
    connection.close()
    print(f"{characterID=}")
    return render_template('Issues.html', 
                           issueList=issues, 
                           pageTitle=pageTitle, 
                           otherIssues=otherIssues, 
                           characterID=characterID
                           )


if __name__ == '__main__':
    app.run(port=7000, debug=True, host="0.0.0.0")
