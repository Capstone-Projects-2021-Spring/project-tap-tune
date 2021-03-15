# CLASS DESCRIPTION

"""
1. accept the user input rhythm recording
2. fetch DB information onset_frames <hashed string>, peak_frames<hashed string>, sr <int>
3. compare the user iput with information from database
4. append the songs labeled as matches to a list of results
    results = [
                {
                    title: *title,
                    artist: *artis,
                    genres: *genres
                }
            ]

    results.append( {"title" : *title, "artist", *artist, "genres":*genre} )
5. Return the song results to use in the Filtering
"""