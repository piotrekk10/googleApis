from __future__ import print_function

import multiprocessing.pool

import googleapiclient
import os.path

from multiprocessing import Pool
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pytube import YouTube

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly',
          'https://www.googleapis.com/auth/youtube']

destinationPlaylist = "LL"
destinationFolderPath = './likedVideos'
errorList = []


def getToken():
    creds = None
    if os.path.exists('tokenYoutube.json'):
        creds = Credentials.from_authorized_user_file('tokenYoutube.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('tokenYoutube.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def downloadSourceVideoList():
    sourceVideoList = []
    nextPageToken = ''
    creds = getToken()
    youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)
    while True:
        if nextPageToken:
            request = youtube.playlistItems().list(part='snippet', playlistId=destinationPlaylist, maxResults=50,
                                                   pageToken=nextPageToken)
            response = request.execute()
        else:
            request = youtube.playlistItems().list(part='snippet', playlistId=destinationPlaylist, maxResults=50)
            response = request.execute()
        for item in response['items']:
            sourceVideoList.append(item['snippet']['resourceId']['videoId'])
        if 'nextPageToken' in response.keys():
            nextPageToken = response['nextPageToken']
        else:
            break
    print(len(sourceVideoList))
    return sourceVideoList


def downloadMP3(videoList):
        for videoId in videoList:
            try:
                yt = YouTube(f'https://www.youtube.com/watch?v={videoId}')
                video = yt.streams.filter(only_audio=True).first()
                out_file = video.download(output_path=destinationFolderPath)
                base, ext = os.path.splitext(out_file)
                new_file = base + '.mp3'
                os.rename(out_file, new_file)
                print(yt.title + " has been successfully downloaded.")
            except Exception  as e:
                errorList.append(e)
                pass


def split(a, n):
    k, m = divmod(len(a), n)
    return [a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

def clearFiles():
    count = 0

    for file in os.listdir(destinationFolderPath):
        if file.endswith('mp4'):
            os.remove(destinationFolderPath + '/' + file)
            count += 1
    print(f'Usunięto {count} plików')


def multiProcess():
    videoList = downloadSourceVideoList()
    numOfProcesses = 4
    sourceVideoList = list(split(videoList, numOfProcesses))
    pool = Pool(processes=numOfProcesses)
    pool.map(downloadMP3, sourceVideoList)
    pool.close()


def oneProcess():
    videoList = downloadSourceVideoList()
    downloadMP3(videoList)


if __name__ == '__main__':
    startTime = datetime.now()
    print(startTime)

    #oneProcess()
    multiProcess()

    endTime = datetime.now()
    print('Duration: {}'.format(endTime - startTime))
    clearFiles()
    print(errorList)
    for error in errorList:
        print(error)
