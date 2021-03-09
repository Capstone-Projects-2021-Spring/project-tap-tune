from flask_mysqldb import MySQL
import MySQLdb.cursors

db = MySQL()


def get_cursor():
    return db.connection.cursor(MySQLdb.cursors.DictCursor)
