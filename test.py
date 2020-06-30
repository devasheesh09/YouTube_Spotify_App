import base64
import webbrowser
import spotipy
import spotipy.util as util
import json
import os
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


def spotify():
    token = util.prompt_for_user_token('<spotify username>',
                                       'playlist-modify-public',
                                       client_id='<your-spotify-client-id>',
                                       client_secret='<your-spotify-client-secret>',
                                       redirect_uri='<your-app-redirect-url>')
    print('token=', token)
    sp = spotipy.Spotify(auth=token)

    # sp.user_playlist_create('<spotify username>', name='spotify playlist')
    artist = sp.artist('<spotify artist urn>')
    print(type(artist))
    print('success')
    return sp


def get_youtube_token():
    """ Log Into Youtube, Copied from Youtube Data API """
    # Disable OAuthlib's HTTPS verification when running locally.
    # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    # This flow is to get access token each time from the browser session
    credential_path = os.path.join('./', 'credential_sample.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secrets_file, scopes)
        credentials = tools.run_flow(flow, store)

    # from the Youtube DATA API
    youtube_client = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    return youtube_client


def get_playlist(youtube_client):

    request = youtube_client.playlistItems().list(
        part='snippet',
        playlistId="<youtube playlist id>"
    )
    response = request.execute()

    print('response str ', response)
    print(type(response))
    title = response['items']
    title_list = []
    for x in range(len(title)):
        ti = (title[x]['snippet']['title'])
        title_list.append(ti)
    return title_list


def search_song_in_spotify(token, title_list):
    space_encrypted_titles = []
    for enc_title in title_list:
        temp = list(enc_title)
        for index, char in enumerate(temp):
            if char == '(' or char == ')' or char == '-' or char == '_':
                temp[index] = ''
        res_string = ''.join(temp)
        space_encrypted_titles.append(res_string)
    print('encrypt=', space_encrypted_titles)
    res = []
    for song in space_encrypted_titles:
        res.append(token.search(song, type='track', market='IN', limit=2))
    print('The final response= ', res)
    songs_id = []
    for i in range(len(res)):
        id = (res[i]['tracks']['items'][0]['id'])

        songs_id.append(id)
    
    return songs_id


def add_track_to_spotify_playlist(token, songs_id):
    token.user_playlist_add_tracks('<username>', '<playlist_id>', songs_id)
    print('success')


token = spotify()
youtube_client = get_youtube_token()
title_list = get_playlist(youtube_client)
songs_id = search_song_in_spotify(token, title_list)
add_track_to_spotify_playlist(token, songs_id)
