import unittest
import lyricsgenius
from acrcloud.recognizer import ACRCloudRecognizer
import requests
import os
import warnings
import FingerprintRequest


class UserTestCase(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ResourceWarning)
        self.fingerprintObj = FingerprintRequest.FingerprintRequest()

        # Need a customary File for this, maybe 2
        dirname = os.path.dirname(__file__)
        self.singingfile = os.path.join(dirname, '..\\..\\sampleMusic\\september.wav')
        self.file = os.path.join(dirname, '..\\..\\sampleMusic\\SpinningMonkeys.wav')


    def test_ACRCloud(self):
        # Expected Result
        songArtist = 'Kevin MacLeod'
        songTitle = 'Monkeys Spinning Monkeys'

        # Perform Method
        songResult = self.fingerprintObj.getACRSongFingerprint(self.file)

        #Checks
        self.assertEqual(songResult.title, songTitle)
        self.assertEqual(songResult.artists, songArtist)

    def test_AudD(self):
        # Expected Result
        songArtist = 'Kevin MacLeod'
        songTitle = 'Monkeys Spinning Monkeys'

        #Perform Method
        songResult = self.fingerprintObj.getAudDFingerprint(self.file)

        #Checks
        self.assertEqual(songResult.title, songTitle)
        self.assertEqual(songResult.artists, songArtist)

    def test_AudD_Humming(self):
        # Expected Result
        result = list

        #Perform Method
        songResult = self.fingerprintObj.getHummingFingerprint(self.singingfile)

        #Checks
        self.assertIsNotNone(songResult)

    def test_Extracting_Song_From_Lyrics(self):
        # Set Up
        UserSungLyrics = 'Do you remember the 21st night of september'

        # Expected Result
        result = list

        # Perform Method
        songResult = self.fingerprintObj.getSongFromLyrics(UserSungLyrics)

        #Checks
        self.assertIsNotNone(songResult)

    def test_Lyric_Comparison(self):
        # Set Up
        UserSungLyrics = 'Do you remember the 21st night of september'

        song1 = FingerprintRequest.foundsong()
        song1.set_title("Don't Stop Me Now"), song1.set_artist("Queen")
        song2= FingerprintRequest.foundsong()
        song2.set_title("September"), song2.set_artist("Earth Wind & Fire")

        songArray = [song1, song2]
        leniency = 0.6

        # Expected Result
        songArtist = 'Earth Wind & Fire'
        songTitle = 'September'

        # Perform Method
        songResult = self.fingerprintObj.lyricSearch(songArray, UserSungLyrics, leniency)

        # Checks
        self.assertEqual(songResult.title, songTitle)
        self.assertEqual(songResult.artists, songArtist)

    def test_Everything_Together(self):
        # Set Up
        UserSungLyrics = 'Do you remember the 21st night of september'

        # Result for Actual Music File
        musicSongArtist = 'Kevin MacLeod'
        musicSongTitle = 'Monkeys Spinning Monkeys'

        # Result for Humming/Singing File
        singSongArtist = 'EARTH，WIND&FIRE'
        singSongTitle = 'SEPTEMBER'

        # Perform Methods
        musicResult = self.fingerprintObj.searchFingerprintAll(self.file, UserSungLyrics)
        humResult = self.fingerprintObj.searchFingerprintAll(self.singingfile, UserSungLyrics)

        # Perform Checks
        self.assertEqual(musicResult.title, musicSongTitle)
        self.assertEqual(musicResult.artists, musicSongArtist)

        self.assertEqual(humResult.title, singSongTitle)
        self.assertEqual(humResult.artists, singSongArtist)



if __name__ == '__main__':
    unittest.main()