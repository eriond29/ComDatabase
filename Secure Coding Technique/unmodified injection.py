#!/usr/bin/python3

from flask import Flask, render_template, request
import mysql.connector, os


app = Flask(__name__)


@app.route('/', methods=['GET'])
def showTable():
    """This is vulnerable to the following SQL injection:
    http://localhost:8000/?id=1' or 1=1 --%20"""
    connection = mysql.connector.connect(
        host=os.environ['localhost'],
        user=os.environ['stephen'],
        password=os.environ['database'],
        db=os.environ['sakila']
    )
    mycursor = connection.cursor()

    id = request.args.get('id')

    # Fetch the value from the table with a matching ID
    sqlstring = "Select * from actor where actor_id='{}'".format(id)
    print(sqlstring)
    mycursor.execute(sqlstring)
    myresult = mycursor.fetchall()
    mycursor.close()
    connection.close()
    output = "<br />\n".join([str(row) for row in myresult])
    return output


if __name__ == '__main__':
    app.run(port=8000, debug=True, host="0.0.0.0")