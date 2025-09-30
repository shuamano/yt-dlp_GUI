#v.0.8, 9/26/25
#this is some of the shittiest code ever written

import importlib.metadata, subprocess, sys
required = {'flet', 'yt-dlp', 'humanfriendly', 'pyperclip', 'spotdl'}
installed = {pkg.metadata['Name'] for pkg in importlib.metadata.distributions()}
missing = required - installed

if missing: 
    print(missing)
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])

import flet as ft
import yt_dlp
from humanfriendly import format_timespan, format_size
import pyperclip
import os
import requests
from base64 import b64encode
import time
import json
from pathlib import Path
import threading
from multiprocessing import Process
import datetime


home_dir = os.path.expanduser("~")

CREATE_NO_WINDOW = 0x08000000

queue = []
item_list = []
number_of_songs = 0
added_controls = []
tlds = ['.com', '.org', '.net', '.edu', '.gov', '.io', 'to', '.be', '.gg', '.fm', '.tv', '.us', '.uk', '.ca', '.au', '.in', '.de', '.fr', '.es', '.it', '.nl', '.se', '.no', '.fi', '.jp', '.cn', '.ru', '.br', '.za', '.mx']
color_controls = []
flags = {}
finished_threads = {}
history_tabs = {}

# check if a config file has already been created. if yes, assign everything to its configuration, if not use defualt config   
if Path('yt-dlp_GUI_settings.json').is_file(): 
    with open("yt-dlp_GUI_settings.json", mode="r", encoding="utf-8") as read_file:
        settings_stored = json.load(read_file)
    client_id = settings_stored["client_id"]
    client_secret = settings_stored["client_secret"]
    theme_setting = settings_stored["theme"]
    transparency_setting = settings_stored['transparency']
    downloads_folder = settings_stored['save_location']
    auto_start = settings_stored['auto_start']
    crop_thumbnails = settings_stored['crop_thumbnails']
    saved_history_tabs = settings_stored['history']
    open_console = settings_stored['open_console']
    if theme_setting == True:
        main_color= ft.Colors.GREEN
        secondary_color = ft.Colors.BLACK26
        bg_color = ft.Colors.BLACK12
        preview_color  = ft.Colors.BLACK54
    else:
        main_color = ft.Colors.BLUE
        secondary_color = ft.Colors.WHITE10
        bg_color = ft.Colors.WHITE10
        preview_color = ft.Colors.WHITE10
else:
    #default config
    downloads_folder = os.path.join(home_dir, "Downloads")
    auto_start = False
    crop_thumbnails = False 
    client_id = '0cc3fdffe0f84a1c80a2b2cdf4df1390'
    client_secret = 'e60c4550c2fd442ebebb8c7b3fbdd4fa'
    theme_setting = True
    transparency_setting = 0.0
    main_color= ft.Colors.GREEN
    secondary_color = ft.Colors.BLACK26
    bg_color = ft.Colors.BLACK12
    preview_color  = ft.Colors.BLACK54
    saved_history_tabs = {}
    open_console = False

def get_spotify_data(link, token):
    
    id = link.split('/')[-1]
    type = link.split('/')[-2] 
    

    if type == 'track':
        url = f'https://api.spotify.com/v1/tracks/{id}'
    elif type == 'album':
        url = f'https://api.spotify.com/v1/albums/{id}'
    elif type == 'playlist':
        url = f'https://api.spotify.com/v1/playlists/{id}'
    else:
        return None

    # Make the API request
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)

    
    return response.json()
    
def get_client_credentials_token(client_id, client_secret):
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + b64encode(f'{client_id}:{client_secret}'.encode()).decode(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, headers=headers, data=data)
    access_token = response.json()['access_token']
    return access_token

try:
    token_response = get_client_credentials_token(client_id, client_secret)
    access_token = token_response
except:
    print("bad spotify credentials")

