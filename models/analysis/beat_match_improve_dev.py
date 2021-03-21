import librosa
import AudioAnalysis
import beat_match


# Purpose: intergrate the process of hash value to timestamp in one function
# Status: In-Progess, bug spotted: converting onset hash value to timestamp looks different than getting timestamp from librosa.onset.onset_detection
def bin_to_frame(bin_array):
    res_frames = []
    track = 0
    offset = 0
    check = 0

    for bin in bin_array:
        if (bin == 0) and (check != len(bin_array) - 1):
            track += 1

        elif (bin == 1):
            res_frames.append(track + offset)
            offset += 1

        else:
            res_frames.append(track + offset + 1)
            offset += 1
        check += 1
    return res_frames


# Sepertaed from old process_timestamp2()
# Purpose: process timestamp and get pattern by getting time differences between each beat
# Status: clear
def process_timestamp_diff(timestamp):
    beat_diff = []
    for i in range(len(timestamp) - 1):
        temp = timestamp[i + 1] - timestamp[i]
        beat_diff.append(temp)
    return beat_diff


# Seperated from old process_timestamp2()
# Purpose: analyze timestamp by deviding each timestamp by avg beat_diff, beat_diff: time difference between one beat to next one
# Status: In-progess
def process_timestamp_ratio(timestamp):
    beat_diff_over_avg = []
    diff = 0
    for i in range(len(timestamp) - 1):
        temp = timestamp[i + 1] - timestamp[i]
        diff += temp
    avg_diff = diff / len(timestamp)
    for i in range(len(timestamp)):
        beat_diff_over_avg.append(timestamp[i] / avg_diff)
    return beat_diff_over_avg


# Purpose: Compare two ratio pattern
# Principle: if user_pattern[i] / song_pattern[i] is very close t 1, it is a match beat
# Status: In progess, error range need more testing to determine
# Note: round both item to same decimal precision to compare?
def compare_ratio(user_pattern, song_pattern):
    mark = len(user_pattern) * 0.7
    numOfHit = 0
    error = 0.2  # Working process
    for i in range(len(song_pattern) - len(user_pattern)):
        numOfHit = 0
        temp = i
        for j in range(len(user_pattern)):
            if user_pattern[j] / song_pattern[i] >= 0.8:
                numOfHit += 1
                i += 1
            else:
                i = temp + 1
                break

        if numOfHit >= mark:
            return 1
    if numOfHit >= mark:
        return 1
    else:
        return 0;


# Purpose: Split a song into three section as a list. Iterate through the list for compare, provide early exit if song match in the first half.
#   sectin one: first half
#   Section two: Second half
#   Section three(enhanced section): from middle of first half to middle of second half, last section to run, make sure no part is missed
# Status: In progress.
# Note: - For unmatched song, running section three for compare actually will cost more time
#       - Another approach to split the song?
def split_song(song_pattern):
    len = len(song_pattern)
    pattern_set = []
    pattern_set.append(song_pattern[0:(len / 2)])
    pattern_set.append(song_pattern[(len / 2):-1])
    pattern_set.append(song_pattern[(len / 4):(len * 3 / 4)])
    return pattern_set


