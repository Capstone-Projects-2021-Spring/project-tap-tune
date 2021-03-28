import librosa
import AudioAnalysis
import beat_match


# Purpose: intergrate the process of hash value to timestamp in one function
# Status: In-Progess, bug spotted: converting onset hash value to timestamp looks different than getting timestamp from
#         librosa.onset.onset_detection
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


# Purpose: for pair of beats that are too closer to each other that sounds like one beat to human ears, consider them
#          as one beat
# Status: clear
def drop_ambiguous(timestamp):
    result = [timestamp[0]]
    i = 1
    while i <= len(timestamp) - 1:
        if timestamp[i] - timestamp[i - 1] >= 0.08:
            result.append(timestamp[i])
        i += 1
    return result


# Sepertaed from old process_timestamp2()
# Purpose: process timestamp and get pattern by getting time differences between each beat
# Status: clear
def process_timestamp_diff(timestamp):
    beat_diff = []
    for i in range(len(timestamp) - 1):
        temp = abs(timestamp[i + 1] - timestamp[i])
        beat_diff.append(temp)
    return beat_diff


# Seperated from old process_timestamp2()
# Purpose: analyze timestamp by deviding each timestamp by avg beat_diff, beat_diff: time difference between one beat to
#          next one
# Status: In-progess
def process_timestamp_ratio(timestamp):
    beat_diff_over_avg = []
    beat_diff = []
    diff = 0
    for i in range(len(timestamp) - 1):
        temp = abs(timestamp[i + 1] - timestamp[i])
        beat_diff.append(temp)
        diff += temp
    avg_diff = diff / (len(timestamp)-1)
    for i in range(len(beat_diff)):
        beat_diff_over_avg.append(beat_diff[i] / avg_diff)
    return beat_diff_over_avg


# Purpose: Compare two ratio pattern, calculate matching rate of user input and return matching rate
# Principle: if user_pattern[i] / song_pattern[i] is very close t 1, it is a match beat
#            since every
# Status: In progess, error range need more testing to determine
# Note: round both item to same decimal precision to compare?
def compare_ratio(user_pattern, song_pattern):
    mark = round(len(user_pattern) * 0.7)
    print('mark = {}'.format(mark))
    numOfHit = 0
    error = 0.2  # Working process
    j = 0
    match_rate = 0
    for i in range(len(song_pattern) - len(user_pattern)):
        while j < len(user_pattern):
            match_rate_this_beat = round(1 - (abs(1 - user_pattern[j] / song_pattern[i])), 4)
            print("match rate of user_pattern[{}]: {} and song_patter[{}]: {} is {}".format(j, user_pattern[j],
                                                                                            i, song_pattern[i],
                                                                                            match_rate_this_beat))
            if match_rate_this_beat >= 0.8:
                print("It's a hit!")
                numOfHit += 1
                match_rate += match_rate_this_beat
                print('Update match_rate: {}'.format(match_rate))
                i += 1
                j += 1
                break
            elif j < len(user_pattern) - 1:
                j += 1
            else:
                j = 0
                break

        # if numOfHit >= mark:
        #     return 1, match_rate / numOfHit
    print('numOfHit: {}, match_rate: {}'.format(numOfHit, match_rate))
    if numOfHit >= mark:
        return 1, round(match_rate / len(user_pattern),4)
    else:
        return 0, round(match_rate / len(user_pattern), 4)


# Purpose: Another implementation of ratio compare
# Principle: if two pattern a,b are similar, a rate X exist such that for i in b, b[i] = X*a[i]
#            meaning that two pattern can be synchronize with [X-error, X+error]
def compare_ratio2(user_pattern, song_pattern):
    mark = len(user_pattern) * 0.7
    error = 0.2
    numOfHit = 0
    syn = user_pattern[0] / song_pattern[0]
    for i in range(len(song_pattern)):

        for j in range(len(user_pattern)):

            if syn - error <= user_pattern[j] / song_pattern[i] <= syn + error:
                numOfHit += 1
            else:
                syn = 0
                break
        if numOfHit >= mark:
            return 1
    if numOfHit >= mark:
        return 1
    else:
        return 0;


# Purpose: Split a song into three section as a list. Iterate through the list for compare, provide early exit if song
#          match in the first half.
#   section one: first half
#   Section two: Second half
#   Section three(enhanced section): from middle of first half to middle of second half, last section to run, make sure
#                                    no part is missed
# Principle: compare first half first, if not match, compare with second half, if both are not match, exit. If both have
#            some match, compare
#            the third section to ensure
# Status: Clear
# Note: Another approach to split the song?
def split_song(song_pattern):
    length = len(song_pattern)
    pattern_set = [song_pattern[0:(length / 2)], song_pattern[(length / 2):-1],
                   song_pattern[(length / 4):(length * 3 / 4)]]
    return pattern_set



#-----------------------------------------------Hash Compare Area-------------------------------------------------------
#Purpose: receive hashes as input, return ratio pattern in hash format,
def process_timestamp_hash(hashes):
        result = []
        #go through the content in hashes
        for i in range(len(hashes)):
            #split the hash
            #convert each combination into number
            # use the number to calculate
            # record result to the result array
            #
            result.append()



# def compare_ratio_hash(user_hash, song_hash):
#     mark = 0.7 #70% match rate
#     numOfHit = 0
#     matching_rate = 0
#     for i in range(len(song_hash)):
#         for j in range(len(user_hash)):
#
#     if numOfHit >= mark:
#         return 1, matching_rate
#     else:
#         return 0, matching_rate



