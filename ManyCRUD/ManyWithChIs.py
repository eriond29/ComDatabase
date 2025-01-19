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
        return redirect(url_for('showIssues'))

     # Handle deletion of an issue
    elif request.args.get('delete') == 'true':
        deleteID = request.args.get('IssueID')
        if deleteID:
            mycursor.execute("DELETE FROM Issue WHERE IssueID=%s", (deleteID,))
            connection.commit()
        return redirect(url_for('showIssues'))
    # Check if this is an update request
    updateID = request.args.get('IssueID')
    if updateID:
        mycursor.close()
        connection.close()
        return redirect(url_for('updateIssues', IssueID=updateID))
    # Initialize comicCharacterName with a default value
    comicCharacterName = "Unknown Character"


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

        # Fetch issues associated with the character
        mycursor.execute("""
            SELECT Issue.IssueID, Issue.SeriesID, Issue.Year, Issue.Author, Issue.Artist, Issue.IssueNumber
            FROM ComicCharacter
            JOIN Issue_Character ON ComicCharacter.CharacterID = Issue_Character.CharacterID
            JOIN Issue ON Issue.IssueID = Issue_Character.IssueID
            JOIN Series ON Series.SeriesID = Issue.SeriesID
            WHERE ComicCharacter.CharacterID = %s
        """, (CharacterID,))
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

    return render_template(
        'Issues.html',
        issueList=issues,
        pageTitle=pageTitle,
        otherIssues=otherIssues,
        CharacterID=CharacterID,
        comicCharacterName=comicCharacterName  # Pass character name to the template
    )


from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/Issues-update', methods=['GET', 'POST'])
def updateIssues():
    try:
        print("Endpoint '/Issues-update' accessed.")

        # Retrieve the IssueID from the query parameters
        IssueID = request.args.get('IssueID')
        print(f"Received IssueID: {IssueID}")

        if not IssueID:
            print("Error: No IssueID provided.")
            return jsonify({"error": "IssueID is required"}), 400

        # Connect to the database
        print("Connecting to database...")
        conn = sqlite3.connect('ComicsDatabase.db')
        c = conn.cursor()
        print("Database connection established.")

        # Query the database
        print(f"Executing SQL query for IssueID: {IssueID}")
        c.execute("SELECT * FROM Issues WHERE IssueID=?", (IssueID,))
        issue_data = c.fetchone()
        print(f"Query result: {issue_data}")

        if not issue_data:
            print("Error: No data found for the given IssueID.")
            return jsonify({"error": "No issue found"}), 404

        # Example: Create a response dictionary from query result
        response = {
            "IssueID": IssueID,
            "Data": {
                "Column1": issue_data[0],
                "Column2": issue_data[1],
                # Add other columns as needed
            }
        }

        print(f"Response prepared: {response}")

        # Close the database connection
        print("Closing database connection.")
        conn.close()

        return jsonify(response)

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500



#from sections
@app.route('/IssueCharacter', methods=['GET'])
def get_sections():
    connection = mysql.connector.connect(**creds)
    mycursor = connection.cursor()

    # check to see if a new section needs to be added
    new_section_info = (
        request.args.get('new_section_id'), 
        request.args.get('new_course_id'), 
        request.args.get('new_meeting_time'), 
        request.args.get('new_meeting_days'), 
        request.args.get('new_meeting_room')
    )
    
    if not None in (new_section_info):
        mycursor.execute("INSERT INTO section (id, course_id, meeting_time, meeting_days, meeting_room) values (%s, %s, %s, %s, %s)", new_section_info)
        connection.commit()

    # check to see if a section needs to be deleted
    delete_section_id = request.args.get('delete_section_id')
    if delete_section_id is not None:
        try:
            mycursor.execute("delete from section where id=%s",(delete_section_id,))
            connection.commit()
        except:
            return render_template("error.html", message="Error deleting section, perhaps there are students registered for it")

    # retrieve all sections
    mycursor.execute("SELECT section.id, course_name, course_code, meeting_time, meeting_days, meeting_room from section join course on course_id=course.id")
    allSections = mycursor.fetchall()
    pageTitle = "Showing all sections"
    mycursor.execute("SELECT id, course_name, course_code from course")
    allCourses = mycursor.fetchall()

    mycursor.close()
    connection.close()
    return render_template('IssueCharacter.html', sectionList=allSections, pageTitle=pageTitle, allCourses=allCourses)


#from section-info
@app.route('/IssueCharacter-update', methods=['GET'])
def get_section_info():
    section_id = request.args.get('section_id')
    
    # redirect to all students if no id was provided
    if section_id is None:
        return redirect(url_for("get_sections"))

    connection = mysql.connector.connect(**creds)
    mycursor = connection.cursor()

    # update section information if necessary
    section_info = (
        request.args.get('meeting_time'),
        request.args.get('meeting_days'),
        request.args.get('meeting_room'),
        section_id
    )
    if not None in section_info:
        mycursor.execute("UPDATE section set meeting_time=%s, meeting_days=%s, meeting_room=%s where id=%s", section_info)
        connection.commit()

    # check to see if a student needs to be dropped from course
    remove_student_id = request.args.get('remove_student_id')
    if remove_student_id is not None:
        mycursor.execute("DELETE from section_student where student_id=%s and section_id=%s", (remove_student_id, section_id))
        connection.commit()

    # retrive basic information for the section
    mycursor.execute("SELECT course_name, course_code, meeting_time, meeting_days, meeting_room from section join course on course_id=course.id where section.id=%s", (section_id,))
    try:
        course_name, course_code, meeting_time, meeting_days, meeting_room = mycursor.fetchall()[0]
    except:
        return render_template("error.html", message="Error retrieving section - does it exist?")
    
    # retrieve registration info
    mycursor.execute("""SELECT student_id, first_name, last_name from student 
                     join section_student on section_student.student_id=student.id 
                     join section on section_student.section_id=section.id 
                     where section.id=%s
                     order by last_name, first_name""", (section_id,)
                     )
    registeredStudents = mycursor.fetchall()


    mycursor.close()
    connection.close()
    return render_template("section-info.html",
                           section_id=section_id,
                           course_name=course_name,
                           course_code=course_code,
                           meeting_time=meeting_time,
                           meeting_days=meeting_days,
                           meeting_room=meeting_room,
                           registeredStudents=registeredStudents
                           )



if __name__ == '__main__':
    app.run(port=8000, debug=True, host="0.0.0.0")
