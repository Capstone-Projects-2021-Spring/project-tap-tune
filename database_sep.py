import mysql.connector

db = mysql.connector.connect(
  host="taptune.cqo4soz29he6.us-east-1.rds.amazonaws.com",
  user="ttapp",
  password="7tV9qEMc3!3Bp8M$zBSt9",
  database="taptune"
)

def get_cursor():
    return db.cursor()

