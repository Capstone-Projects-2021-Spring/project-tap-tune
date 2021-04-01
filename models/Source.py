"""
- accept user file [front end -> backend] OR accept YouTube URL

*if youtube URL we need to convert from .mp4 to .wav

- accept user input song title and song artist
- search spotify for song metadata (genre, release_date, etc.)
- present and prompt user to check information [back end-> front end]
- record user verification (yes/no) [front end -> back end]
- process song file, produce hashes
- upload song metadata and hashes into DB
- return confirmation of uploading to user [back end -> front end]
"""

from pytube import YouTube

yt = YouTube("https://www.youtube.com/watch?v=96D-C_MIV_U")
streams = yt.streams.filter(only_audio=True)

for stream in streams:
    if stream.mime_type == "audio/mp4":
        print(stream)
        stream.download()
        break

class Source:
    # constructor for the source class
    # @param url - youtube url if provided by the user
    # @param file - .wav file uploaded by user
    def __innit__(self, url=None, file=None):
        self.url = url
        self.file = file

    # function to fetch audio stream from youtube
    # returns audio stream, can be saved from call
    def fetch_youtube_audio(self):
        try:
            yt = YouTube(self.url)
            streams = yt.streams.filter(only_audio=True)

            for stream in streams:
                if stream.mime_type == "audio/mp4":
                    return stream
                    break

        except Exception as e:
            print("FAILED YOUTUBE STREAM FETCH")
            return None

