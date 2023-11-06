from typing import List, Tuple
import pandas as pd
from Google import create_service as Create_Service
import os
from db_connect import *

# def getChannelPlaylists(channelId: str):
#     """returning only id will cost zero quota"""
#     try:
#         items = []
#         response = service.playlists().list(
#             channelId=channelId,
#             maxResults=50,
#             part='id'
#         ).execute()
#         items.extend(response.get('items'))
#         nextPageToken = response.get('nextPageToken')

#         while nextPageToken:
#             response = service.playlists().list(
#                 channelId=channelId,
#                 maxResults=50,
#                 part='id',
#                 pageToken=nextPageToken
#             ).execute()
#             items.extend(response.get('items'))
#             nextPageToken = response.get('nextPageToken')
#         return items
#     except Exception as e:
#         print(e)
#         return
    
def getMyChannelPlaylists(service):
    try:
        items = []
        response = service.playlists().list(
            mine=True,
            maxResults=50,
            part='snippet'
        ).execute()
        items.extend(response.get('items'))
        nextPageToken = response.get('nextPageToken')

        while nextPageToken:
            response = service.playlists().list(
                mine=True,
                maxResults=50,
                part='snippet',
                pageToken=nextPageToken
            ).execute()
            items.extend(response.get('items'))
            nextPageToken = response.get('nextPageToken')
        return items
    except Exception as e:
        print(e)
        return

def getPlaylistVideos(serviceInstance, playlistId: str) -> Tuple[List, str]:
    try:
        playlistItems = serviceInstance.playlists().list(
            part='snippet',
            id=playlistId
        ).execute()
        playlistTitle = playlistItems.get('items')[0]['snippet'].get('localized').get('title')

        maxResults = 50
        items = []

        response = serviceInstance.playlistItems().list(
            part='contentDetails,snippet',
            playlistId=playlistId,
            maxResults=maxResults
        ).execute()
        items.extend(response.get('items'))
        nextPageToken = response.get('nextPageToken')

        while nextPageToken:
            response = serviceInstance.playlistItems().list(
                part='contentDetails,snippet',
                playlistId=playlistId,
                maxResults=maxResults,
                pageToken=nextPageToken
            ).execute()
            items.extend(response.get('items'))
            nextPageToken = response.get('nextPageToken')
        return (items, playlistTitle)
    except Exception as e:
        print(e)
        return

def exportPlaylistToExcel(playlistItems: List, excelPath: str) -> None:
    try:
        if not excelPath.endswith('.xlsx'):
            print('Excel file path is invalid.')
            return

        with pd.ExcelWriter(excelPath, engine='openpyxl') as xlwriter:
            df = pd.DataFrame(playlistItems)
            # for time saving, I am going to export everything
            df['snippet'].apply(pd.Series).to_excel(xlwriter, sheet_name='snippet', index=False)
            df['contentDetails'].apply(pd.Series).to_excel(xlwriter, sheet_name='contentDetails', index=False)

        print('Export is saved at "{0}"'.format(excelPath))
    except Exception as e:
        print(e)
        return


if __name__ == '__main__':
    file_name = 'client_secret_3_10_PM.json'
    path = os.getcwd()
    CLIENT_FILE = os.path.join(path, file_name)
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube']
    service = Create_Service(CLIENT_FILE, API_NAME, API_VERSION, SCOPES)

    CLIENT_FILE_DICT = {'client_file': 'client_secret_3_10_PM.json'}
    
    playlistIds = getMyChannelPlaylists(service)
    conn = db_connect()

    def save_playlist(playlist_obj, playlist_items):
        r_type = 'STORED-PROCEDURE'
        r_name = 'sp_insert_or_update_playlist'
        video_list = []
        for item in playlist_items:
            video_list.append({
                'ytube_video_id': item['id'],
                'video_title': item['snippet']['title'],
                'video_description': item['snippet']['description'],
                'channel_name':item['snippet']['videoOwnerChannelTitle'],
                'channel_id': item['snippet']['videoOwnerChannelId']
            })

        args_dict = {

                        'ytube_playlist_id': playlist_obj["id"],
                        'playlist_name'    : playlist_obj["snippet"]["title"],
                        'channel_owner'    : playlist_obj["snippet"]['channelTitle'],
                        'videos_list'      : json.dumps(video_list)
                    }

        args = list(args_dict.values())
        try:
            stored_procedure_call(conn, r_type, r_name, *args)
        except psycopg2.Error as e:
            print("SQLSTATE:", e.pgcode)
            print("Error message:", e.pgerror)  
    
    def update_status():
        r_type = 'STORED-PROCEDURE'
        r_name = 'sp_update_status_removed_content'
        try:
            stored_procedure_call(conn, r_type, r_name)
        except psycopg2.Error as e:
            print("SQLSTATE:", e.pgcode)
            print("Error message:", e.pgerror)  

    for playlistId in playlistIds:
        # DB save playlist call
        playlistItems, playlistTitle = getPlaylistVideos(service, playlistId['id'])
        # if a playlsit has no video, then there is nothign to exprot
        if playlistItems :
            save_playlist(playlistId,playlistItems)
            exportPlaylistToExcel(playlistItems, 'Playist backup ({0}).xlsx'.format(playlistTitle))
    
    # update_status()