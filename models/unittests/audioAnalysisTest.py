import unittest
import flask_unittest
from flask import Flask
from models.Database import db, get_cursor
from models.Song import Song
from models.analysis.Filtering import Filtering
import models.analysis.AudioAnalysis as audioAnalysis
import librosa

song1 = {
    'title': 'Pumped Up Kicks',
    'artist': 'Foster The People',
    'genre': 'indie pop, indietronica, modern rock, pop, rock',
    'release_date': '2011-05-23',
    'preview': 'https://p.scdn.co/mp3-preview/db83e69f4ef8a49f5b77e367f7031cc3bcc41b1a?cid=57483e104132413189f41cd82836d8ef',
    'onset_hash': 'B*K*J*J*J*K*9*9*9*9*9*9*J*A*8*A*8*J*K*A*8*9*9*I*K*A*8*A*8*K*J*A*9*9*9*9*9*J*A*8*A*8*J*K*A*8*J*I*K*B*7*A*8*9*9*K*9*9*A*9*9*9*J*J*A*8*J*K*A*8*9*9*J*J*A*8*A*8*J*K*A*8*A*9*8*A*J*J*A*8*J*K*A*8*9*9*I*K*A*8*A*8*J*K*9*9*A*9*9*9*J*J*A*8*J*K*A*8*I*J*9*9*K*J*B*7*K*9*9*A*8*9*A*9*9*B*7*B*7*J*B*8*A*8*A*7*J*K*C*6*A*8*A*6*0*B*7*A*9*A*9*8*A*J*B*7*A*7*K*B*8*A*8*B*6*I*0*J*A*8*9*9*I*C*8*A*8*A*8*9*A*J*A*8*B*7*J*B*8*A*8*A*7*K*J*B*7*A*8*J*B*8*A*8*A*9*8*A*A*9*I*J*K*I*.40.*J*J*.39.*.40.*K*J*A*9*A*8*I*J*J*K*J*J*J*J*.39.*A*9*8*9*L*J*K*9*9*I*J*J*K*K*I*J*J*.39.*B*S*K*J*9*A*J*.38.*J*K*.39.*J*J*K*I*A*J*9*K*J*J*J*J*B*7*J*B*8*A*8*B*6*H*2*J*J*B*7*K*A*8*A*8*A*9*9*9*J*B*6*C*7*J*B*8*A*8*A*7*J*K*I*B*8*J*K*A*8*A*9*9*9*I*K*J*J*B*8*A*8*I*K*J*A*8*9*9*J*I*0*A*8*A*9*9*9*J*A*8*A*8*J*B*8*A*8*A*8*J*J*A*8*A*8*A*8*B*8*A*8*9*A*8*A*A*9*I*J*K*I*.40.*J*J*K*I*.40.*K*J*A*9*A*8*I*J*K*J*J*J*J*J*.39.*A*J*9*K*J*K*J*I*J*K*J*K*I*J*J*K*I*B*S*K*J*9*U*.38.*K*J*.39.*J*J*K*I*A*9*9*9*A*9*J*J*J*J*A*8*K*J*A*8*J*J*J*J*A*9*A*8*J*9*A*9*9*9*9*J*A*8*J*J*K*A*9*9*8*J*J*J*9*9*K*J*A*9*9*9*J*J*J*A*8*J*B*8*A*8*J*J*J*A*8*A*8*B*8*A*8*9*A*9*9*9*9*J*A*8*J*J*K*A*9*9*8*J*J*B*7*9*9*B*8*J*A*8*A*I*B*I*J*J*K*I*.41.*J*I*.39.*K*J*K*8*A*A*K*I*S*K*J*T*A*J*I*.39.*A*I*A*9*A*J*9*A*J*I*J*K*J*.39.*J*J*V*7*.40.*K*J*A*9*J*J*J*J*J*.39.*K*I*.39.*U*9*K*T*A*J*I*K*J*J*.39.*J*J*V*7*.40.*K*J*A*9*J*J*I*K*J*.39.*K*I*.39.*U*9*K*9*9*K*',
    'peak_hash': 'B*A*L*I*K*J*J*J*J*O*E*J*S*K*A*I*T*J*A*J*T*J*A*J*J*U*I*B*S*J*A*J*R*K*B*I*I*A*J*K*J*J*F*D*K*T*B*I*I*T*A*J*J*T*J*A*E*E*J*F*E*J*T*J*A*I*T*J*A*J*H*A*K*K*J*J*E*G*I*H*A*B*J*K*R*J*B*I*K*K*I*J*J*J*L*J*J*J*J*J*K*R*C*H*J*K*J*J*J*G*C*B*I*K*J*J*E*C*C*E*C*B*I*J*K*J*J*J*I*A*B*J*J*J*J*J*M*H*K*H*J*K*J*J*I*A*A*J*I*G*D*C*I*H*T*J*A*J*J*K*H*B*J*A*K*I*N*E*A*C*H*I*T*C*H*K*I*J*K*I*A*K*J*I*J*K*C*H*I*M*Q*A*J*K*K*G*B*J*K*A*I*S*A*M*H*F*C*C*J*J*I*I*J*K*I*A*J*J*B*J*J*J*J*K*J*J*J*J*J*J*J*J*J*H*B*B*J*D*E*B*I*J*I*H*B*C*H*J*M*H*J*J*I*A*J*A*K*J*J*K*J*G*A*A*J*K*J*J*J*J*L*I*J*K*J*J*J*K*F*B*A*J*J*L*I*J*I*B*J*I*F*F*L*I*H*M*J*H*L*H*K*I*A*J*A*K*I*N*E*A*C*I*H*T*C*I*J*I*J*K*I*A*K*J*I*B*H*A*C*I*H*M*Q*A*J*K*S*K*J*A*J*J*J*J*N*H*E*C*C*J*R*I*A*J*K*I*A*K*J*A*J*J*J*J*K*J*R*B*J*J*J*J*K*I*A*J*I*B*J*J*J*J*K*J*K*G*A*A*K*I*K*I*A*J*A*I*K*J*J*K*J*R*A*J*K*J*J*K*I*A*I*A*J*K*J*J*J*K*R*B*H*A*A*J*J*J*J*A*I*A*K*J*L*B*E*F*G*J*B*F*I*A*K*I*A*K*I*B*I*I*K*G*C*B*H*A*J*B*I*J*I*J*E*F*B*I*J*I*L*E*D*C*I*H*A*J*B*H*K*I*K*I*A*J*A*K*I*K*I*M*I*I*T*B*I*I*F*D*J*A*J*A*J*J*I*B*J*L*I*J*K*J*H*K*I*K*I*A*J*A*K*I*N*E*A*C*I*I*T*B*I*J*J*I*K*J*K*.55.*.63.*',
    'harm_hash': 'B*A*5*7*7*8*2*6*4*7*G*4*5*9*2*6*9*9*8*3*6*9*2*6*4*4*2*6*9*9*9*2*F*C*8*2*6*9*8*C*G*G*5*7*9*2*6*9*J*7*C*9*9*A*8*9*A*E*4*2*6*9*9*T*B*8*2*6*9*9*B*3*C*3*I*8*8*2*6*9*2*G*C*7*2*6*9*9*9*9*A*2*B*4*2*9*8*7*C*G*B*8*4*5*8*L*G*2*7*4*7*6*9*2*6*9*2*C*3*N*6*9*5*4*8*3*5*9*F*7*7*8*2*6*C*G*K*2*6*9*L*G*3*B*7*6*9*2*6*4*4*2*G*6*D*2*G*9*E*4*A*3*9*4*4*6*3*6*7*E*2*B*A*8*3*6*9*2*6*6*5*F*8*2*B*7*3*4*4*4*0*7*2*7*4*F*B*6*6*2*3*5*9*8*B*3*4*A*3*5*9*0*0*4*0*5*6*6*8*4*5*9*2*6*9*2*6*8*2*0*C*0*4*2*7*8*6*8*9*8*4*6*0*3*D*C*6*3*5*7*2*C*5*9*I*5*6*8*4*4*7*5*6*7*5*5*9*2*6*9*2*6*7*4*7*5*F*3*2*2*6*6*6*4*D*0*4*5*2*5*5*D*5*9*9*9*3*5*A*7*7*3*3*5*8*B*5*7*5*8*4*5*9*2*6*4*4*2*6*7*5*E*B*B*0*5*8*9*C*0*8*4*B*8*4*5*9*3*5*9*8*A*A*9*9*P*N*C*6*B*6*L*I*J*A*L*6*K*.40.*J*K*A*B*6*8*7*W*7*4*6*A*7*A*A*I*J*A*L*R*8*A*K*B*8*J*9*J*9*J*J*J*A*9*J*I*J*A*K*7*B*8*S*B*J*K*9*C*Z*K*C*6*B*S*B*6*C*6*C*7*A*8*T*9*A*9*B*8*4*E*A*8*3*6*8*3*6*8*3*F*A*9*2*6*9*A*C*B*2*4*6*B*0*5*8*3*5*9*2*7*4*3*9*D*0*4*9*9*9*9*A*5*6*2*7*6*B*7*3*4*4*6*7*4*5*6*2*2*6*9*2*6*C*7*7*A*6*5*0*6*5*0*3*5*K*7*D*2*8*5*3*5*9*C*6*A*7*9*5*4*9*A*6*6*6*8*A*9*2*6*9*2*6*6*0*3*7*8*7*E*6*9*3*4*6*6*7*4*6*0*5*6*5*0*4*9*9*9*9*9*B*8*4*4*9*9*6*6*0*4*8*A*9*2*6*9*3*5*5*6*F*A*9*4*4*9*9*9*2*0*4*6*2*4*5*9*9*9*9*J*A*9*J*K*8*J*D*5*4*6*D*5*8*I*J*A*L*6*L*.39.*K*9*9*A*B*6*G*W*D*5*B*6*6*E*0*G*C*6*V*J*8*9*9*K*9*A*J*9*J*9*A*8*J*J*B*8*J*I*J*3*6*J*0*7*J*V*8*K*9*J*C*7*S*9*9*D*5*B*S*I*C*6*K*9*9*A*8*9*9*A*9*K*J*N*6*8*9*E*E*A*9*2*6*9*8*0*A*H*M*7*8*9*D*6*B*7*9*2*5*7*5*5*0*J*9*J*9*9*A*C*F*A*9*2*6*J*C*7*7*N*8*7*8*D*0*5*K*8*9*9*9*D*G*J*3*6*8*9*E*5*8*A*9*2*6*9*9*C*7*7*O*5*9*9*K*J*9*2*5*7*3*7*0*9*9*9*A*8*3*5*J*E*5*8*A*9*3*5*D*5*C*0*5*8*N*6*8*8*D*6*K*9*2*6*9*9*J*A*9*C*6*K*8*J*C*6*C*H*9*V*6*4*Y*K*9*9*K*9*A*I*B*B*6*B*6*A*J*6*5*6*B*0*4*L*J*I*B*S*A*I*9*A*3*5*B*8*9*9*9*.40.*8*J*D*5*B*6*C*3*4*I*C*H*K*8*J*.40.*K*9*9*A*J*S*J*D*5*B*6*L*J*4*6*S*I*5*4*I*9*K*9*A*8*A*9*.40.*8*J*D*5*B*6*C*8*B*7*T*K*8*K*.39.*K*9*9*A*C*6*S*J*J*B*6*L*J*B*B*6*9*L*7*8*9*9*K*9*A*.65.*',
    'perc_hash': 'B*J*J*J*J*K*9*9*A*8*A*8*K*9*8*A*8*J*K*A*9*8*9*I*K*B*8*9*8*K*J*A*9*9*9*9*9*J*A*8*B*7*J*K*A*9*9*8*I*K*B*8*9*8*9*A*J*9*9*A*9*9*9*J*A*8*A*8*J*K*A*9*8*9*J*J*B*8*9*8*K*J*A*9*A*8*9*9*J*B*7*A*8*K*J*A*8*9*9*J*J*A*9*9*5*3*8*9*6*D*9*A*9*9*9*9*J*J*A*9*J*J*A*8*B*6*K*9*9*K*J*A*8*J*A*9*A*8*9*9*A*8*B*7*B*8*J*J*A*8*B*6*J*K*C*6*A*8*B*6*0*I*B*9*9*9*9*9*J*C*6*B*7*C*6*K*A*8*B*6*D*4*0*I*0*A*7*B*7*J*K*A*9*A*8*9*9*J*B*7*B*7*K*B*7*A*8*B*7*E*4*J*C*6*A*8*J*K*A*9*A*8*8*B*9*8*A*8*A*8*B*8*J*C*6*9*9*J*J*K*I*B*9*I*9*A*9*9*A*9*A*7*B*7*B*7*K*J*B*7*9*9*J*J*K*I*A*9*9*9*A*9*9*9*9*A*A*8*9*8*J*A*9*J*J*A*8*J*J*A*9*A*7*B*9*I*9*A*9*9*A*9*A*8*9*9*I*A*8*K*B*7*A*8*J*J*K*B*6*A*9*9*9*A*9*9*9*A*8*K*B*6*B*7*K*J*A*9*A*7*J*J*B*8*B*7*J*J*A*9*A*8*9*9*J*B*7*B*8*I*K*A*8*B*7*J*8*A*C*6*A*8*K*J*A*9*9*9*9*9*9*9*9*9*J*J*K*A*9*A*6*K*J*A*9*9*8*H*2*I*0*9*9*A*8*9*9*C*7*9*8*A*8*K*J*A*9*9*8*J*J*B*8*9*8*A*7*0*C*6*A*9*9*8*0*8*A*A*7*J*J*B*8*J*J*9*9*J*J*K*I*B*9*I*K*9*9*A*9*A*8*A*8*I*K*J*B*7*9*9*J*J*K*I*A*9*9*9*A*9*9*9*9*A*A*8*A*7*B*7*A*9*J*C*6*A*8*K*I*K*I*B*9*I*9*A*9*9*A*9*A*8*A*8*9*8*A*8*K*J*A*8*K*I*K*A*7*A*9*9*9*A*9*9*A*9*9*J*B*7*A*8*J*J*A*9*9*8*J*J*K*A*8*A*8*J*A*9*A*8*9*A*J*9*9*A*7*J*K*A*9*9*8*C*6*J*C*7*8*A*B*7*J*A*9*9*9*9*A*J*9*9*9*9*J*K*9*9*9*8*J*J*A*9*9*9*A*8*J*A*9*A*8*9*A*I*A*9*9*8*J*L*9*9*9*8*J*J*B*8*8*A*A*8*J*A*9*9*9*9*A*A*7*B*7*J*C*7*D*5*J*9*A*J*I*K*9*8*B*9*A*7*K*8*B*9*L*7*A*8*I*K*D*5*J*9*A*J*I*L*H*A*J*A*9*9*B*7*A*9*A*8*I*B*8*J*J*C*6*A*9*J*I*L*9*7*B*9*I*9*A*9*A*9*9*B*7*A*8*J*J*J*J*A*9*J*I*L*H*B*8*9*9*B*8*9*A*8*A*A*8*I*K*J*J*C*6*A*9*I*J*L*9*7*B*9*I*9*A*9*A*9*9*B*7*A*8*J*J*J*J*A*9*J*I*L*H*A*9*9*9*B*8*9*A*9*9*'
}

