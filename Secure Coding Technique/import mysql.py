import mysql.connector, json

with open('/home/googlabill/ComDatabase/Secure Coding Technique/secrets.json', 'r') as secretFile:
    creds = json.load(secretFile)['mysqlCredentials']


connection = mysql.connector.connect(**creds)

mycursor = connection.cursor()
mycursor.execute("select * from actor")
myresult = mycursor.fetchall()

print(f"{myresult=}")

print("In the actor table, we have the following items:")
for row in myresult:
    print(row)

mycursor.close()
connection.close()