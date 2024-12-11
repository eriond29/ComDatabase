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

    
    # Handle unregistering of a character
   
   # Get the CharacterID and IssueID from the request arguments
        character_id = request.args.get('CharacterID')
        issue_id = request.args.get('IssueID')

        if character_id and issue_id:
            try:
                # Debugging: Ensure the parameters are correctly received
                print(f"Attempting to unregister CharacterID: {character_id} from IssueID: {issue_id}")

                # Delete the relationship between the character and the issue from Issue_Character
                mycursor.execute("DELETE FROM Issue_Character WHERE CharacterID=%s AND IssueID=%s", (character_id, issue_id))
                connection.commit()
                print(f"Successfully unregistered CharacterID {character_id} from IssueID {issue_id}.")
            except mysql.connector.Error as e:
                print(f"Error during unregistering: {e}")
                connection.rollback()
        else:
            print("Error: Missing CharacterID or IssueID")

    

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

        # Check for unregister parameter
    character_id = request.args.get('CharacterID')
    issue_id = request.args.get('IssueID')
    unregister = request.args.get('unregister')

    # If unregister is set to 'true', perform the deletion
    if unregister == 'true' and character_id and issue_id:
        mycursor.execute("DELETE FROM Issue_Character WHERE CharacterID=%s AND IssueID=%s", (character_id, issue_id))
        connection.commit()

    # Fetch issues associated with the character if CharacterID is provided
    if character_id:
        mycursor.execute("""
            SELECT Issue.IssueID, Issue.SeriesID, Issue.Year, Issue.Author, Issue.Artist, Issue.IssueNumber
            FROM Issue
            JOIN Issue_Character ON Issue_Character.IssueID = Issue.IssueID
            WHERE Issue_Character.CharacterID = %s""", (character_id,))
        issues = mycursor.fetchall()
        pageTitle = f"Showing all issues for character: {character_id}"
    else:
        # If no CharacterID is provided, show all issues
        mycursor.execute("""
            SELECT Issue.IssueID, Series.Title, Issue.Year, Issue.Author, Issue.Artist, Issue.IssueNumber
            FROM Issue
            JOIN Series ON Series.SeriesID = Issue.SeriesID
        """)
        issues = mycursor.fetchall()
        pageTitle = "Showing all issues"

    

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
        return redirect(url_for('showIssues'))


     # Handle deletion of an issue
    if request.args.get('delete') == 'true':
        deleteID = request.args.get('IssueID')
        if deleteID:
            mycursor.execute("DELETE FROM Issue WHERE IssueID=%s", (deleteID,))
            connection.commit()
        return redirect(url_for('showIssues'))


    # Get CharacterID from query string
    CharacterID = request.args.get('CharacterID')
    print(f"Received CharacterID: {CharacterID}")  # Debugging

    comicCharacterName = "Unknown Character"  # Default name if not found

    if CharacterID:
        # Fetch character name
        mycursor.execute("""
            SELECT CONCAT(FirstName, ' ', LastName) AS CharacterName
            FROM ComicCharacter
            WHERE CharacterID = %s
        """, (CharacterID,))
        characterData = mycursor.fetchone()
        comicCharacterName = characterData[0] if characterData else "Unknown Character"

        # Get IssueID from query string
        IssueID = request.args.get('IssueID')
        print(f"Received IssueID: {IssueID}")  # Debugging

        if IssueID:
            try:
                print(f"Attempting to insert CharacterID: {CharacterID}, IssueID: {IssueID}")
                mycursor.execute(
                    """INSERT INTO Issue_Character (IssueID, CharacterID) VALUES (%s, %s)""",
                    (IssueID, CharacterID)
                )
                connection.commit()
                print("Insertion successful!")  # Debugging
            except mysql.connector.IntegrityError:
                print(f"Character {CharacterID} is already associated with Issue {IssueID}.")
            except mysql.connector.Error as e:
                print(f"Database error during insertion: {e}")
        else:
            print(f"Invalid or missing IssueID: {IssueID}")  # Debugging

        # Fetch issues associated with the character
        mycursor.execute("""
            SELECT Issue.IssueID, Issue.SeriesID, Issue.Year, Issue.Author, Issue.Artist, Issue.IssueNumber
            FROM ComicCharacter
            JOIN Issue_Character ON ComicCharacter.CharacterID = Issue_Character.CharacterID
            JOIN Issue ON Issue.IssueID = Issue_Character.IssueID
            JOIN Series ON Series.SeriesID = Issue.SeriesID
            WHERE ComicCharacter.CharacterID = %s""", (CharacterID,))
        issues = mycursor.fetchall()
        print(f"Issues fetched for CharacterID {CharacterID}: {issues}")  # Debugging

        # Fetch other issues not associated with the character
        mycursor.execute("""
            SELECT Issue.IssueID, Issue.SeriesID, Issue.Year, Issue.Author, Issue.Artist, Issue.IssueNumber
            FROM Issue
            JOIN Series ON Series.SeriesID = Issue.SeriesID
            WHERE Issue.IssueID NOT IN (
                SELECT IssueID
                FROM Issue_Character
                WHERE CharacterID = %s
            )
        """, (CharacterID,))
        otherIssues = mycursor.fetchall()

        pageTitle = f"Showing all issues for comic character: {comicCharacterName}"
    else:
        # Show all issues if no CharacterID is provided
        print("No CharacterID provided. Showing all issues.")
        mycursor.execute("""
            SELECT Issue.IssueID, Series.Title, Issue.Year, Issue.Author, Issue.Artist, Issue.IssueNumber
            FROM Issue
            JOIN Series ON Series.SeriesID = Issue.SeriesID
        """)
        issues = mycursor.fetchall()


        otherIssues = None
        pageTitle = "Showing all issues"

    mycursor.close()
    connection.close()

    print(f"CharacterID being passed to template: {CharacterID}")  # Debugging: check if CharacterID is passed correctly
    print(f"Final CharacterID: {CharacterID}")  # Debugging
    return render_template(
        'Issues.html',
        issueList=issues,
        pageTitle=pageTitle,
        otherIssues=otherIssues,
        CharacterID=CharacterID,
        comicCharacterName=comicCharacterName  # Pass character name to the template
    )


