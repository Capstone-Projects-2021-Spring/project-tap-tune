from models.Database import db, get_cursor
from models.Mail import mail
from flask_mail import Message
from passlib.context import CryptContext
from flask import session
import secrets

"""
User class models and contains information about a user.
Including their identifying information and their login information.
"""


class User:
    UNKNOWN_ERROR = 'generic error'

    # errors related to signup
    DUPLICATE_EMAIL_ERROR = 'duplicate email'
    DUPLICATE_USERNAME_ERROR = 'duplicate username'

    pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
    )

    def __init__(self, id, username, email, name):
        self.id = id
        self.username = username
        self.email = email
        self.name = name

    # encrypt password
    @staticmethod
    def __encrypt_password(password):
        return User.pwd_context.hash(password)

    """
    Used to create an instance of a new user and add them to the database. 
    This method saves the information in the database and 
    creates an instance of the User if the save is successful. 
    Returns an instance of the User class with the user’s info on success 
    or error code on failure.
    
    user = User.signup(...)
    if isinstance(user, User):
        //success
    else:
        //check for user error code 
        user == User.DUPLICATE_EMAIL_ERROR
    """
    @staticmethod
    def signup(username, email, name, password):
        try:
            # encrypt password
            enc_password = User.__encrypt_password(password)

            # insert user into database
            cursor = get_cursor()
            cursor.execute('INSERT INTO user (username,email,`name`,`password`) VALUES (%s,%s,%s,%s)',
                           (username, email, name, enc_password))
            db.connection.commit()
        except Exception as e:
            print(e)
            error = User.UNKNOWN_ERROR
            # mysql error code for duplicate entry
            if e.args[0] == 1062:
                if 'username' in e.args[1]:
                    error = User.DUPLICATE_USERNAME_ERROR
                elif 'email' in e.args[1]:
                    error = User.DUPLICATE_EMAIL_ERROR
            return error
        return User.login(username, password)

    """
    Used to check that the entered username and password matches the 
    user’s information in the database and log the user in. 
    Returns a User instance with the user’s info if successful, 
    return null on failure.
    """
    @staticmethod
    def login(username, password):
        user = None
        try:
            # get user info from database
            cursor = get_cursor()
            cursor.execute('SELECT * FROM user WHERE username = %s', (username, ))
            user_data = cursor.fetchone()

            # if user found verify password
            if user_data:
                if User.pwd_context.verify(password, user_data['password']):
                    user = User(user_data['id'], user_data['username'], user_data['email'], user_data['name'])
                    # add to session
                    session['user_id'] = user.id
                    session['username'] = user.username
                    session['email'] = user.email
                    session['name'] = user.name
        except Exception as e:
            print(e)

        return user

    """
    Used to logout a user. 
    Destroys any session info and logs user out. 
    Returns void.
    """
    @staticmethod
    def logout():
        # remove user from session
        session.pop('user_id', None)
        session.pop('username', None)
        session.pop('email', None)
        session.pop('name', None)

    """
    Used to send an email to the user with a link to reset their password. 
    This method creates a reset token and saves in the database, 
    it then sends an email to the specified email address with a link, 
    which can be used to reset the user’s password . 
    Returns true on success and false on email send failure.
    """
    @staticmethod
    def send_reset_password_email(email):
        # check if user is valid
        cursor = get_cursor()
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        data = cursor.fetchone()

        # user is valid
        if data:
            # generate reset token
            reset_token = User.__generate_reset_token()

            # add token to database
            if User.__set_reset_token(data['id'], reset_token):
                # send email if token added successfully
                html_body = '''
                        <p>
                            Hello, %s<br>
                            Follow the link below to reset your password.
                        </p>
                        <a href="taptune.live/reset-password?token=%s">Reset Password</a>''' % (data['name'], reset_token)
                msg = Message()
                msg.add_recipient(data['email'])
                msg.subject = "TapTune - Reset Password Link"
                msg.html = html_body
                mail.send(msg)
                print('sending email to %s' % email)
                return True
            return False

        return False

    """
    generate secure token that is url safe
    """
    @staticmethod
    def __generate_reset_token():
        return secrets.token_urlsafe(32)

    """
    add reset token to database
    """
    @staticmethod
    def __set_reset_token(user_id, reset_token):
        try:
            # insert user reset_token into database
            cursor = get_cursor()
            cursor.execute('UPDATE user set reset_token = %s WHERE id = %s',
                           (reset_token, user_id))
            db.connection.commit()

            if cursor.rowcount < 1:
                return False
        except Exception as e:
            print(e)
            return False

        return True

    """
    Used to check that the given reset_token is valid. 
    Checks the database to see if there is a matching reset_token found.
    """
    @staticmethod
    def is_valid_reset_token(reset_token):
        try:
            # check if reset_token in database
            cursor = get_cursor()
            cursor.execute('SELECT * FROM user WHERE reset_token = %s', (reset_token, ))
            data = cursor.fetchone()

            # if data found token is valid
            if data:
                return True
        except Exception as e:
            print(e)

        return False

    """
    Used to update a user’s password. 
    Takes the string password input and saves a hashed copy of it in the database. 
    This method also deletes the reset_token from the database. 
    Return true on success and false on failure.
    """
    @staticmethod
    def reset_password(password, reset_token):
        try:
            # encrypt password
            enc_password = User.__encrypt_password(password)

            # update database
            cursor = get_cursor()
            cursor.execute('UPDATE user SET reset_token = NULL, password = %s WHERE reset_token = %s'
                           , (enc_password, reset_token))
            db.connection.commit()
            if cursor.rowcount < 1:
                return False
        except Exception as e:
            print(e)
            return False

        return True

    """
    This method retrieves the user’s song history from the database, 
    initializes them into Song class and returns an array containing the search results. 
    Returns an array with the songs from the user’s song log. 
    The array can be empty.
    """
    def get_song_log(self):
        # TODO IMPLEMENT GET SONG LOG
        return []
