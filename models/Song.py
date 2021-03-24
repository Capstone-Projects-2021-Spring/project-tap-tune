from models.Database import db, get_cursor

"""
Song class models and contains information about a song.
"""
class Song:

    def __init__(self, id, title, artist, release_date, genre, onset_hash, peak_hash):
        self.id = id
        self.title = title
        self.artist = artist
        self.release_date = release_date
        self.genre = genre
        self.onset_hash = onset_hash
        self.peak_hash = peak_hash

    """
    used to create an instance of the song class from an associative array of attributes
    """
    @staticmethod
    def create(attr_a):
        return Song(attr_a['id'], attr_a['title'], attr_a['artist'], attr_a['release_date'], attr_a['genre']
                    , attr_a['onset_hash'], attr_a['peak_hash'])

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
    """
    @staticmethod
    def get_by_genre(genre):
        # format genre for like query
        genre_f = '%' + genre + '%'

        try:
            songs = []

            # get songs from database
            cursor = get_cursor()
            cursor.execute('SELECT * FROM song WHERE genre LIKE %s', (genre_f, ))
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
