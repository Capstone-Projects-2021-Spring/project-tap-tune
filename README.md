# Project Software Release
  
 ## New Features Implemented
 - Improved Rhythm Recording/Results UI (Matched Song Pattern Playback, Spotify Embed web player, new custom visualizer)
 - Spotfy Song Suggestion with Attributes
 - Autosourcing Audio Files, uses the song suggestion feature to obtain correct song titles and rtists from Spotify, fetches and verifies YouTube videos for audio streams
 - Database search feeature

## Known Bugs
- Occasional timeout with Genius Lyrics requests
- Rhythm Results User Pattern Playback and Song Pattern Playback can overlap if clicked in succession
- Melody Recording service occasionally throws error prevnting use of service, resolved with time
- Song Suggestion component issues a bad request if refresh button is clicked without any trcks marked to be seeds

## Build and Install instructions
- Source Code can be compiled and run using Python 3.8
- ffprobe should be installed on machine to use the crowd sourcing and autosourcing feature
- The live server site taptune.live is updated with the latest release
- Mobile installations can be done by saving the application to a devices homescren (setting to do so can be found in the browser settings) 
 

## Contributors
Peter Ramirez, Aley Chaing, Xufeng Ren, Rishir Patel, Daniel Lee, Wayne Cook
