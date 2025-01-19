#!/usr/bin/python3

from flask import Flask, render_template, request, redirect, url_for
import mysql.connector, os, json

with open('/home/googlabill/ComDatabase/ManyCRUD/secrets.json', 'r') as secretFile:
    creds = json.load(secretFile)['mysqlCredentials']

connection = mysql.connector.connect(**creds)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/showCharacters', methods=['GET'])
def showCharacters():
    mycursor = connection.cursor()
    issueID = request.args.get('IssueID')  # Get IssueID from URL
    characterID = request.args.get('CharacterID')  # Get CharacterID from URL
    # Insert new character if parameters are provided
    newCharacterID = request.args.get('CharacterID')
    newFirst = request.args.get('FirstName')
    newLast = request.args.get('LastName')
    newMonicker = request.args.get('Monicker')
    
    if newCharacterID and newFirst and newLast and newMonicker:
        insert_query = "INSERT INTO ComicCharacter (CharacterID, FirstName, LastName, Monicker) VALUES (%s, %s, %s, %s)"
        mycursor.execute(insert_query, (newCharacterID, newFirst, newLast, newMonicker))
        connection.commit()

    # Handle deletion of a character
    elif request.args.get('delete') == 'true':
        deleteID = request.args.get('CharacterID')
        if deleteID:
            mycursor.execute("DELETE FROM ComicCharacter WHERE CharacterID=%s", (deleteID,))
            connection.commit()

    # Retrieve the issueID from the query parameter for filtering by issue
    issueID = request.args.get('issueID')
    if issueID:
        # Get characters associated with the given issueID
        mycursor.execute("""
            SELECT ComicCharacter.CharacterID, ComicCharacter.FirstName, ComicCharacter.LastName, ComicCharacter.Monicker
            FROM ComicCharacter
            JOIN Issue_Character ON ComicCharacter.CharacterID = Issue_Character.CharacterID
            JOIN Issue ON Issue.IssueID = Issue_Character.IssueID
            WHERE Issue_Character.IssueID = %s""", (issueID,))
        characters = mycursor.fetchall()
        pageTitle = f"Characters in Issue {issueID}:"
    else:
        # If no issueID is provided, show all characters
        mycursor.execute("SELECT CharacterID, FirstName, LastName, Monicker FROM ComicCharacter")
        pageTitle = "Showing all comic characters"
        characters = mycursor.fetchall()

    mycursor.close()
    return render_template('Characters.html', ComicCharacterList=characters, pageTitle=pageTitle)

@app.route("/ComicCharacter-update")
def updateCharacter():
    CharacterID = request.args.get('CharacterID')
    FirstName = request.args.get('FirstName')
    LastName = request.args.get('LastName')
    Monicker = request.args.get('Monicker')

    if CharacterID is None:
        return "Error, id not specified"
    elif FirstName is not None and LastName is not None:
        mycursor = connection.cursor()
        mycursor.execute("UPDATE ComicCharacter SET FirstName=%s, LastName=%s, Monicker=%s WHERE CharacterID=%s", 
                         (FirstName, LastName, Monicker, CharacterID))
        mycursor.close()
        connection.commit()
        return redirect(url_for('showCharacters'))

    mycursor = connection.cursor()
    mycursor.execute("SELECT CharacterID, FirstName, LastName, Monicker FROM ComicCharacter WHERE CharacterID=%s;", (CharacterID,))
    existingCharacter = mycursor.fetchone()
    mycursor.close()
    if existingCharacter:
        existingID, existingFirst, existingLast, existingMonicker = existingCharacter
        return render_template('ComicCharacter-update.html', 
                               existingID=existingID, 
                               existingFirst=existingFirst, 
                               existingLast=existingLast, 
                               existingMonicker=existingMonicker)
    else:
        return "Error, character not found"

