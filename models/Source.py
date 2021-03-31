"""
- accept user file [front end -> backend] OR accept YouTube URL
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
