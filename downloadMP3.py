from __future__ import print_function

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

sourceVideoList = []
destinationVideoListIds = []
videosToAdd = []
destinationPlaylist = "LL"


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

def downloadMP3(videoList):
    #for video in videoList:
    #   yt = YouTube(f'https://www.youtube.com/watch?v={video["id"]}')
    #   video = yt.streams.filter(only_audio=True).first()
    #   destination = './likedVideos'
    #   out_file = video.download(output_path=destination)
    #   base, ext = os.path.splitext(out_file)
    #   new_file = base + '.mp3'
    #   os.rename(out_file, new_file)
    #   print(yt.title + " has been successfully downloaded.")

def split(a, n):
    k, m = divmod(len(a), n)
    return [a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]

startTime = datetime.now()
print(startTime)
if __name__ == '__main__':
    downloadSourceVideoList()
    numOfProcesses = 4
    sourceVideoList = list(split(sourceVideoList, numOfProcesses))
    pool = Pool(processes=numOfProcesses)
    results = pool.map(downloadMP3, sourceVideoList)
    pool.close()
    endTime = datetime.now()
    print('Duration: {}'.format(endTime - startTime))


