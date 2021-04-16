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
    DUPLICATE_FINGERPRINT_ERROR = 'song already has associated fingerprint'

    BASE_SELECT_QUERY = 'SELECT song.*,fp.perc_hash,fp.harm_hash FROM song LEFT JOIN fingerprint AS fp ON song.`id` = fp.song_id'

    def __init__(self, song_id, title, artist, release_date, genre, onset_hash, peak_hash, perc_hash, harm_hash, preview=None, favorited_on=None):
        self.id = song_id
        self.title = title
        self.artist = artist
        self.release_date = release_date
        self.genre = genre
        self.onset_hash = onset_hash
        self.peak_hash = peak_hash
        self.perc_hash = perc_hash
        self.harm_hash = harm_hash
        self.preview = preview
        self.favorited_on = favorited_on

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
        perc_hash = attr_d.get('perc_hash')
        harm_hash = attr_d.get('harm_hash')

        return Song(attr_d['id'], attr_d['title'], attr_d['artist'], release_date, genre
                    , onset_hash, peak_hash, perc_hash, harm_hash, attr_d.get('preview'), attr_d.get('favorited_on'))

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
                'INSERT INTO song (title,artist,genre,release_date,preview,onset_hash,peak_hash) VALUES (%s,%s,%s,%s,%s,%s,%s)'
                , (attr_d.get('title'), attr_d.get('artist'), genre, attr_d.get('release_date'), attr_d.get('preview')
                   , attr_d.get('onset_hash'), attr_d.get('peak_hash')))
            db.connection.commit()

            # get/set inserted id
            attr_d['id'] = cursor.lastrowid

            # insert fingerprint row
            cursor.execute(
                'INSERT INTO fingerprint (song_id,perc_hash,harm_hash) VALUES (%s,%s,%s)'
                , (attr_d['id'], attr_d.get('perc_hash'), attr_d.get('harm_hash')))
            db.connection.commit()

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
                elif 'song_id' in e.args[1]:
                    error = Song.DUPLICATE_FINGERPRINT_ERROR
            return error

    """
    gets all songs from the database
    returns None on failure
    returns array of songs on success 
    """
    @staticmethod
    def get_all():
        # get songs from database
        return Song.__get_songs(Song.BASE_SELECT_QUERY, [])

    """
    get all songs by id
    input array of songs ids
    returns None on failure
    returns array of songs on success (array can be empty)
    """
    @staticmethod
    def get_by_ids(ids: list):
        # create query
        query = Song.BASE_SELECT_QUERY + ' WHERE song.`id` IN '
        placeholder = []
        for id in ids:
            placeholder.append('%s')
        query += '(' + ','.join(placeholder) + ')'

        # get songs from database
        return Song.__get_songs(query, ids)

    """
    get all songs by genre 
    returns None on failure
    returns array of songs on success (array can be empty)
    """
    @staticmethod
    def get_by_genre(genre):
        # format genre for like query
        genre_f = '%' + genre + '%'

        # setup query
        query = Song.BASE_SELECT_QUERY + ' WHERE song.genre LIKE %s'

        # get songs from database
        return Song.__get_songs(query, [genre_f])

    """
    get all songs by artist
    returns None on failure
    returns array of songs on success (array can be empty)
    """
    @staticmethod
    def get_by_artist(artist):
        # format genre for like query
        artist_f = '%' + artist + '%'

        # setup query
        query = Song.BASE_SELECT_QUERY + ' WHERE song.artist SOUNDS LIKE %s'

        # get songs from database
        return Song.__get_songs(query, [artist_f])

    """
    private method
    used to get songs from database
    returns array of songs on success (array can be empty)
    returns None on failure
    """
    @staticmethod
    def __get_songs(query, data: list):
        try:
            songs = []

            # get songs from database
            cursor = get_cursor()
            cursor.execute(query, data)
            song_rows = cursor.fetchall()

            # create song classes and append to songs array
            for song_r in song_rows:
                #print(song_r)
                songs.append(Song.create(song_r))

        except Exception as e:
            print(e)
            print(query)
            return None

        return songs

    """
    check if song is favorite
    return Boolean
    """
    def is_favorite(self):
        return self.favorited_on is not None

    """
    set preview for song
    return false on failure, true on success
    """
    def set_preview(self, preview):
        return self.__update_song_val('preview', preview)

    """
    set onset hash for song
    return false on failure, true on success
    """
    def set_onset_hash(self, hash):
        return self.__update_song_val('onset_hash', hash)

    """
    set peak hash for song
    return false on failure, true on success
    """
    def set_peak_hash(self, hash):
        return self.__update_song_val('peak_hash', hash)

    """
    set percussion hash for song
    return false on failure, true on success
    """
    def set_perc_hash(self, hash):
        return self.__update_song_val('perc_hash', hash)

    """
    set harmonic hash for song
    return false on failure, true on success
    """
    def set_harm_hash(self, hash):
        return self.__update_song_val('harm_hash', hash)

    """
    private method
    used to update single song attribute value in database
    """
    def __update_song_val(self, col, val):
        # set fingerprint attributes
        fp_attr = ['perc_hash', 'harm_hash']

        if col in fp_attr:
            table = 'fingerprint'
            rel_id = 'song_id'
        else:
            table = 'song'
            rel_id = 'id'

        try:
            # set query
            query = 'UPDATE %s set %s' % (table, col)
            query += ' = %s WHERE ' + rel_id + ' = %s'

            # update song hash
            cursor = get_cursor()
            cursor.execute(query, (val, self.id))
            db.connection.commit()

            if cursor.rowcount < 1:
                print('update failed')
                return False

            # set the attribute to provided value
            setattr(self, col, val)

        except Exception as e:
            print(e)
            return False
        return True
