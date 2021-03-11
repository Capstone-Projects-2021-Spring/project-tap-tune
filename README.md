# This branch is use for beat matching algorithm development and testing.
#  Do NOT merge this branch to main
-
-
-
-
-
-

# Project overview
  
 ## Tap Tune
  Tap Tune is a website/application that will allow users to tap a beat or rhythm. The user can specify with advanced filtering options to narrow down their results or can be recommended similar songs based on their taps. The service will be catered towards those who want to know the song of a tune or beat they happen to remember.
  
### Methodology
  Tap Tune will utilize the Librosa Python library. With it, we will be able to apply beat tracking, tempo estimation, and onset detection analysis to recordings and songs. The beat of a song represents a repeating occurring pattern of a song, the tempo is the speed of a beat, and onset detection finds the beginning of a musical note. These provide timing cues which can be used to find recurrence and self-similarity within the provided audio.  
  
librosa: https://github.com/librosa/librosa#librosa


  
  Tap Tune will also be using PyDejavu, an audio fingerprinting library in python that samples a sound file multiple times in order to find amplitudes. To find distinctive amplitudes that can be used to identify the song, PyDejavu compares the sample amplitude to its neighbors to find the peak. Taking the hash of the sum of peak frequency and delta time between peaks, a unique fingerprint is made for the song. The more identified peaks in a song creates a more distinctive audio fingerprint
  
Dejavu: https://github.com/worldveil/dejavu



### Deliverables
Users will be able to create an account. In it, they will be able to save song history and connect to other music services (Spotify or SoundCloud),

Users can submit audio files that can be matched with to find the song. The user can hum a song into their mic as well and use that.

Users can add filters along with the user submission to specify results. Filtering options will include genre, artist, instrument, or lyrics

On PC, wsers will need to use the keyboard to tap or will need to click on the button to the beat or melody of a song.

For Android or IOS, users will be able to download the app and use the functions.


# Contributors
Peter Ramirez, Aley Chaing, Xufeng Ren, Rishir Patel, Daniel Lee, Wayne Cook