@app.route('/Issues-update', methods=['GET'])
def updateIssues():
    IssueID = request.args.get('IssueID')
    SeriesID = request.args.get('SeriesID')
    Year = request.args.get('Year')
    Author = request.args.get('Author')
    Artist = request.args.get('Artist')
    IssueNumber = request.args.get('IssueNumber')
    print(f"IssueID: {IssueID}, SeriesID: {SeriesID}, Year: {Year}, Author: {Author}, Artist: {Artist}, IssueNumber: {IssueNumber}")

    if IssueID is None:
        return "Error, id not specified"

    # If all necessary fields are provided, update the issue
    if IssueID and SeriesID and Year and Author and Artist and IssueNumber:
        mycursor = connection.cursor()
        # Update the issue in the database
        print("Query: ", """
        UPDATE Issue 
        SET SeriesID=%s, Year=%s, Author=%s, Artist=%s, IssueNumber=%s
        WHERE IssueID=%s
        """)
        print("Params: ", (SeriesID, Year, Author, Artist, IssueNumber, IssueID))
        
        mycursor.execute("""
            UPDATE Issue 
            SET SeriesID=%s, Year=%s, Author=%s, Artist=%s, IssueNumber=%s
            WHERE IssueID=%s
        """, (SeriesID, Year, Author, Artist, IssueNumber, IssueID ))

        connection.commit()
        mycursor.close()

        # Redirect back to the showIssues page to view updated list
        return redirect(url_for('showIssues'))
    #return "Error: Missing parameters", 400

    # Retrieve existing issue details for the form (if update not performed yet)
    mycursor = connection.cursor()
    mycursor.execute("SELECT IssueID, SeriesID, Year, Author, Artist, IssueNumber FROM Issue WHERE IssueID=%s;", (IssueID,))
    existingIssue = mycursor.fetchone()
    mycursor.close()

    if existingIssue:
        existingIssueID, existingSeriesID, existingYear, existingAuthor, existingArtist, existingIssueNumber = existingIssue
        return render_template(
            'Issues-update.html', 
            existingIssueID=existingIssueID, 
            existingSeriesID=existingSeriesID, 
            existingYear=existingYear, 
            existingAuthor=existingAuthor, 
            existingArtist=existingArtist, 
            existingIssueNumber=existingIssueNumber
        )
    else:
        return "Error, issue not found"




if __name__ == '__main__':
    app.run(port=8000, debug=True, host="0.0.0.0")