def spotify_link():
    global added_controls
    global number_of_songs
    global item_list
    global history_tabs
    unique_id = link_entry.value
    time = datetime.date.today()
    token_response = get_client_credentials_token(client_id, client_secret)
    access_token = token_response
    data = get_spotify_data(link_entry.value, access_token)
    
    if 'playlist' not in unique_id and 'album' not in unique_id:
        song_name = data.get("name", "Unknown Song")
        album_name = data.get("album", {}).get("name", "Unknown Album")
        artist_name = data.get("artists", [{}])[0].get("name", "Unknown Artist")
        album_art_url = data.get("album", {}).get("images", [{}])[0].get("url", "No album art available")
        length_ms = data.get('duration_ms') 
        try:
            minutes =(length_ms // 1000) // 60
            seconds = length_ms // 1000 - (minutes * 60)
            if seconds < 10:
                seconds = f"0{seconds}"
            song_duration = f"{minutes}:{seconds}"
        except:
            song_duration = "couldnt fetch duration"
        #print(data)     
        history_tab = ft.Card(content=ft.Container(content=ft.Row(controls=[ft.Row([ft.Image(src=album_art_url,width=60,height=60,fit=ft.ImageFit.CONTAIN,border_radius=ft.border_radius.all(5)),ft.Column(controls=[ft.Text(song_name, size=20), ft.Text(f"{artist_name} - {datetime.date.today()}")])]),ft.ElevatedButton("Copy link", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.COPY, height = 60, width = 130, on_click=lambda e, link=link_entry.value, id=unique_id: pyperclip.copy(link))],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),padding=10, bgcolor=secondary_color,))
        history_tabs[unique_id] = [album_art_url, song_name, artist_name, str(time)]
        preview_tab = ft.Card(
            content=ft.Container(
                content=ft.Row(
                    controls=[
                    ft.Image(
                    src=album_art_url,
                    width=100,
                    height=100,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=ft.border_radius.all(5)),
                    
                    ft.Column(
                        controls=[
                            ft.Text(song_name, size=20,  weight=ft.FontWeight.BOLD),
                            ft.Text(f"{artist_name} • {album_name}"),
                            ft.Text(f"{song_duration}", size = 14,  weight=ft.FontWeight.W_500)
                        ], expand=1, alignment=ft.MainAxisAlignment.SPACE_EVENLY
                    ),
                    ft.Container( #control 3
                        content=ft.Column(
                            controls=[
                            ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value,  id=unique_id: individual_download(link)),
                            ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.Icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value,  id=unique_id: remove_control(link))
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY
                                        ),
                            #alignment=ft.alignment.center_right  # Align container to the right
                                ),   

                    ]),
                width=700,
                height=110,
                padding=ft.Padding(left = 5, top = 5, bottom =5, right = 10),
                border_radius=5,
                bgcolor=preview_color,
                alignment=ft.alignment.center))

    #if its a playlist:    
    elif 'playlist' in unique_id:
        playlist_name = data.get('name')
        playlist_length = data.get('tracks').get('total')
        playlist_owner = data.get('owner').get('display_name')
        playlist_art = data.get('images')[0].get('url')
        playlist_duration = 0
        try:
            for song in data.get('tracks').get('items'):
                playlist_duration += song['track']['duration_ms']
        except:
            pass
        #minutes=playlist_duration//1000//60
        #seconds=playlist_duration//1000-minutes*60
        #if seconds < 10:
        #    seconds = f"0{seconds}"
        playlist_duration = playlist_duration //1000
        history_tab = ft.Card(content=ft.Container(content=ft.Row(controls=[ft.Row([ft.Image(src=playlist_art,width=60,height=60,fit=ft.ImageFit.CONTAIN,border_radius=ft.border_radius.all(5)),ft.Column(controls=[ft.Text(playlist_name, size=20), ft.Text(f"{playlist_owner} - {datetime.date.today()}")])]),ft.ElevatedButton("Copy link", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.COPY, height = 60, width = 130, on_click=lambda e, link=link_entry.value, id=unique_id: pyperclip.copy(link))],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),padding=10, bgcolor=secondary_color,))        
        history_tabs[unique_id] = [playlist_art, playlist_name, playlist_owner, str(time)]
        preview_tab = ft.Card(
            content=ft.Container(
                content=ft.Row(
                    controls=[
                    ft.Image(
                    src=playlist_art,
                    width=100,
                    height=100,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=ft.border_radius.all(5)),
                    
                    ft.Column(
                        controls=[
                            ft.Text(playlist_name, size=20,  weight=ft.FontWeight.BOLD),
                            ft.Text(f"{playlist_owner} • {playlist_length} items"),
                            ft.Text(f"{format_timespan(playlist_duration)}", size = 14,  weight=ft.FontWeight.W_500)
                        ], expand=1, alignment=ft.MainAxisAlignment.SPACE_EVENLY
                    ),
                    ft.Container( #control 3
                        content=ft.Column(
                            controls=[
                            ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value,  id=unique_id: individual_download(link)),
                            ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.Icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value,  id=unique_id: remove_control(link))
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY
                                        ),
                            #alignment=ft.alignment.center_right  # Align container to the right
                                ),   

                    ]),
                width=700,
                height=110,
                padding=ft.Padding(left = 5, top = 5, bottom =5, right = 10),
                border_radius=5,
                bgcolor=preview_color,
                alignment=ft.alignment.center))
        
    else: #for albums
        #print(data)    
        total_tracks = data.get('total_tracks')
        artist = data['artists'][0]['name']
        album_art = data['images'][0]['url']
        title = data['name']
        duration = 0
        for song in data['tracks']['items']:
            duration = duration + song['duration_ms']

        history_tab = ft.Card(content=ft.Container(content=ft.Row(controls=[ft.Row([ft.Image(src=album_art,width=60,height=60,fit=ft.ImageFit.CONTAIN,border_radius=ft.border_radius.all(5)),ft.Column(controls=[ft.Text(title, size=20), ft.Text(f"{artist} - {datetime.date.today()}")])]),ft.ElevatedButton("Copy link", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.COPY, height = 60, width = 130, on_click=lambda e, link=link_entry.value, id=unique_id: pyperclip.copy(link))],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),padding=10, bgcolor=secondary_color,))        
        history_tabs[unique_id] = [album_art, title, artist, str(time)]
        preview_tab = ft.Card(
            content=ft.Container(
                content=ft.Row(
                    controls=[
                    ft.Image(
                    src=album_art,
                    width=100,
                    height=100,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=ft.border_radius.all(5)),
                    
                    ft.Column(
                        controls=[
                            ft.Text(f"Album - {title}", size=20,  weight=ft.FontWeight.BOLD),
                            ft.Text(f"{artist} • {total_tracks} items"),
                            ft.Text(f"{format_timespan(duration//1000)}", size = 14,  weight=ft.FontWeight.W_500)
                        ], expand=1, alignment=ft.MainAxisAlignment.SPACE_EVENLY
                    ),
                    ft.Container( #control 3
                        content=ft.Column(
                            controls=[
                            ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value,  id=unique_id: individual_download(link)),
                            ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.Icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value,  id=unique_id: remove_control(link))
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY
                                        ),
                            #alignment=ft.alignment.center_right  # Align container to the right
                                ),   

                    ]),
                width=700,
                height=110,
                padding=ft.Padding(left = 5, top = 5, bottom =5, right = 10),
                border_radius=5,
                bgcolor=preview_color,
                alignment=ft.alignment.center))
        
    added_controls.append((unique_id, preview_tab))
    if preview_placeholder in lv.content.controls:
        lv.content.controls.remove(preview_placeholder)
    lv.content.controls.insert(0, preview_tab)

