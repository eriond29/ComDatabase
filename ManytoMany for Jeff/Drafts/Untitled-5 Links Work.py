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

    # Retrieve the issueID from the query parameter
    issueID = request.args.get('issueID')

    # Print issueID to check if it's being passed correctly
    print(issueID)
    ##issueID = request.args.get('issue_id')  # Get the character_id from the URL
    if issueID is not None:
        # If issueID is provided, fetch the characters associated with that issue
        mycursor.execute("""
            SELECT ComicCharacter.CharacterID, ComicCharacter.FirstName, ComicCharacter.LastName, ComicCharacter.Monicker
            FROM ComicCharacter
            JOIN Issue_Character ON ComicCharacter.CharacterID = Issue_Character.CharacterID
            #JOIN Issue ON Issue.IssueID = Issue_Character.IssueID
            WHERE Issue_Character.IssueID = %s""", (issueID,)) #problem was here-where clause trying to connect from Issue.IssueID instead of issue_character
            #JOIN Issue ON Issue.IssueID = Issue_Character.IssueID was redundant and pulled from above the where statement
        characters = mycursor.fetchall()
        print(f"Characters for issueID {issueID}: {characters}")  # Check the fetched characters
        if len(characters) > 0:
            title = characters[0][3]  # Assuming 'Monicker' is the title of the issue (adjust if necessary)
            pageTitle = f"Characters in Issue {issueID}:"
        else:
            pageTitle = f"No characters found for Issue {issueID}"
    else:
        # If no issueID is provided, show all characters
        mycursor.execute("SELECT CharacterID, FirstName, LastName, Monicker FROM ComicCharacter")
        pageTitle = "Showing all comic characters"
        characters = mycursor.fetchall()

    mycursor.close()
    connection.close()

    return render_template('Characters.html', ComicCharacterList=characters, pageTitle=pageTitle)


@app.route('/showIssues', methods=['GET'])
def showIssues():
    connection = mysql.connector.connect(**creds)
    mycursor = connection.cursor()

    # If there is a character_id 'GET' variable, use this to refine the query
    characterID = request.args.get('characterID')
    print(characterID)
    #characterID = request.args.get('character_id')  # Get the character_id from the URL
    if characterID is not None:
        # Check if the character is being added to a new issue
    
        mycursor.execute("""SELECT Issue.IssueID, Issue.SeriesID, Issue.IssueNumber, ComicCharacter.FirstName, ComicCharacter.LastName 
                            FROM ComicCharacter
                            JOIN Issue_Character ON ComicCharacter.CharacterID = Issue_Character.CharacterID
                            JOIN Issue ON Issue.IssueID = Issue_Character.IssueID
                            WHERE ComicCharacter.CharacterID = %s""", (characterID,))
        issues = mycursor.fetchall()
        ###print(f"Issues for CharacterID {characterID}: {issues}")
        print(issues)
        if len(issues) >= 1:
            comicCharacterName = issues[0][3] + " " + issues[0][4]
            mycursor.execute("""SELECT Issue.IssueID, Issue.SeriesID, Issue.IssueNumber
                                FROM Issue
                                WHERE Issue.IssueID NOT IN (
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
    else:    ##the select statement needs to be joined to get better results
        mycursor.execute("""SELECT Issue.IssueID, SeriesID, Year, Author, Artist, Issue.IssueNumber FROM Issue""")
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
    app.run(port=4000, debug=True, host="0.0.0.0")
