import time

import requests
from api_secrets import API_KEY_ASSEMBLYAI
import sys

# upload
upload_endpoints = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
filename = sys.argv[1]
headers = {'authorization': API_KEY_ASSEMBLYAI}

def upload(filename):
    def read_file(filename, chunk_size=5242880):
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data

    url_response = requests.post(upload_endpoints,
                                 headers=headers,
                                 data=read_file(filename))

    print(url_response.json())

    audio_url = url_response.json()['upload_url']
    return audio_url


def trancribe(audio_url):
    transcript_request = {"audio_url": audio_url
                          , "language_detection": 'hi'}

    trsanscript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
    print(trsanscript_response.json())
    job_id = trsanscript_response.json()['id']
    return job_id


# poll
def polling(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    pollingg_response = requests.get(polling_endpoint, headers=headers)
    return (pollingg_response.json())


def get_transcription_result_url(audio_url):
    transcript_id = trancribe(audio_url)
    while True:
        data = polling(transcript_id)
        if data['status'] == 'completed':
            return data, None
        # elif data['status'] == 'error':
        #     return data, data['error']
        print('waiting for 30 seconds.....')
        print(data['status'])
        time.sleep(30)

audio_url = upload(filename)


def save_transcript(audio_url):
    data, error = get_transcription_result_url(audio_url)
    if data:
        file_name = filename + ".txt"
        with open(file_name, "w") as f:
            f.write(data['text'])
        print('transcription saved!!')
    # elif error:
    #     print("Error", error)


audio_url = upload(filename)
save_transcript(audio_url)
