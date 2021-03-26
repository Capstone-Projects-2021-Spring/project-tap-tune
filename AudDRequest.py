import requests
data = {
    'api_token': '5e3d89525fdf63a5f5ef79f3ae87db68'
}

files = {
    'file': open('C:\\Users\\2015d\\OneDrive\\Desktop\\.wav files\\Cringe_Singing.mp3', 'rb'),
}

result = requests.post('https://api.audd.io/recognizeWithOffset/', data=data, files=files)
print(result.text)
# result2 = requests.post('https://api.audd.io/ ', data=data, files=files)
# print(result2.text)