timestamp = [0.325,0.944,1.555,2.219,2.887,3.521,4.181,4.815,5.485,6.117,6.795,7.495,8.123,8.781,9.473,10.131,10.771,11.059,11.367,11.753,12.025,12.385,12.671,13.049,13.417,13.599,13.779,13.953,14.127,14.303,14.481,14.665,14.851,15.029,15.227,15.411,15.589,15.773,15.959,16.149,16.327,16.527,16.693,16.861,17.055,17.223,17.405,17.603,17.797,19.379,20.067,20.263,20.663,20.923,21.457,21.635,21.833,22.215,22.619,23.225,23.419,23.839,24.251,24.641,24.855,25.041,25.469,25.899,26.499,26.713,27.093,27.496,27.917,28.105,28.299,28.707,29.147,29.788,29.994,30.367,31.149,31.331,31.533,31.981,32.409,32.995,33.185,33.633]
input = [0.613,1.09,1.296,1.572,2.054,2.277,2.572,3.068,3.532]

class UserTestCase(unittest.TestCase):

    def test_change_tempo(self):
        #test with invalid k value
        synced = audioAnalysis.change_tempo(input,0)
        self.assertEqual(synced,[])
        synced = audioAnalysis.change_tempo(input,-2)
        self.assertEqual(synced,[])
        #test with normal value
        synced = audioAnalysis.change_tempo(input,60)
        self.assertIsInstance(synced,list)

    def test_get_tempo(self):
        #test with normal input
        tempo = audioAnalysis.get_tempo(input)
        self.assertIsInstance(tempo,list)
        tempo = audioAnalysis.get_tempo([1,2,3,4,5,6,7,8,9])
        self.assertEqual(tempo,60)
        tempo = audioAnalysis.get_tempo([2,4,6,8,10,12,14,16,18,20])
        self.assertEqual(tempo,30)
        #teset with invalid input
        tempo = audioAnalysis.get_tempo(0)
        self.assertEqual(tempo,0)
        tempo = audioAnalysis.get_tempo('abc')
        self.assertEqual(tempo,0)
        tempo = audioAnalysis.get_tempo({1,2,3})
        self.assertEqual(tempo,0)

    def test_get_pettern(self):
        #normal input
        pattern = audioAnalysis.get_pattern(input)
        self.assertIsInstance(pattern,list)
        #invalid input
        pattern = audioAnalysis.get_pattern([0])
        self.assertEqual(pattern,[])
        pattern = audioAnalysis.get_pattern([-1])
        self.assertEqual(pattern, [])
        pattern = audioAnalysis.get_pattern(115)
        self.assertEqual(pattern, [])
        pattern = audioAnalysis.get_pattern('abcd')
        self.assertEqual(pattern, [])
        #skip pattern that is smaller than 0
        pattern = audioAnalysis.get_pattern([1,2,1,3,4,5])
        self.assertEqual(pattern, [1,2,1,1])

    def test_hashing(self):
        #convert an timestamp list to hash, unhash it and compare to original
        frame = librosa.time_to_frames(input)
        bin = audioAnalysis.frames_to_bin(frame)
        hash = audioAnalysis.hash_array(bin)
        unhash = librosa.frames_to_time(audioAnalysis.bin_to_frame(audioAnalysis.unhash_array(hash)))
        self.assertEqual(len(unhash),len(input))
        error = abs(sum(unhash-input))/len(unhash)
        self.assertTrue(self, error<0.05)
if __name__ == '__main__':
    unittest.main()

    #print(audioAnalysis.change_tempo([],-60))
    # print(audioAnalysis.get_pattern([1,2,1,3,4,5]))

    # print( audioAnalysis.unhash_array('A*S*D*V*4*2*A*L*'))
    # frame = librosa.time_to_frames(input)
    # bin = audioAnalysis.frames_to_bin(frame)
    # hash = audioAnalysis.hash_array(bin)
    # unhash = librosa.frames_to_time(audioAnalysis.bin_to_frame(audioAnalysis.unhash_array(hash)))
    # print(unhash)
    # print(input)
    # print(sum(unhash-input)/len(unhash))