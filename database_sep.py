import mysql.connector

mydb = mysql.connector.connect(
  host="taptune.cqo4soz29he6.us-east-1.rds.amazonaws.com",
  user="ttapp",
  password="7tV9qEMc3!3Bp8M$zBSt9"
)

def get_cursor():
    return mydb.cursor()

