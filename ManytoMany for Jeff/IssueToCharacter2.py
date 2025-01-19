#!/usr/bin/python3

from flask import Flask, render_template, request, redirect, url_for
import mysql.connector, os, json

with open('/home/googlabill/ComDatabase/ManytoMany for Jeff/secrets.json', 'r') as secretFile:
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
        # If issueID is provided, get the characters associated with that issue
        mycursor.execute("""
            SELECT ComicCharacter.CharacterID, ComicCharacter.FirstName, ComicCharacter.LastName, ComicCharacter.Monicker
            FROM ComicCharacter
            JOIN Issue_Character ON ComicCharacter.CharacterID = Issue_Character.CharacterID
            JOIN Issue ON Issue.IssueID = Issue_Character.IssueID
            WHERE Issue_Character.IssueID = %s""", (issueID,)) #problem was here-where clause trying to connect from Issue.IssueID instead of issue_character
            #JOIN Issue ON Issue.IssueID = Issue_Character.IssueID was redundant and pulled from above the where statement
        characters = mycursor.fetchall()
        print(f"Characters for issueID {issueID}: {characters}")  # Check the fetched characters
        if len(characters) >= 1:
           # title = characters[0][3]  # Assuming 'Monicker' is the title of the issue (adjust if necessary)
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

    # Get characterID from query string
    CharacterID = request.args.get('CharacterID')  # Make sure the name matches 'CharacterID'
    print(f"Received CharacterID: {CharacterID}")  # Debugging

    if CharacterID is not None:
        # Get IssueID from query string
        IssueID = request.args.get('IssueID')  # Ensure 'IssueID' matches the form field
        print(f"Received IssueID: {IssueID}")  # Debugging
        
        if IssueID is not None:
            try:
                print(f"Attempting to insert CharacterID: {CharacterID}, IssueID: {IssueID}")
                mycursor.execute(
                    """INSERT INTO Issue_Character (IssueID, CharacterID) VALUES (%s, %s)""",
                    (IssueID, CharacterID)  # Use 'IssueID' and 'CharacterID' for insertion
                )
                connection.commit()
                print("Insertion successful!")  # Debugging
            except mysql.connector.Error as e:
                print(f"Database error during insertion: {e}")  # Debugging
        else:
            print(f"Invalid or missing IssueID: {IssueID}")  # Debugging

        # Fetch issues associated with the character
        mycursor.execute("""SELECT Issue.IssueID, Issue.SeriesID, Issue.Year, Issue.Author, Issue.Artist, Issue.IssueNumber
                            FROM ComicCharacter
                            JOIN Issue_Character ON ComicCharacter.CharacterID = Issue_Character.CharacterID
                            JOIN Issue ON Issue.IssueID = Issue_Character.IssueID
                            WHERE ComicCharacter.CharacterID = %s""", (CharacterID,))
        issues = mycursor.fetchall()
        print(f"Issues fetched for CharacterID {CharacterID}: {issues}")  # Debugging

        if len(issues) >= 1:
            comicCharacterName = issues[0][3] + " " + issues[0][4]
            mycursor.execute("""SELECT Issue.IssueID, Issue.SeriesID, Issue.IssueNumber
                                FROM Issue
                                WHERE Issue.IssueID NOT IN (
                                    SELECT IssueID
                                    FROM Issue_Character
                                    WHERE Issue_Character.CharacterID = %s
                                )
                             """, (CharacterID,))
            otherIssues = mycursor.fetchall()
            print(f"Other issues for CharacterID {CharacterID}: {otherIssues}")  # Debugging
        else:
            comicCharacterName = "Unknown"
            otherIssues = None
        pageTitle = f"Showing all issues for comic character: {comicCharacterName}"
    else:
        # Show all issues if no characterID is provided
        mycursor.execute("""SELECT Issue.IssueID, Issue.SeriesID, Issue.Year, Issue.Author, Issue.Artist, Issue.IssueNumber 
                            FROM Issue
                            JOIN Author ON Issue.Author = Author.PersonID
                            JOIN Artist ON Issue.Artist = Artist.PersonID""")
        pageTitle = "Showing all issues"
        issues = mycursor.fetchall()
        print(f"All issues fetched: {issues}")  # Debugging
        otherIssues = None

    mycursor.close()
    connection.close()
    print(f"CharacterID being passed to template: {CharacterID}")  # Debugging: check if characterID is passed correctly
    print(f"Final CharacterID: {CharacterID}")  # Debugging
    return render_template('Issues.html', 
                           issueList=issues, 
                           pageTitle=pageTitle, 
                           otherIssues=otherIssues, 
                           CharacterID=CharacterID
                           )

if __name__ == '__main__':
    app.run(port=7000, debug=True, host="0.0.0.0")