# ------------------------------------------------TESTING AREA----------------------------------------------------------
back_in_black_onset_hash = 'I*.60.*0*R*S*T*R*T*R*S*Q*S*E*E*Q*D*E*D*D*S*7*6*7*5*R*E*C*E*D*E*C*E*E*D*C*8*B*8*B*9*B*6*D*Q*D*E*R*D*E*R*S*7*6*7*5*R*E*D*E*E*R*D*E*E*C*L*K*J*K*M*4*S*D*5*6*F*D*D*7*5*D*E*6*6*D*M*5*E*C*E*E*D*7*5*E*D*D*C*L*K*7*C*5*D*R*E*D*E*C*E*D*D*6*6*D*E*D*E*E*C*D*D*F*Q*D*F*C*E*C*K*K*J*D*6*Q*Q*.81.*Q*Q*.55.*P*Q*R*R*Q*P*R*.80.*.54.*.52.*Q*.67.*D*Q*.78.*Q*L*5*E*D*Q*D*E*D*6*5*R*E*D*R*Q*0*E*C*J*5*0*E*D*D*6*4*M*K*K*J*L*5*R*E*6*5*D*E*D*5*6*C*E*E*D*C*E*K*7*D*E*D*C*M*6*D*D*6*C*K*7*B*E*6*P*R*.81.*Q*R*Q*R*Q*R*.54.*Q*P*.54.*.80.*Q*Q*P*Q*Q*Q*Q*Q*J*.87.*R*R*R*D*D*R*E*B*E*C*Q*R*R*D*C*S*Q*D*.95.*R*R*D*C*R*E*D*D*C*D*C*R*S*D*C*E*.40.*D*D*.80.*E*C*R*R*R*R*D*C*Q*R*D*S*C*R*R*D*.40.*.55.*R*Q*E*C*R*R*R*C*D*R*.52.*.183.*.54.*.53.*Q*.82.*Q*.54.*Q*Q*.53.*.52.*.54.*.53.*.53.*Q*Q*Q*.105.*.95.*.59.*6*D*.66.*Q*Q*.53.*Q*P*Q*Q*P*P*R*Q*P*Q*.80.*Q*Q*Q*P*C*6*5*6*.208.*.216.*Q*.80.*.108.*.53.*Q*Q*.247.*N*.52.*J*D*R*E*D*Q*E*D*R*E*C*Q*.49.*5*E*D*Q*E*D*Q*D*.41.*R*Q*E*D*Q*D*E*R*R*D*C*D*.40.*S*Q*S*R*C*E*Q*.55.*E*.40.*D*D*S*D*D*D*C*R*Q*T*K*5*D*D*Q*D*D*.81.*R*Q*.55.';
we_will_rock_you_peak_hash = '.58.*C*Q*X*.58.*X*Z*.61.*.36.*R*.63.*Z*T*.61.*.36.*U*.61.*.36.*R*.61.*W*U*.62.*X*U*.62.*.37.*R*X*F*D*X*W*W*D*D*Y*S*V*E*G*W*T*X*C*G*X*D*F*L*T*B*V*D*G*L*.39.*G*J*M*.38.*P*O*9*U*L*C*E*6*8*.60.*.65.*.62.*.61.*Q*.38.*.60.*X*T*.64.*.256.*T*Z*.59.*Z*T*.61.*M*C*T*V*R*X*W*T*E*E*T*U*6*Y*8*E*X*V*V*M*9*U*T*.50.*B*S*Z*.50.*A*F*G*U*X*G*C*W*S*U*B*F*.68.*.127.*.61.*.65.*.60.*H*H*U*.61.*.194.*.61.*.63.*.58.*Z*T*.61.*Z*S*X*S*X*S*W*F*C*W*U*Q*Y*O*A*S*V*L*7*Y*D*D*Y*R*M*7*B*M*G*C*T*X*U*E*F*Y*C*H*T*.63.*.65.*.61.*.126.*R*Z*Y*D*.45.*S*.37.*Q*.159.*.95.*N*.37.*.62.*X*S*Y*F*D*.66.*.186.*S*.96.*Y*T*.65.*.61.*.125.*.46.*.43.*.93.*.64.*.153.*G*E*E*.97.*.80.*S*.129.*C*E*.64.*V*X*V*T*G*B*G*I*V*S*W*I*.75.*V*R*W*T*K*.42.*E*F*U*E*D*G*H*W*T*T*D*.79.*U*G*.45.*U*U*E*H*V*S*Z*8*7*.45.*V*.44.*H*V*S*Z*9*7*.45.*V*T*E*H*W*R';

userinput = [1,1,4,5,1,4,1,1,4,5];
test = [2,2,1,1,4,5,3,3,1,1,4,5,1,4,8,8,9,1,1,4,5,1,4,1,7,4,5,6,]
# back_in_black_bin_array = AudioAnalysis.unhash_array(back_in_black_onset_hash);
# back_in_black_frame = bin_to_frame(back_in_black_bin_array)
# back_in_black_timestamp = librosa.frames_to_time(back_in_black_frame, sr=22050)
# print('timestamp extract from onset hash: ')
# print(back_in_black_timestamp[0:15])
# print("time stamp from librosa")
# back_in_black_timestamp_from_librosa = beat_match.process_music_onset('../../sampleMusic/backInBlack.wav')
# print(back_in_black_timestamp_from_librosa[0:15])
# 
# back_in_black_pattern_diff = process_timestamp_diff(back_in_black_timestamp_from_librosa)
# back_in_black_pattern_ratio = process_timestamp_ratio(back_in_black_timestamp_from_librosa)

# print('pattern_diff:')
# print(back_in_black_pattern_diff)
# print('pattern ratio')
# print(back_in_black_pattern_ratio)

# Seperate a song into x part to compare:
print(compare_ratio(userinput,test))