@app.route('/showIssues', methods=['GET'])
def showIssues():
    connection = mysql.connector.connect(**creds)
    mycursor = connection.cursor()

    # Insert new issue if parameters are provided
    newIssueID = request.args.get('IssueID')
    newSeriesID = request.args.get('SeriesID')
    newYear = request.args.get('Year')
    newAuthor = request.args.get('Author')
    newArtist = request.args.get('Artist')
    newIssueNumber = request.args.get('IssueNumber')

    if newIssueID and newSeriesID and newYear and newAuthor and newArtist and newIssueNumber:
        insert_query = "INSERT INTO Issue (IssueID, SeriesID, Year, Author, Artist, IssueNumber) VALUES (%s, %s, %s, %s, %s, %s)"
        mycursor.execute(insert_query, (newIssueID, newSeriesID, newYear, newAuthor, newArtist, newIssueNumber))
        connection.commit()

    # Handle deletion of an issue
    elif request.args.get('delete') == 'true':
        deleteID = request.args.get('IssueID')
        if deleteID:
            mycursor.execute("DELETE FROM Issue WHERE IssueID=%s", (deleteID,))
            connection.commit()
    # Check if this is an update request
    updateID = request.args.get('IssueID')
    if updateID:
        mycursor.close()
        connection.close()
        return redirect(url_for('updateIssues', IssueID=updateID))
    # Initialize comicCharacterName with a default value
    comicCharacterName = "Unknown Character"

    # Get characterID from query string
    CharacterID = request.args.get('CharacterID')
    if CharacterID is not None:
        # Fetch character name
        mycursor.execute("""
            SELECT CONCAT(FirstName, ' ', LastName) AS CharacterName
            FROM ComicCharacter
            WHERE CharacterID = %s
        """, (CharacterID,))
        characterData = mycursor.fetchone()
        comicCharacterName = characterData[0] if characterData else "Unknown"

        # Handle IssueID insertion
        IssueID = request.args.get('IssueID')
        if IssueID is not None:
            try:
                mycursor.execute(
                    """INSERT INTO Issue_Character (IssueID, CharacterID) VALUES (%s, %s)""",
                    (IssueID, CharacterID)
                )
                connection.commit()
            except mysql.connector.Error as e:
                print(f"Database error during insertion: {e}")

        # Fetch issues associated with the character
        mycursor.execute("""
            SELECT Issue.IssueID, Series.Title, Issue.Year, Issue.Author, Issue.Artist, Issue.IssueNumber
            FROM ComicCharacter
            JOIN Issue_Character ON ComicCharacter.CharacterID = Issue_Character.CharacterID
            JOIN Issue ON Issue.IssueID = Issue_Character.IssueID
            JOIN Series ON Series.SeriesID = Issue.SeriesID
            WHERE ComicCharacter.CharacterID = %s
        """, (CharacterID,))
        issues = mycursor.fetchall()

        # Fetch other issues not associated with the character
        mycursor.execute("""
            SELECT Issue.IssueID, Issue.SeriesID, Issue.IssueNumber
            FROM Issue
            WHERE Issue.IssueID NOT IN (
                SELECT IssueID
                FROM Issue_Character
                WHERE Issue_Character.CharacterID = %s
            )
        """, (CharacterID,))
        otherIssues = mycursor.fetchall()

        pageTitle = f"Showing all issues for comic character: {comicCharacterName}"
    else:
        # Show all issues if no characterID is provided
        mycursor.execute("""
            SELECT Issue.IssueID, Issue.SeriesID, Issue.Year, Issue.Author, Issue.Artist, Issue.IssueNumber
            FROM Issue
            JOIN Author ON Issue.Author = Author.PersonID
            JOIN Artist ON Issue.Artist = Artist.PersonID
        """)
        pageTitle = "Showing all issues"
        issues = mycursor.fetchall()
        otherIssues = None

    mycursor.close()
    connection.close()
    return render_template('Issues.html',
                           issueList=issues,
                           pageTitle=pageTitle,
                           otherIssues=otherIssues,
                           CharacterID=CharacterID,
                           comicCharacterName=comicCharacterName)

@app.route("/Issues-update")
def updateIssues():
    IssueID = request.args.get('IssueID')
    SeriesID = request.args.get('SeriesID')
    Year = request.args.get('Year')
    AuthorID = request.args.get('AuthorID')
    ArtistID = request.args.get('ArtistID')
    IssueNumber = request.args.get('IssueNumber')
    
    if IssueID is None:
        return "Error, id not specified"
    elif SeriesID is not None and Year is not None and AuthorID is not None and ArtistID is not None and IssueNumber is not None and IssueID is not None:
        mycursor = connection.cursor()
        # Update the issue in the database
        mycursor.execute("UPDATE Issue SET IssueID=%s, SeriesID=%s, Year=%s, Author=%s, Artist=%s, IssueNumber=%s WHERE IssueID=%s",
        (SeriesID, Year, AuthorID, ArtistID, IssueNumber, IssueID))
        mycursor.close()
        connection.commit()
        return redirect(url_for('showIssues'))

    # Retrieve the existing issue details
    mycursor = connection.cursor()
    mycursor.execute("SELECT IssueID, SeriesID, Year, Author, Artist, IssueNumber FROM Issue WHERE IssueID=%s;", (IssueID,))
    existingIssue = mycursor.fetchone()
    mycursor.close()

    if existingIssue:
        existingIssueID, existingSeriesID, existingYear, existingAuthorID, existingArtistID, existingIssueNumber = existingIssue
        return render_template(
            'Issues-update.html', 
            existingIssueID=existingIssueID, 
            existingSeriesID=existingSeriesID, 
            existingYear=existingYear, 
            existingAuthorID=existingAuthorID, 
            existingArtistID=existingArtistID, 
            existingIssueNumber=existingIssueNumber)
    else:
        return "Error, issue not found"



if __name__ == '__main__':
    app.run(port=8000, debug=True, host="0.0.0.0")