# ------------------------------------------------TESTING AREA----------------------------------------------------------
back_in_black_onset_hash = 'I*.60.*0*R*S*T*R*T*R*S*Q*S*E*E*Q*D*E*D*D*S*7*6*7*5*R*E*C*E*D*E*C*E*E*D*C*8*B*8*B*9*B*6*D*Q*D*E*R*D*E*R*S*7*6*7*5*R*E*D*E*E*R*D*E*E*C*L*K*J*K*M*4*S*D*5*6*F*D*D*7*5*D*E*6*6*D*M*5*E*C*E*E*D*7*5*E*D*D*C*L*K*7*C*5*D*R*E*D*E*C*E*D*D*6*6*D*E*D*E*E*C*D*D*F*Q*D*F*C*E*C*K*K*J*D*6*Q*Q*.81.*Q*Q*.55.*P*Q*R*R*Q*P*R*.80.*.54.*.52.*Q*.67.*D*Q*.78.*Q*L*5*E*D*Q*D*E*D*6*5*R*E*D*R*Q*0*E*C*J*5*0*E*D*D*6*4*M*K*K*J*L*5*R*E*6*5*D*E*D*5*6*C*E*E*D*C*E*K*7*D*E*D*C*M*6*D*D*6*C*K*7*B*E*6*P*R*.81.*Q*R*Q*R*Q*R*.54.*Q*P*.54.*.80.*Q*Q*P*Q*Q*Q*Q*Q*J*.87.*R*R*R*D*D*R*E*B*E*C*Q*R*R*D*C*S*Q*D*.95.*R*R*D*C*R*E*D*D*C*D*C*R*S*D*C*E*.40.*D*D*.80.*E*C*R*R*R*R*D*C*Q*R*D*S*C*R*R*D*.40.*.55.*R*Q*E*C*R*R*R*C*D*R*.52.*.183.*.54.*.53.*Q*.82.*Q*.54.*Q*Q*.53.*.52.*.54.*.53.*.53.*Q*Q*Q*.105.*.95.*.59.*6*D*.66.*Q*Q*.53.*Q*P*Q*Q*P*P*R*Q*P*Q*.80.*Q*Q*Q*P*C*6*5*6*.208.*.216.*Q*.80.*.108.*.53.*Q*Q*.247.*N*.52.*J*D*R*E*D*Q*E*D*R*E*C*Q*.49.*5*E*D*Q*E*D*Q*D*.41.*R*Q*E*D*Q*D*E*R*R*D*C*D*.40.*S*Q*S*R*C*E*Q*.55.*E*.40.*D*D*S*D*D*D*C*R*Q*T*K*5*D*D*Q*D*D*.81.*R*Q*.55.';
we_will_rock_you_peak_hash = '.58.*C*Q*X*.58.*X*Z*.61.*.36.*R*.63.*Z*T*.61.*.36.*U*.61.*.36.*R*.61.*W*U*.62.*X*U*.62.*.37.*R*X*F*D*X*W*W*D*D*Y*S*V*E*G*W*T*X*C*G*X*D*F*L*T*B*V*D*G*L*.39.*G*J*M*.38.*P*O*9*U*L*C*E*6*8*.60.*.65.*.62.*.61.*Q*.38.*.60.*X*T*.64.*.256.*T*Z*.59.*Z*T*.61.*M*C*T*V*R*X*W*T*E*E*T*U*6*Y*8*E*X*V*V*M*9*U*T*.50.*B*S*Z*.50.*A*F*G*U*X*G*C*W*S*U*B*F*.68.*.127.*.61.*.65.*.60.*H*H*U*.61.*.194.*.61.*.63.*.58.*Z*T*.61.*Z*S*X*S*X*S*W*F*C*W*U*Q*Y*O*A*S*V*L*7*Y*D*D*Y*R*M*7*B*M*G*C*T*X*U*E*F*Y*C*H*T*.63.*.65.*.61.*.126.*R*Z*Y*D*.45.*S*.37.*Q*.159.*.95.*N*.37.*.62.*X*S*Y*F*D*.66.*.186.*S*.96.*Y*T*.65.*.61.*.125.*.46.*.43.*.93.*.64.*.153.*G*E*E*.97.*.80.*S*.129.*C*E*.64.*V*X*V*T*G*B*G*I*V*S*W*I*.75.*V*R*W*T*K*.42.*E*F*U*E*D*G*H*W*T*T*D*.79.*U*G*.45.*U*U*E*H*V*S*Z*8*7*.45.*V*.44.*H*V*S*Z*9*7*.45.*V*T*E*H*W*R';

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
# print(compare_ratio(userinput, test))


# ------------------------------------Recycle Zone-------------------------------------------------------
userinput = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,17,18,19,20,21,22,23,24,25,26,27,28,38,48,58,68]
input2 = [1, 4, 6, 8, 8.2,8.3,8.4,8.5,12, 14, 16, 17]
userinput = drop_ambiguous(userinput)
userinput = process_timestamp_ratio(userinput)
input2 = process_timestamp_ratio(input2)
print("userinput ratio pattern:")
print(userinput)
print("input2 ratio pattern: ")
print(input2)
print("userinput[0]/input2[0]")
print(userinput[0] / input2[0])
result, matchrate = compare_ratio(input2, userinput)
print("result: {}, rate: {}".format(result, matchrate))
# test = [2, 2, 1, 1, 4, 5, 3, 3, 1, 1, 4, 5, 1, 4, 8, 8, 9, 1, 1, 4, 5, 1, 4, 1, 7, 4, 5, 6, ]