def youtube_link():
    global added_controls
    global number_of_songs
    global item_list
    global history_tabs
    unique_id = link_entry.value
    time = datetime.date.today()
    #if from ytmusic:
    if 'music' in unique_id:
        if 'playlist' not in unique_id: #if its just a song:
            ydl_opts = {'dump_single_json': True, 'flat_playlist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                song_info = ydl.extract_info(link_entry.value.strip(), download=False)
                album_art_url = song_info.get("thumbnails")[2]["url"]
                file_size = song_info.get('filesize_approx')
                album = song_info.get('album')
                length = song_info.get('duration')
                minutes = length // 60
                seconds = length - (minutes * 60)
                if seconds < 10:
                    seconds = f"0{seconds}"

                megabytes = file_size // 1048576
            history_tab = ft.Card(content=ft.Container(content=ft.Row(controls=[ft.Row([ft.Image(src=album_art_url,width=60,height=60,fit=ft.ImageFit.CONTAIN,border_radius=ft.border_radius.all(5)),ft.Column(controls=[ft.Text(song_info.get('title'), size=20), ft.Text(f"{song_info.get('uploader')} - {datetime.date.today()}")])]),ft.ElevatedButton("Copy link", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.COPY, height = 60, width = 130, on_click=lambda e, link=link_entry.value, id=unique_id: pyperclip.copy(link))],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),padding=10, bgcolor=secondary_color,))            
            history_tabs[unique_id] = [album_art_url, song_info.get('title'), song_info.get('uploader'), str(time)]
            preview_tab = ft.Card(
                content=ft.Container(
                    content=ft.Row(
                        controls=[
                        ft.Image(
                        src=album_art_url,
                        width=100,
                        height=100,
                        fit=ft.ImageFit.CONTAIN,
                        border_radius=ft.border_radius.all(5)),
                        
                        ft.Column(
                            controls=[
                                ft.Text(song_info.get('title'), size=20,  weight=ft.FontWeight.BOLD),
                                ft.Text(f"{song_info.get('uploader')} • {album}"),
                                ft.Text(f"{minutes}:{seconds} - {format_size(file_size)}", size = 14,  weight=ft.FontWeight.W_500)
                            ], expand=1, alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                        
                        ft.Container( #control 3
                            content=ft.Column(
                                controls=[
                                ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: individual_download(link)),
                                ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.Icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: remove_control(link))
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                                            ),
                                #alignment=ft.alignment.center_right  # Align container to the right
                                    ),   

                        ]),
                    width=700,
                    height=110,
                    padding=ft.Padding(left = 5, top = 5, bottom =5, right = 10),
                    border_radius=5,
                    bgcolor=preview_color,
                    alignment=ft.alignment.center))

        else: #if its an album or playlist
            ydl_opts = {'dump_single_json': True, 'extract_flat': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(link_entry.value.strip(), download=False)
            
            playlist_title = playlist_info.get("title")                
            playlist_art = playlist_info['thumbnails'][0]['url']
            playlist_owner = playlist_info.get('uploader')
            playlist_length = playlist_info.get('playlist_count')
            if 'Album' in playlist_title:
                playlist_owner = playlist_info['entries'][0]['uploader']
            history_tab = ft.Card(content=ft.Container(content=ft.Row(controls=[ft.Row([ft.Image(src=playlist_art,width=60,height=60,fit=ft.ImageFit.CONTAIN,border_radius=ft.border_radius.all(5)),ft.Column(controls=[ft.Text(playlist_title, size=20), ft.Text(f"{playlist_owner} - {datetime.date.today()}")])]),ft.ElevatedButton("Copy link", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.COPY, height = 60, width = 130, on_click=lambda e, link=link_entry.value, id=unique_id: pyperclip.copy(link))],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),padding=10, bgcolor=secondary_color,))            
            history_tabs[unique_id] = [playlist_art, playlist_title, playlist_owner, str(time)]
            preview_tab = ft.Card(
                content=ft.Container(
                    content=ft.Row(
                        controls=[
                        ft.Image(
                        src=playlist_art,
                        width=100,
                        height=100,
                        fit=ft.ImageFit.CONTAIN,
                        border_radius=ft.border_radius.all(5)),
                        
                        ft.Column(
                            controls=[
                                ft.Text(playlist_title, size=20,  weight=ft.FontWeight.BOLD),
                                ft.Text(playlist_owner),
                                ft.Text(f"{playlist_length} items", size = 14,  weight=ft.FontWeight.W_500)
                            ], expand=1, alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                        
                        ft.Container( #control 3
                            content=ft.Column(
                                controls=[
                                ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: individual_download(link)),
                                ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.Icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: remove_control(link))
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                                            ),
                                #alignment=ft.alignment.center_right  # Align container to the right
                                    ),   

                        ]),
                    width=700,
                    height=110,
                    padding=ft.Padding(left = 5, top = 5, bottom =5, right = 10),
                    border_radius=5,
                    bgcolor=preview_color,
                    alignment=ft.alignment.center))
            
    else: #if its just a video
        if 'playlist' not in unique_id:
            ydl_opts = {'dump_single_json': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                song_info = ydl.extract_info(link_entry.value.strip(), download=False)
                album_art_url = song_info.get("thumbnails")[2]["url"]
                file_size = song_info.get('filesize_approx')
                album = song_info.get('album')
                length = song_info.get('duration')
                minutes = length // 60
                seconds = length - (minutes * 60)
                if seconds < 10:
                    seconds = f"0{seconds}"

                    megabytes = file_size // 1048576
                    decimal_place = (file_size - (megabytes * 1048576)) % 1048576
                    #print(song_info)
                history_tab = ft.Card(content=ft.Container(content=ft.Row(controls=[ft.Row([ft.Image(src=album_art_url,width=60,height=60,fit=ft.ImageFit.CONTAIN,border_radius=ft.border_radius.all(5)),ft.Column(controls=[ft.Text(song_info.get('title'), size=20), ft.Text(f"{song_info.get('uploader')} - {datetime.date.today()}")])]),ft.ElevatedButton("Copy link", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.COPY, height = 60, width = 130, on_click=lambda e, link=link_entry.value, id=unique_id: pyperclip.copy(link))],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),padding=10, bgcolor=secondary_color,))                
                history_tabs[unique_id] = [album_art_url, song_info.get('title'), song_info.get('uploader'), str(time)]
                preview_tab = ft.Card(
                    content=ft.Container(
                        content=ft.Row(
                            controls=[
                            ft.Image(
                            src=album_art_url,
                            width=100,
                            height=100,
                            fit=ft.ImageFit.CONTAIN,
                            border_radius=ft.border_radius.all(5)),
                            
                            ft.Column(
                                controls=[
                                    ft.Text(song_info.get('title'), size=20,  weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{song_info.get('uploader')}"),
                                    ft.Text(f"{minutes}:{seconds} - {format_size(file_size)}", size = 14,  weight=ft.FontWeight.W_500)
                                ], expand=1, alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                            
                            ft.Container( #control 3
                                content=ft.Column(
                                    controls=[
                                    ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: individual_download(link)),
                                    ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.Icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: remove_control(link))
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_EVENLY
                                                ),
                                    #alignment=ft.alignment.center_right  # Align container to the right
                                        ),   

                            ]),
                        width=700,
                        height=110,
                        padding=ft.Padding(left = 5, top = 5, bottom =5, right = 10),
                        border_radius=5,
                        bgcolor=preview_color,
                        alignment=ft.alignment.center))

        else:  #if its a normal yt playlist
            ydl_opts = {'dump_single_json': True, 'extract_flat': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(link_entry.value.strip(), download=False)
            #print(playlist_info)
            playlist_title = playlist_info.get("title")                
            playlist_art = playlist_info['thumbnails'][0]['url']
            playlist_owner = playlist_info.get('uploader')
            playlist_length = playlist_info.get('playlist_count')
            if 'Album' in playlist_title:
                playlist_owner = playlist_info['entries'][0]['uploader']
            history_tab = ft.Card(content=ft.Container(content=ft.Row(controls=[ft.Row([ft.Image(src=playlist_art,width=60,height=60,fit=ft.ImageFit.CONTAIN,border_radius=ft.border_radius.all(5)),ft.Column(controls=[ft.Text(playlist_title, size=20), ft.Text(f"{playlist_owner} - {datetime.date.today()}")])]),ft.ElevatedButton("Copy link", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.COPY, height = 60, width = 130, on_click=lambda e, link=link_entry.value, id=unique_id: pyperclip.copy(link))],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),padding=10, bgcolor=secondary_color,))            
            history_tabs[unique_id] = [playlist_art, playlist_title, playlist_owner, str(time)]
            preview_tab = ft.Card(
                content=ft.Container(
                    content=ft.Row(
                        controls=[
                        ft.Image(
                        src=playlist_art,
                        width=100,
                        height=100,
                        fit=ft.ImageFit.CONTAIN,
                        border_radius=ft.border_radius.all(5)),
                        
                        ft.Column(
                            controls=[
                                ft.Text(playlist_title, size=20,  weight=ft.FontWeight.BOLD),
                                ft.Text(playlist_owner),
                                ft.Text(f"{playlist_length} items", size = 14,  weight=ft.FontWeight.W_500)
                            ], expand=1, alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                        
                        ft.Container( #control 3
                            content=ft.Column(
                                controls=[
                                ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: individual_download(link)),
                                ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.Icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: remove_control(link))
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                                            ),
                                #alignment=ft.alignment.center_right  # Align container to the right
                                    ),   

                        ]),
                    width=700,
                    height=110,
                    padding=ft.Padding(left = 5, top = 5, bottom =5, right = 10),
                    border_radius=5,
                    bgcolor=preview_color,
                    alignment=ft.alignment.center))

    #add the newly created preview_tab        
    added_controls.append((unique_id, preview_tab))
    if preview_placeholder in lv.content.controls:
        lv.content.controls.remove(preview_placeholder)
    lv.content.controls.insert(0, preview_tab)


def main(page: ft.Page):
    page.window.width = 700
    page.window.height = 645
    page.window.min_width = 700
    page.window.min_height = 645
    page.window.max_width = 700
    page.window.max_height = 2560

    page.title = "yt-dlp_GUIv.0.7"   
    
    #pre-declaring some things because I dont know to how to code
    def draw_main_page():
        pass
    def on_download_client_choice():
        pass
    global update_status_bar, update_button_status, finished_status, cancelled_status, multiple_status, preview_placeholder, lv, link_entry, remove_control, individual_download, output_path, history, add_to_history, update_appearance_and_settings, downloading_settings

    #various status messages 
    preview_loading=ft.Container(ft.Row([ft.Text('Loading Preview...', size=16), ft.ProgressRing(color='green', width=30, height=30),],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=405, height=50, bgcolor=bg_color,padding=ft.Padding(left=10, top=5, right=10, bottom=5), border_radius=10,)
    finished_status=ft.Container(ft.Row([ft.Text('Finished.', size=16), ft.IconButton(icon=ft.Icons.CHECK, style=ft.ButtonStyle(color=main_color), disabled=True)],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=405, height=50, bgcolor=bg_color,padding=ft.Padding(left=10, top=5, right=10, bottom=5), border_radius=10,)
    preview_added=ft.Container(ft.Row([ft.Text('Link Already Entered.', size=16), ft.IconButton(icon=ft.Icons.LINK_OFF, style=ft.ButtonStyle(color=main_color), disabled=True),],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=405, height=50, bgcolor=bg_color,padding=ft.Padding(left=10, top=5, right=10, bottom=5), border_radius=10,)
    multiple_status = ft.Container(ft.Row([ft.Text(f'Downloading... {len(queue)} left', size=16), ft.Icon(name = ft.Icons.TIMELAPSE, color = ft.Colors.GREEN),],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=405, height=50, bgcolor=bg_color,padding=ft.Padding(left=10, top=5, right=10, bottom=5), border_radius=10)
    preview_invalid=ft.Container(ft.Row([ft.Text('Enter a Valid Link.', size=16), ft.IconButton(icon=ft.Icons.LINK_OFF, style=ft.ButtonStyle(color=main_color), disabled=True),],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=405, height=50, bgcolor=bg_color,padding=ft.Padding(left=10, top=5, right=10, bottom=5), border_radius=10,)
    cancelled_status=ft.Container(ft.Row([ft.Text('Canceled.', size=16, color = ft.Colors.GREY), ft.IconButton(icon=ft.Icons.CANCEL_ROUNDED, icon_color = ft.Colors.GREY, style=ft.ButtonStyle(color=main_color), disabled=True),],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=405, height=50, bgcolor=bg_color,padding=ft.Padding(left=10, top=5, right=10, bottom=5), border_radius=10,)

    #appearance stuff
    def update_appearance_and_settings(e):
        """this updates widgets to match new theme settings and 
        saves all configurations/settings to a json"""
        global secondary_color, bg_color, main_color, preview_color, auto_start, crop_thumbnails, client_id, client_secret, downloads_folder, open_console
        transparent_value =  appearance_settings.content.content.controls[1].content.controls[1].controls[1].value
        theme_selection = appearance_settings.content.content.controls[1].content.controls[0].controls[1].value
        client_id = spotify_api_settings.content.content.controls[1].content.controls[0].value
        client_secret = spotify_api_settings.content.content.controls[1].content.controls[1].value
        crop_thumbnails = downloading_settings.content.content.controls[1].content.controls[0].controls[1].value
        auto_start = downloading_settings.content.content.controls[1].content.controls[1].controls[1].value
        save_location = downloading_settings.content.content.controls[1].content.controls[3].controls[1].controls[0].value
        open_console = downloading_settings.content.content.controls[1].content.controls[2].controls[1].value
        #check what the screen transparency should be
        if transparent_value != 0:    
            page.window.opacity = transparent_value
        else:
            page.window.opacity = 1
        #check what theme is selected and change the Colors to correct values
        if theme_selection == True:
            page.theme_mode = 'dark'
            main_color = ft.Colors.GREEN
            secondary_color = ft.Colors.BLACK26
            bg_color = ft.Colors.BLACK12
            preview_color  = ft.Colors.BLACK54
            
        else:
            page.theme_mode = 'light'
            main_color = ft.Colors.BLUE
            secondary_color = ft.Colors.WHITE12
            bg_color = ft.Colors.WHITE12
            preview_color = ft.Colors.WHITE12

        #reassign all the controls with their new Colors
        for control in color_controls:
            if hasattr(control, 'style') and hasattr(control.style, 'color'):
                control.style.color = main_color
                control.style.bgcolor = secondary_color
            if hasattr(control, 'icon_color'):
                control.icon_color = main_color
            if hasattr(control, 'active_color'):
                control.active_color = main_color
            else:
                control.color = main_color
        for control in main_control_bar.content.content.controls:
            if hasattr(control, 'style') and hasattr(control.style, 'color'):
                control.style.bgcolor = secondary_color        
                clear_url_entry.style.bgcolor = secondary_color
            else:
                control.bgcolor = secondary_color
                
        preview_loading.content.controls[1].color = main_color
        finished_status.content.controls[1].style.color = main_color
        try:    
            for control in lv.content.controls:
                control.content.content.controls[2].content.controls[0].style.color = main_color
                control.content.bgcolor=preview_color
        except:
            pass
        settings_back_button.style.color = main_color
        settings_text.color = main_color
        spotify_api_settings.content.content.controls[0].color = main_color
        appearance_settings.content.content.controls[0].color = main_color
        appearance_settings.content.content.controls[1].content.controls[1].controls[1].active_color = main_color
        appearance_settings.content.content.controls[1].content.controls[0].controls[1].active_color = main_color
        downloading_settings.content.content.controls[0].color = main_color
        downloading_settings.content.content.controls[1].content.controls[1].controls[1].active_color = main_color
        downloading_settings.content.content.controls[1].content.controls[0].controls[1].active_color = main_color

        #save the settings in a json
        settings_config = {"theme": theme_selection, "transparency": transparent_value, "client_id": client_id, "client_secret": client_secret, "save_location": save_location, "auto_start": auto_start, "crop_thumbnails": crop_thumbnails, "open_console": open_console, 'history': saved_history_tabs}
        with open("yt-dlp_GUI_settings.json", mode="w", encoding="utf-8") as write_file:
            json.dump(settings_config, write_file, indent=4)

        #enables this function to run when its not called from the settings page (duh)
        if settings_page in page.controls:
            settings_page.update()
        page.update()

    def on_dialog_result(e: ft.FilePickerResultEvent):
        global downloads_folder
        if settings_page not in page.controls:    
            downloads_folder = e.path
            output_path.value=downloads_folder
            output_path.update()
        else:
            output_path.value = e.path
            downloading_settings.content.content.controls[1].content.controls[3].controls[1].controls[0].value = e.path
            downloading_settings.content.content.controls[1].content.controls[3].controls[1].controls[0].update()

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)
    page.update()
    
    #ui elements for download path stuff
    edit_path_button = ft.IconButton(icon=ft.Icons.EDIT, on_click=lambda _: file_picker.get_directory_path(), icon_color=main_color)
    output_path = ft.TextField(label="Output destination", read_only=True, value=downloads_folder, width='250')

    def on_format_select(e):
        if align_video_quality in row_4.controls:
            row_4.controls.remove(align_video_quality)
        if align_audio_quality in row_4.controls:
            row_4.controls.remove(align_audio_quality)
        if align_unselected_format in row_4.controls:
            row_4.controls.remove(align_unselected_format)     

        if format_choice.value in ['mp4', 'mkv', 'm4a', 'mp3']:
            embed_thumbnail.disabled = False
            embed_thumbnail.value = True
        else:
            embed_thumbnail.value = False
            embed_thumbnail.disabled = True
        if format_choice.value in ['mp4', 'mkv']:
            row_4.controls.append(align_video_quality)
            video_quality.disabled = False
        elif format_choice.value in ['m4a', 'mp3', 'opus', 'flac']:
            row_4.controls.append(align_audio_quality) 
            audio_quality.disabled = False
            if format_choice.value == "flac":
                audio_quality.disabled = True
        else:
            row_4.controls.append(align_unselected_format)
        page.update()
    
    #all the dropdown menus
    downloader = ft.Dropdown(
    options=[
        ft.dropdown.Option("Auto"),
        ft.dropdown.Option("Manual")], width="350", value='Auto', on_change=lambda e: on_download_client_choice())
    format_choice = ft.Dropdown(
    label="Format",
    options=[
        ft.dropdown.Option("mp4"),
        ft.dropdown.Option("mkv"),
        ft.dropdown.Option("m4a"),
        ft.dropdown.Option("mp3"),
        ft.dropdown.Option("opus")], on_change=on_format_select, width="350", disabled=True)
    audio_quality = ft.Dropdown(
    label="Bitrate",
    options=[
        ft.dropdown.Option("Best available quality"),
        ft.dropdown.Option("160 kbps"),
        ft.dropdown.Option("128 kbps"),
        ft.dropdown.Option("70 kbps")], width="350", disabled=True)
    video_quality = ft.Dropdown(
    label="Resolution",
    options=[
        ft.dropdown.Option("Best available quality"),
        ft.dropdown.Option("1080p"),
        ft.dropdown.Option("720p"),
        ft.dropdown.Option("480p")], width="350", disabled=True)
    format_unselected = ft.Dropdown(      
    label="Quality",
    options=[
        ft.dropdown.Option("select a format first")], width="350", disabled=True)
    auto_choice = ft.Dropdown(
    label="Download type",
    options=[
        ft.dropdown.Option("Audio+Video"),
        ft.dropdown.Option("Audio"),
        ], width="350", disabled=False)
    align_video_quality = ft.Container(
        content=video_quality,
        alignment=ft.alignment.center_right  # Aligns to the right
    )
    align_audio_quality = ft.Container(
        content=audio_quality,
        alignment=ft.alignment.top_right  # Aligns to the right
    )
    align_unselected_format = ft.Container(
        content=format_unselected,
        alignment=ft.alignment.top_right  # Aligns to the right
    )
    align_format_choice = ft.Container(
        content=format_choice,
        alignment=ft.alignment.top_right  # Aligns to the right
    )
    
    #this goes in lv when item_list is empty
    preview_placeholder = ft.Card(
        content=ft.Container(
            content=ft.Text("Download previews will appear here."),
            width=700,
            height=290,
            padding=0,
            border_radius=5,
            bgcolor=ft.Colors.BLACK54,
            alignment=ft.alignment.center,
            expand=True
            ))

    #example song preview
    preview_tab_example = ft.Card(
        content=ft.Container(
            content=ft.Row(
                controls=[
                ft.Image( #control 1
                src='https://i.scdn.co/image/ab67616d0000b273255e131abc1410833be95673',
                width=100,
                height=100,
                fit=ft.ImageFit.CONTAIN,
                border_radius=ft.border_radius.all(5)
                        ),
                
                ft.Column( #control 2
                    controls=[
                        ft.Text("Never Gonna give You Up", size=20,  weight=ft.FontWeight.BOLD),
                        ft.Text("Rick Astley • Whenever You Need Somebody"),
                        ft.Text("3:33 - 5.12 MB", size = 14,  weight=ft.FontWeight.W_500)
                            ], expand = 1, alignment=ft.MainAxisAlignment.SPACE_EVENLY
                        ),
                ft.Container( #control 3
                    content=ft.Column(
                        controls=[
                        ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='green', icon =ft.Icons.SAVE, height = 40, width = 150),
                        ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.Icons.DELETE,  height = 40, width = 150)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_EVENLY
                                    ),
                        #alignment=ft.alignment.center_right  # Align container to the right
                            ),   
                        
                        ],
                        ),
                        
            width=700,
            height=110,
            padding=ft.Padding(left = 5, top = 5, bottom =5, right = 10),
            border_radius=5,
            bgcolor=ft.Colors.BLACK54,
            alignment=ft.alignment.center))
    
    #this listview holds all the song previews
    lv = ft.Card(content=ft.ListView(spacing=1, padding=5, auto_scroll=False, expand=True),height=200, expand=True)
    lv.content.controls.append(preview_placeholder)
    #lv.controls.append(preview_tab_example)
    
    #this is the stuff shown to display terminal/cmd output of yt-dlp/spotdl
    history_spacer = ft.Container(ft.Row(expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=380, height=50, padding=ft.Padding(left=10, top=0, right=10, bottom=5))
    history_text=ft.Text('Previous Downloads', color=main_color, weight=ft.FontWeight.BOLD, size=20)
    history=ft.Card(content=ft.ListView(spacing=1, padding=5, auto_scroll=False, expand=True), expand=True)
    history_back_button = ft.IconButton(height="50", width=50, icon=ft.Icons.ARROW_BACK, style=ft.ButtonStyle(color=main_color), on_click=lambda e: draw_main_page())
    history_page = ft.Container(content=ft.Column([ft.Row([history_back_button, history_spacer, history_text,],alignment=ft.MainAxisAlignment.SPACE_BETWEEN, height=50),history], expand = True), padding=ft.Padding(left=5, top=5, right=5, bottom=5),width=700, expand=True)

    #load the download history
    for item in saved_history_tabs:
        history_tab = ft.Card(content=ft.Container(content=ft.Row(controls=[ft.Row([ft.Image(src=saved_history_tabs[item][0],width=60,height=60,fit=ft.ImageFit.CONTAIN,border_radius=ft.border_radius.all(5)),ft.Column(controls=[ft.Text(saved_history_tabs[item][1], size=20), ft.Text(f"{saved_history_tabs[item][2]} - {saved_history_tabs[item][3]}")])]),ft.ElevatedButton("Copy link", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.COPY, height = 60, width = 130, on_click=lambda e, link=item: pyperclip.copy(link))],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),padding=10, bgcolor=secondary_color,))            
        history.content.controls.insert(0, history_tab)

    add_metadata = ft.Switch(label="  Include metadata", active_color=main_color, value=True)
    embed_thumbnail = ft.Switch(label="  Embed thumbnail/album art", active_color=main_color, value=True, on_change=lambda e: page.update())
    link_entry = ft.TextField(label="song, album, playlist, or video", width="470", height='50')
    url_text = ft.Text(value=" URL:", color=main_color, weight=ft.FontWeight.BOLD, size=15)
    
    #settings stuff here
    settings_spacer = ft.Container(ft.Row(expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=500, height=50, padding=ft.Padding(left=10, top=0, right=10, bottom=5))
    settings_text=ft.Text('Settings', color=main_color, weight=ft.FontWeight.BOLD, size=20)
    settings_list=ft.Card(content=ft.ListView(spacing=1, padding=5, auto_scroll=False, expand=True), expand=True)
    settings_back_button = ft.IconButton(height="50", width=50, icon=ft.Icons.ARROW_BACK, style=ft.ButtonStyle(color=main_color), on_click=lambda e: draw_main_page())
    settings_page = ft.Container(content=ft.Column([ft.Row([settings_back_button, settings_spacer, settings_text,],alignment=ft.MainAxisAlignment.SPACE_BETWEEN, height=50),settings_list], expand = True), padding=ft.Padding(left=5, top=5, right=5, bottom=5),width=700, expand=True)
    
    spotify_api_settings = ft.Card(content=ft.Container(content=ft.Column([ft.Text(' Spotify API Credentials', color=main_color, theme_style=ft.TextThemeStyle.TITLE_MEDIUM), ft.Container(content=ft.Column(controls=[ft.TextField(label='Client ID', value=client_id), ft.TextField(label='Client Secret', value=client_secret)] ), padding=ft.Padding(left=0, top=10, right=0, bottom=0)) ], width=700,), padding=10, ))
    appearance_settings = ft.Card(ft.Container(ft.Column([ft.Text(' Appearance:', color=main_color, theme_style=ft.TextThemeStyle.TITLE_MEDIUM), ft.Container(ft.Column([ft.Row([ft.Text('Dark Mode: ', theme_style=ft.TextThemeStyle.TITLE_SMALL),ft.Switch( active_color=main_color, value=theme_setting, on_change=update_appearance_and_settings)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), ft.Row([ft.Text('Transparency: ', theme_style=ft.TextThemeStyle.TITLE_SMALL),ft.Slider(min=0, max=100, divisions=10, label="{value}%", active_color=main_color, on_change=update_appearance_and_settings, value=transparency_setting)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN) ]), padding=ft.Padding(left=5, top=5, right=0, bottom=0))]), padding=10))
    downloading_settings = ft.Card(ft.Container(ft.Column([ft.Text(' Downloading:', color=main_color, theme_style=ft.TextThemeStyle.TITLE_MEDIUM), ft.Container(ft.Column([
        ft.Row([ft.Text(' Crop Thumbnails to 1:1: ', theme_style=ft.TextThemeStyle.TITLE_SMALL),ft.Switch( active_color=main_color, value=crop_thumbnails, on_change=update_appearance_and_settings)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([ft.Text(' Auto-start downloads: ', theme_style=ft.TextThemeStyle.TITLE_SMALL),ft.Switch( active_color=main_color, value=auto_start, on_change=update_appearance_and_settings)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([ft.Text(' Open a console window for each download: ', theme_style=ft.TextThemeStyle.TITLE_SMALL),ft.Switch( active_color=main_color, value=open_console, on_change=update_appearance_and_settings)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([ft.Text(' Default save location: ', theme_style=ft.TextThemeStyle.TITLE_SMALL), ft.Row([ft.TextField(label="Output destination", read_only=True, value=downloads_folder, width='250', height = '45'), edit_path_button])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ]))], ),padding=10))
    
    settings_list.content.controls.append(appearance_settings)
    settings_list.content.controls.append(downloading_settings)
    settings_list.content.controls.append(spotify_api_settings)
    
    #compiles the command to be used in subprocess.run based on user choices
    def compile_command(link):
        format_selection = format_choice.value
        downloader_selection = downloader.value
        audio_quality_selection = audio_quality.value
        video_quality_selection = video_quality.value
        embed_thumbnail_selection = embed_thumbnail.value
        add_metadata_selection = add_metadata.value
        
        if 'spotify' in link:
            command = ['spotdl', '--output', downloads_folder, link]
        else:
            command = ['yt-dlp', '-o', os.path.join(downloads_folder, '%(title)s.%(ext)s')]
            if embed_thumbnail_selection == True:
                command += ['--embed-thumbnail']
            if add_metadata_selection == True:
                command += ['--add-metadata']
            if crop_thumbnails == True:
                command += ['--ppa', "EmbedThumbnail+ffmpeg_o:-c:v mjpeg -vf crop='if(gt(ih,iw),iw,ih)':'if(gt(iw,ih),ih,iw)'"]
            if downloader_selection == 'Manual':
                if format_selection in  ['mp4', 'mkv', ' ', '']: #video formats
                    command += ['--merge-output-format', format_selection]
                    if video_quality_selection == '1080p':
                        command += ['-f', '137+bestaudio']
                    elif video_quality_selection == '720p':
                        command += ['-f', '136+bestaudio']
                    elif video_quality_selection == '480p':
                        command += ['-f', '135+bestaudio']
                    elif video_quality_selection == '360p':
                        command += ['-f', '134+bestaudio']
                    else:
                        command += ['-f', 'bestvideo+bestaudio']
                else: #audio only formats
                    command += ['-x', '--audio-format', format_selection]
                    if audio_quality_selection == '128 kbps':
                        command += ['--audio-quality', '128k']
                    elif audio_quality_selection == '160 kbps':
                        command += ['--audio-quality', '160k']
                    elif audio_quality_selection == '70 kbps':
                        command += ['--audio-quality', '70k']
                    else:
                        pass
            else: #auto mode
                if auto_choice.value == 'Audio':
                    command += ['-x', '--audio-format', 'm4a']
                if auto_choice.value == 'Audio+Video':
                    pass
        command += [link]
        return command
    
    #determines the type of entered link and creates and adds the preview to lv
    def create_preview(e):
        global added_controls, auto_start
        for tup in added_controls:
            if link_entry.value.strip() in tup:
                update_status_bar(preview_added)
                return
        if link_entry.value == '' or link_entry.value == ' ' or all(tld not in link_entry.value for tld in tlds):
            update_status_bar(preview_invalid)
            print('not a valid link')
            return
        update_button_status("uh", "loading_preview")
        update_status_bar(preview_loading)

        item_list.append(link_entry.value.strip())
        #print(item_list)
        try:
            if 'spotify' in link_entry.value:
                spotify_link()
            else:
                youtube_link()
        except:
            unique_id=link_entry.value
            print('preview unavailable or failed.')
            preview_tab = ft.Card( #the fallback_preview
            content=ft.Container(
            content=ft.Row(
                controls=[
                ft.Text(''),
                
                ft.Column( #control 2
                    controls=[
                        ft.Text(link_entry.value.strip(), size=14,  weight=ft.FontWeight.BOLD),
                        ft.Text("Preview Unavailable", size=10,  weight=ft.FontWeight.BOLD)
                            ], expand = 1, alignment=ft.MainAxisAlignment.SPACE_EVENLY
                        ),
                ft.Container( #control 3
                    content=ft.Column(
                        controls=[
                        ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: individual_download(link)),
                        ft.ElevatedButton(text="Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.Icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: remove_control(link))
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_EVENLY
                                    ),
                        #alignment=ft.alignment.center_right  # Align container to the right
                            ),   
                        
                        ],
                        ),
                        
            width=700,
            height=110,
            padding=ft.Padding(left = 15, top = 5, bottom =5, right = 10),
            border_radius=5,
            bgcolor=bg_color,
            alignment=ft.alignment.center))

            added_controls.append((link_entry.value.strip(), preview_tab))
            if preview_placeholder in lv.content.controls:
                lv.content.controls.remove(preview_placeholder)
            lv.content.controls.insert(0, preview_tab)
        if auto_start == True:
            queue.append(link_entry.value.strip())
            item_list.remove(link_entry.value.strip())
            page.update()
            return
        update_status_bar(finished_status)
        update_button_status("uh", "finished_loading_preview")
        page.update()

    #clears the url entry bar (link_entry)
    def clear_url(e):
        link_entry.value = ''
        link_entry.update()

    #shows download history
    def show_history(e):
        for control in page.controls[:]:
            page.remove(control)
        #draw the settings page
        page.add(history_page)
        page.update()

    #adds item to the history log
    def add_to_history(link):
        global history
        saved_history_tabs[link] = history_tabs[link]
        history_tab = ft.Card(content=ft.Container(content=ft.Row(controls=[ft.Row([ft.Image(src=history_tabs[link][0],width=60,height=60,fit=ft.ImageFit.CONTAIN,border_radius=ft.border_radius.all(5)),ft.Column(controls=[ft.Text(history_tabs[link][1], size=20), ft.Text(f"{history_tabs[link][2]} - {history_tabs[link][3]}")])]),ft.ElevatedButton("Copy link", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color=main_color, icon =ft.Icons.COPY, height = 60, width = 130, on_click=lambda e, link=link: pyperclip.copy(link))],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),padding=10, bgcolor=secondary_color,))            
        history.content.controls.insert(0, history_tab)

        with open("yt-dlp_GUI_settings.json", "r") as f:
            data = json.load(f)
        data['history'][link] = history_tabs[link]
        with open("yt-dlp_GUI_settings.json", "w") as f:    
            json.dump(data, f, indent=4)

    #shows the settings
    def settings(e):
        #clear the whole window
        for control in page.controls[:]:
            page.remove(control)
        #draw the settings page
        page.add(settings_page)
        page.update()
    
    #removes an individual selected preview
    def remove_control(link):
        global item_list
        for i, (uid, control) in enumerate(added_controls):
            if uid == link:
                if control.content.content.controls[2].content.controls[1].text == "cancel":
                    flags[link] = False
                    return
                added_controls.pop(i)
                lv.content.controls.remove(control)  
                lv.update()
        item_list = [item for item in item_list if item != link.strip()]
        print(item_list)
        
        if len(lv.content.controls) < 1:
            item_list = []
            lv.content.controls.append(preview_placeholder)
        page.update()

    #clears all previews from lv
    def remove_all_previews(e):
        global item_list
        global added_controls
        global queue
        delete_all_button = main_control_bar.content.content.controls[1]
        if delete_all_button.icon == ft.Icons.CANCEL:
            for link in queue:
                flags[link] = False
            delete_all_button.icon = ft.Icons.DELETE_FOREVER
            main_control_bar.update()
            return
        
        for control in lv.content.controls[:]:
            lv.content.controls.remove(control)  
            lv.update()
            time.sleep(.1)
        lv.content.controls.append(preview_placeholder)
        lv.update()
        item_list = []
        added_controls = []   
        queue = []

    #runs on_download for the selected item
    def individual_download(link):        
        if link in item_list:
            queue.append(link)
            item_list.remove(link)
        
    #this runs when the download_all button is pressed, runs on_download for each link in item_list
    def download_all(e):
        for item in item_list:
            queue.append(item)
        item_list.clear()

    #this disables configuration options if the 'Auto' choice is selected
    def on_download_client_choice():  
        if downloader.value == 'Auto':
            format_choice.disabled = True
            audio_quality.disabled = True
            video_quality.disabled = True
            format_unselected.disabled = True
            del row_4.controls[1]
            del row_3.controls[1]
            row_4.controls.append(align_unselected_format)       
            row_3.controls.append(auto_choice)
        else:
            format_choice.disabled = False
            audio_quality.disabled = False
            video_quality.disabled = False
            format_unselected.disabled = False
            del row_3.controls[1]
            del row_4.controls[1]
            row_4.controls.append(align_unselected_format)
            row_3.controls.append(align_format_choice)

        page.update()
        
    add_button = ft.IconButton( height="50", width='50', icon=ft.Icons.ADD_LINK, tooltip='Add To Queue', style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),bgcolor=secondary_color, color=main_color), on_click=create_preview)
    clear_url_entry = ft.IconButton( icon=ft.Icons.CLEAR, height="50",width=50, style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),bgcolor=secondary_color, color='grey'), on_click=clear_url)
    main_control_bar = ft.Card(content=ft.Container(content=ft.Row([ft.IconButton( height="50", width=50, icon=ft.Icons.DOWNLOADING_ROUNDED,  style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5), bgcolor=secondary_color,color=main_color,), tooltip='Download All', on_click=download_all), ft.IconButton(height="50", width=50, icon=ft.Icons.DELETE_FOREVER, style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5), bgcolor=secondary_color,color=ft.Colors.GREY,), tooltip='Clear All', on_click=remove_all_previews), ft.Container(ft.Row([],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN), width=405, height=50, bgcolor=bg_color, padding=ft.Padding(left=10, top=5, right=10, bottom=5), border_radius=10,), ft.IconButton( height="50", width=50,icon=ft.Icons.SETTINGS, style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5), bgcolor=secondary_color,color=ft.Colors.GREY,), tooltip='Settings',on_click=settings), ft.IconButton( height="50",width=50, icon=ft.Icons.HISTORY_ROUNDED,  style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5), bgcolor=secondary_color,color=main_color,), tooltip='Download History', on_click=show_history),], width=700, height=50), padding=ft.Padding(left=5, top=5, right=5, bottom=5)))
    row_1 = ft.Card(content=ft.Container(content=ft.Row(controls=[
            url_text, 
            link_entry, clear_url_entry,
            add_button], alignment=ft.MainAxisAlignment.SPACE_EVENLY,  height='50', ),padding=ft.Padding(left=0, top=5, right=0, bottom=5) ))
    row_2 = ft.Row(controls=[
            edit_path_button,
            output_path,
            downloader], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    row_3 = ft.Row(controls=[
            add_metadata,
            auto_choice
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    row_4 = ft.Row(controls=[
        embed_thumbnail,
        align_unselected_format
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    #list of controls that have a specified color
    color_controls = [url_text, add_button, edit_path_button, embed_thumbnail, add_metadata, 
                    main_control_bar.content.content.controls[0], 
                    main_control_bar.content.content.controls[4]]
    
    #adds all the ui elements to the page
    def draw_main_page():    
        e=0
        update_appearance_and_settings(e)
        for control in page.controls[:]:
            page.remove(control)
        page.add(row_1, row_2, row_3, row_4, lv, main_control_bar,)
        if len(queue) == 0:
            main_control_bar.content.content.controls.pop(2)
            main_control_bar.content.content.controls.insert(2, ft.Container(ft.Row([],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=405, height=50, bgcolor=bg_color,padding=ft.Padding(left=10, top=5, right=10, bottom=5), border_radius=10))
            main_control_bar.update()
        page.update()
    
    def update_status_bar(status):
        try:
            #all this does is check if there is the "multiple status" already in the status bar, if so it just updates the text instead of replacing the whole control
            if "left" in main_control_bar.content.content.controls[2].content.controls[0].value and "left" in status.content.controls[0].value:
                print(main_control_bar.content.content.controls[2].content.controls[0].value)
                main_control_bar.content.content.controls[2].content.controls[0].value = f'Downloading... {len(queue)} left'
                main_control_bar.update()
                return
        except:
            pass
        main_control_bar.content.content.controls.pop(2)
        main_control_bar.content.content.controls.insert(2, status)
        try:
            main_control_bar.update()
        except:
            pass 

    def update_button_status(control, status):
        download_all_button = main_control_bar.content.content.controls[0]
        delete_all_button = main_control_bar.content.content.controls[1]
        download_all_button.disabled = False
        delete_all_button.disabled = False
        try:
            download_button = control.content.content.controls[2].content.controls[0]
            delete_button = control.content.content.controls[2].content.controls[1]
        except: 
            print("updating buttons in status bar")
        if status == "disabled":
            download_button.disabled = True
            delete_button.disabled = False
            try:
                control.update()
            except:
                print("settings open probably")
        if status == "finished":
            download_button.text = "Finished"
            download_button.icon = ft.Icons.CHECK
            delete_button.text = "remove"
            delete_button.icon = ft.Icons.DELETE_FOREVER
            download_all_button.disabled = False
            delete_all_button.disabled = False
            delete_all_button.icon = ft.Icons.DELETE_FOREVER
            delete_button.disabled = False
            try:
                delete_all_button.update()
                download_all_button.update()
                download_button.update()
                delete_button.update()
                control.update()
            except:
                print("settings open probably")
        if status == "downloading":
            download_button.text = "Downloading"
            download_button.icon = None
            delete_button.text = "cancel"
            delete_button.icon = ft.Icons.CANCEL
            download_all_button.disabled = True
            delete_all_button.disabled = False
            delete_all_button.icon = ft.Icons.CANCEL
            delete_all_button.icon_color = ft.Colors.GREY
            try:
                delete_all_button.update()
                download_all_button.update()
                control.update()
            except:
                print("settings open probably")
        if status == "loading_preview":
            download_all_button.disabled = False
            delete_all_button.disabled = False
        if status == "finished_loading_preview":
            print("finished loading preview")
            download_all_button.disabled = False
            delete_all_button.disabled = False
        if status == "canceled":
            time.sleep(.1)
            download_button.text = "Download"
            download_button.text_color = ft.Colors.GREEN
            download_button.icon = ft.Icons.SAVE
            download_button.icon_color = ft.Colors.GREEN
            delete_button.text = "Remove"
            delete_button.icon = ft.Icons.DELETE_FOREVER
            download_all_button.disabled = False
            delete_all_button.disabled = False
            delete_button.disabled = False
            download_button.disabled = False
            delete_all_button.icon = ft.Icons.DELETE_FOREVER
            try:
                delete_all_button.update()
                download_all_button.update()
                control.update()
            except:
                print("settings open probably")
    
    def monitor_queue():
        global download_threads
        
        download_threads = {}
        while True:
            if len(queue) != 0:
                for item in queue:
                    if item not in download_threads:
                        for i, (uid, control) in enumerate(added_controls):
                            if uid == item:
                                flags[item] = True
                                command = compile_command(item)
                                update_button_status(control, "downloading")
                                download_threads[item] = threading.Thread(target=download_container, args=(item, control, command, open_console))
                                download_threads[item].start()      
                                update_button_status(control, "disabled")
            if len(download_threads) != 0:
                multiple_status = ft.Container(ft.Row([ft.Text(f'Downloading... {len(queue)} left', size=16), ft.ProgressRing(color=main_color, width=30, height=30),],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=405, height=50, bgcolor=bg_color,padding=ft.Padding(left=10, top=5, right=10, bottom=5), border_radius=10)
                update_status_bar(multiple_status)
            if len(finished_threads) != 0:
                for item in finished_threads.copy():
                    update_button_status(finished_threads[item], "finished")
                    update_button_status(control, "disabled")
                    finished_threads.pop(item, None)
                    
            time.sleep(0.1)
    queue_checker = threading.Thread(target=monitor_queue, args=())
    queue_checker.start()
    
    draw_main_page()

def download_container(link, control, command, open_console):
    global queue
    global download_threads
    global finished_threads
   
    p1 = Process(target=download, args=(command, open_console))
    p1.start()

    while p1.is_alive():
        if flags.get(link) == False:
            p1.terminate()
            p1.join()
            update_button_status(control, "canceled")
            queue.remove(link)
            download_threads.pop(link, None)
            flags.pop(link, None)
            item_list.append(link)
            if len(queue) == 0:
                update_status_bar(cancelled_status)
            return
        time.sleep(0.1)

    queue.remove(link)
    download_threads.pop(link, None)
    finished_threads[link] = control
    add_to_history(link)
    update_appearance_and_settings(0)

    if len(queue) == 0:
        update_status_bar(finished_status,)
        return

def download(command, console):
    if console == True:
       result = subprocess.run(command, text=True, check=True)  
    else:
        result = subprocess.run(command, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result)
    
if __name__ == "__main__":    
    ft.app(target=main)
