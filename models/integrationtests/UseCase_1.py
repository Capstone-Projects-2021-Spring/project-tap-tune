"""
Use Case #1:
Accesses Tap Tune website
Uses Tap (keyboard) function to record rhythm
Uses the Artist filter in his search
Gets a song suggestion

def test_usecase1(self):
    Set timestamp array for input
        [user_result = *timestamp array*]
    Use artist filter get result
        [filterResults = objF = Filtering(Artist=*some artist)]
    Send timestamp array and filter result to analysis
        objR = rhythmAnalysis(userTaps=user_result, filterResults=filterResults)
    Get song suggestion with analysis results as track seeds
        parse objR for song title and artist
        Search Spotify of song ids
        Use spotify suggest request and get result
"""