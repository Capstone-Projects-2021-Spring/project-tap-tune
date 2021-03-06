# Class defining a recording
# inherited by Rhythmrecording and MelodyRecording
# contains functions for handeling information about user recordings

from abc import ABC, abstractclassmethod

class Recording(ABC):

    """
    recor_length : Date - refers to the time (seconds) of the recording
    record_type: Integer - flag for what recording type (Melody or Rhythm)
    recordingID: Integer - unique ID for the recording
    userID: Integer - ID associated with the user who created recording
    time_start: Date - time recording was started
    time_stop: Date - time recording ended
    recordin: Determined by the data format, Melody or Rhythm
    """
    record_length = None
    record_type = None
    recordingID = None
    userID = None
    time_start = None
    time_stop = None
    recording = None

    """
    Constructor
    """
    def __innit__(self, recordType,  userID):
        self.record_type = recordType
        self.userID = userID

    """
    Abstract method for MelodyRecording and RhythmRecording to define separately
    """
    @abstractclassmethod
    def recordStart(cls, self):
        pass
    
    """
    Abstract method for MelodyRecording and RhythmRecording to define separately
    """
    @abstractclassmethod
    def recordStop(cls, self):
        pass

    """
    Abstract method for MelodyRecording and RhythmRecording to define separately
    """
    @abstractclassmethod
    def clearRecording(cls, self):
        pass



