from models.Database import db, get_cursor
# from database_sep import db, get_cursor

"""
Song class models and contains information about a song.
"""


class Song:
    UNKNOWN_ERROR = 'generic error'

    # errors related to insert
    SONG_TITLE_REQUIRED = 'song title not specified'
    SONG_ARTIST_REQUIRED = 'song artist not specified'
    DUPLICATE_SONG_ERROR = 'duplicate title and artist'

    def __init__(self, song_id, title, artist, release_date, genre, onset_hash, peak_hash, harmonic_hash, percussive_hash, preview=None):
        self.id = song_id
        self.title = title
        self.artist = artist
        self.release_date = release_date
        self.genre = genre
        self.onset_hash = onset_hash
        self.peak_hash = peak_hash
        self.percussive_hash = percussive_hash
        self.harmonic_hash = harmonic_hash
        self.preview = preview


    def set_preview(self, preview):
        self.preview = preview

    """
    used to create an instance of the song class from an associative array of attributes
    """
    @staticmethod
    def create(attr_d: dict):
        # set non required values to null if not provided
        genre = attr_d.get('genre') if attr_d.get('genre') else attr_d.get('genres')
        release_date = attr_d.get('release_date')
        onset_hash = attr_d.get('onset_hash')
        peak_hash = attr_d.get('peak_hash')

        return Song(attr_d['id'], attr_d['title'], attr_d['artist'], release_date, genre
                    , onset_hash, peak_hash)

    """
    insert song into database
    Parameters
        attr_d a dictionary with song attributes
            required: title, artist
            optional: genre, release_date, onset_hash, peak_hash
    return error on failure, Song instance on success
    """
    @staticmethod
    def insert(attr_d: dict):
        try:
            genre = attr_d.get('genre') if attr_d.get('genre') else attr_d.get('genres')

            # insert song into db
            cursor = get_cursor()
            cursor.execute(
                'INSERT INTO song (title,artist,genre,release_date,onset_hash,peak_hash) VALUES (%s,%s,%s,%s,%s,%s)'
                , (attr_d.get('title'), attr_d.get('artist'), genre, attr_d.get('release_date')
                   , attr_d.get('onset_hash'), attr_d.get('peak_hash')))
            db.connection.commit()

            # get/set inserted id
            attr_d['id'] = cursor.lastrowid

            return Song.create(attr_d)
        except KeyError as e:
            print(e)
            error = 'Missing required value'
            return error
        except Exception as e:
            print(e)
            error = Song.UNKNOWN_ERROR

            # mysql error code for null entry into non null (required) field
            if e.args[0] == 1048:
                if 'title' in e.args[1]:
                    error = Song.SONG_TITLE_REQUIRED
                elif 'artist' in e.args[1]:
                    error = Song.SONG_ARTIST_REQUIRED
            # mysql error code for duplicate entry
            elif e.args[0] == 1062:
                if 'title' in e.args[1]:
                    error = Song.DUPLICATE_SONG_ERROR
            return error

    """
    gets all songs from the database
    returns None on failure
    returns array of songs on success 
    """
    @staticmethod
    def get_all():
        try:
            songs = []

            # get songs from database
            cursor = get_cursor()
            cursor.execute('SELECT * FROM song', ())
            song_rows = cursor.fetchall()

            # create song classes and append to songs array
            for song_r in song_rows:
                print(song_r)
                songs.append(Song.create(song_r))

        except Exception as e:
            print(e)
            return None

        return songs

    """
    get all songs by genre 
    returns None on failure
    returns array of songs on success (array can be empty)
    """
    @staticmethod
    def get_by_genre(genre):
        # format genre for like query
        genre_f = '%' + genre + '%'

        try:
            songs = []

            # get songs from database
            cursor = get_cursor()
            cursor.execute('SELECT * FROM song WHERE genre LIKE %s', (genre_f,))
            song_rows = cursor.fetchall()

            # create song classes and append to songs array
            for song_r in song_rows:
                print(song_r)
                songs.append(Song.create(song_r))

        except Exception as e:
            print(e)
            return None

        return songs

    """
    get all songs by artist
    returns None on failure
    returns array of songs on success (array can be empty)
    """
    @staticmethod
    def get_by_artist(artist):
        # format genre for like query
        artist_f = '%' + artist + '%'
        try:
            songs = []

            # get songs from database
            cursor = get_cursor()
            cursor.execute('SELECT * FROM song WHERE artist LIKE %s', (artist_f,))
            song_rows = cursor.fetchall()
            # create song classes and append to songs array
            for song_r in song_rows:
                print(song_r)
                songs.append(Song.create(song_r))

        except Exception as e:
            print(e)
            return None

        return songs

    """
    set onset hash for song
    return false on failure, true on success
    """
    def set_onset_hash(self, hashs):
        try:
            # update song hash
            cursor = get_cursor()
            cursor.execute('UPDATE song set onset_hash = %s WHERE id = %s', (hashs, self.id))
            db.connection.commit()

            if cursor.rowcount < 1:
                print('update failed')
                return False

        except Exception as e:
            print(e)
            return False
        return True

    """
    set peak hash for song
    return false on failure, true on success
    """
    def set_peak_hash(self, hashs):
        try:
            # update song hash
            cursor = get_cursor()
            cursor.execute('UPDATE song set peak_hash = %s WHERE id = %s', (hashs, self.id))
            db.connection.commit()

            if cursor.rowcount < 1:
                print('update failed')
                return False

        except Exception as e:
            print(e)
            return False
        return True
