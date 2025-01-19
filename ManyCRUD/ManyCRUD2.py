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

@app.route('/', methods=['GET'])
def showActors():
    mycursor = connection.cursor()

    # If there are name and desc 'GET' variables, insert the new value into the database
    newCharacterID = request.args.get('newCharacterID')
    newFirst = request.args.get('newFirstName')
    newLast = request.args.get('newLastName')
    newMonicker = request.args.get('newMonicker')
    if newCharacterID and newFirst and newLast and newMonicker:
        insert_query = "INSERT INTO ComicCharacter (CharacterID, FirstName, LastName, Monicker) VALUES (%s, %s, %s, %s)"
        mycursor.execute(insert_query, (newCharacterID, newFirst, newLast, newMonicker))
        connection.commit()
    elif request.args.get('delete') == 'true':
        deleteID = request.args.get('CharacterID')
        print(f"Delete ID: {deleteID}")  # Debugging line
        mycursor.execute("DELETE FROM ComicCharacter WHERE CharacterID=%s", (deleteID,))
        connection.commit()


    # Fetch the current values of the ComicCharacter table
    mycursor.execute("SELECT * FROM ComicCharacter")
    myresult = mycursor.fetchall()
    mycursor.close()
    return render_template('Characters.html', collection=myresult)

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
        return redirect(url_for('showComicCharacters'))

    mycursor = connection.cursor()
    mycursor.execute("SELECT CharacterID, FirstName, LastName, Monicker FROM ComicCharacter WHERE CharacterID=%s;", (CharacterID,))
    existingCharacter = mycursor.fetchone()
    mycursor.close()
    if existingCharacter:
        existingID, existingFirst, existingLast, existingMonicker = existingCharacter
        return render_template('ComicCharacter-update.html', existingID=existingID, existingFirst=existingFirst, 
                               existingLast=existingLast, existingMonicker=existingMonicker)
    else:
        return "Error, character not found"

    

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
        mycursor.execute("""SELECT Issue.IssueID, Series.Title, Issue.Year, Issue.Author, Issue.Artist, Issue.IssueNumber
                            FROM ComicCharacter
                            JOIN Issue_Character ON ComicCharacter.CharacterID = Issue_Character.CharacterID
                            JOIN Issue ON Issue.IssueID = Issue_Character.IssueID
                            JOIN Series ON Series.SeriesID = Issue.SeriesID
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
    app.run(port=8000, debug=True, host="0.0.0.0")