from __future__ import print_function
import os.path

import googleapiclient
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly',
          'https://www.googleapis.com/auth/youtube']

sourceVideoList = []
destinationVideoListIds = []
videosToAdd = []
destinationPlaylist = "PLP_vOMhofnYfPFS4pcBA9f_84145xHu_8"


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
    i = 1
    creds = getToken()
    youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)
    request = youtube.videos().list(part='snippet', myRating='like', maxResults=50)
    response = request.execute()
    for item in response['items']:
        sourceVideoList.append({'iter': i,
                                'id': item['id'],
                                'title': item['snippet']['title']})
        i += 1
    print(sourceVideoList)


def downloadDestinationList():
    creds = getToken()
    youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)
    request = youtube.playlistItems().list(part='snippet', playlistId=destinationPlaylist, maxResults=50)
    response = request.execute()
    for item in response['items']:
        destinationVideoListIds.append(item['snippet']['resourceId']['videoId'])
    print(destinationVideoListIds)


def getMissingVideos():
    for video in sourceVideoList:
        if video['id'] in destinationVideoListIds:
            print("Na tym video przestaję iterować: ", video)
            break
        else:
            videosToAdd.append(video)


def refreshPlaylist():
    creds = getToken()
    for video in reversed(videosToAdd):
        print(video)
        youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=creds)
        request = youtube.playlistItems().insert(part='snippet', body={
            "snippet": {"playlistId": destinationPlaylist, "resourceId": {"kind": "youtube#video", "videoId": video["id"]}}})
        response = request.execute()
        if not response["snippet"]["resourceId"]["videoId"] == video["id"]:
            print(f"Błąd dla {video['id']}")
            break



if __name__ == '__main__':
    downloadDestinationList()
    downloadSourceVideoList()
    getMissingVideos()
    refreshPlaylist()
