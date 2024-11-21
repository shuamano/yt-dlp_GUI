#v.0.5 11/20/24 11:20 pm FAKECOPYRIGHT Shua Manory
import flet as ft
import subprocess
import os
import requests
from base64 import b64encode
import yt_dlp
from humanfriendly import format_timespan, format_size
import time

home_dir = os.path.expanduser("~")
downloads_folder = os.path.join(home_dir, "Downloads")
download_command_line = ""
si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
CREATE_NO_WINDOW = 0x08000000

#spotify api stuff
client_id = '0cc3fdffe0f84a1c80a2b2cdf4df1390'
client_secret = 'e60c4550c2fd442ebebb8c7b3fbdd4fa'

#add every link to this list, download them all when selected, then clear it
song_list = []
number_of_songs = 0
added_controls = []



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

token_response = get_client_credentials_token(client_id, client_secret)
access_token = token_response

def spotify_link():
    global added_controls
    global number_of_songs
    global song_list
    unique_id = link_entry.value

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
                            ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='green', icon =ft.icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value,  id=unique_id: indivudual_download(link)),
                            ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value,  id=unique_id: remove_control(link))
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
                bgcolor=ft.colors.BLACK54,
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
                            ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='green', icon =ft.icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value,  id=unique_id: indivudual_download(link)),
                            ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value,  id=unique_id: remove_control(link))
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
                bgcolor=ft.colors.BLACK54,
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
                            ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='green', icon =ft.icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value,  id=unique_id: indivudual_download(link)),
                            ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value,  id=unique_id: remove_control(link))
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
                bgcolor=ft.colors.BLACK54,
                alignment=ft.alignment.center))
        
    added_controls.append((unique_id, preview_tab))
    if preview_placeholder in lv.content.controls:
        lv.content.controls.remove(preview_placeholder)
    lv.content.controls.insert(0, preview_tab)

def youtube_link():
    global added_controls
    global number_of_songs
    global song_list
    unique_id = link_entry.value
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
                                ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='green', icon =ft.icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: indivudual_download(link)),
                                ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: remove_control(link))
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
                    bgcolor=ft.colors.BLACK54,
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
                                ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='green', icon =ft.icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: indivudual_download(link)),
                                ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: remove_control(link))
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
                    bgcolor=ft.colors.BLACK54,
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
                                    ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='green', icon =ft.icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: indivudual_download(link)),
                                    ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: remove_control(link))
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
                        bgcolor=ft.colors.BLACK54,
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
                                ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='green', icon =ft.icons.SAVE, height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: indivudual_download(link)),
                                ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.icons.DELETE,  height = 40, width = 150, on_click=lambda e, link=link_entry.value, id=unique_id: remove_control(link))
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
                    bgcolor=ft.colors.BLACK54,
                    alignment=ft.alignment.center))

    #add the newly created preview_tab        
    added_controls.append((unique_id, preview_tab))
    if preview_placeholder in lv.content.controls:
        lv.content.controls.remove(preview_placeholder)
    lv.content.controls.insert(0, preview_tab)

def main(page: ft.Page):
    page.window.width = 700
    page.window.height = 600
    page.window.min_width = 700
    page.window.min_height = 600
    page.window.max_width = 700
    page.window.max_height = 2560

    page.title = "yt-dlp_GUI3 (©️ Mauhs lol)"
    page.icon = "C:/Users/shuam/Downloads/yt_dlp_GUI2_icon.png"       
    #page.window.opacity = 0.95
    
    global draw_main_page
    def draw_main_page():
        pass
    def on_download_client_choice():
        pass

    def on_dialog_result(e: ft.FilePickerResultEvent):
        global downloads_folder
        downloads_folder = e.path
        output_path.value=downloads_folder
        output_path.update()

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)
    page.update()
    
    edit_path_button = ft.IconButton(icon=ft.icons.EDIT, on_click=lambda _: file_picker.get_directory_path(), icon_color='green')
    output_path = ft.TextField(label="Output destination", read_only=True, value=downloads_folder, width='250')

    def on_format_select(e):
        if align_video_quality in row_4.controls:
            row_4.controls.remove(align_video_quality)
        if align_audio_quality in row_4.controls:
            row_4.controls.remove(align_audio_quality)
        if align_unselected_quality in row_4.controls:
            row_4.controls.remove(align_unselected_quality)     

        if format_choice.value == "mp4":
            row_4.controls.append(align_video_quality)
            video_quality.disabled = False
        elif format_choice.value in ['m4a', 'mp3', 'flac', 'opus']:
            row_4.controls.append(align_audio_quality) 
            audio_quality.disabled = False
        else:
           row_4.controls.append(align_unselected_quality)
        page.update()
    
    downloader = ft.Dropdown(
    label="Downloader Client",
    options=[
        ft.dropdown.Option("Auto"),
        ft.dropdown.Option("yt-dlp"),
        ft.dropdown.Option("spotdl")], width="350", value='Auto', on_change=lambda e: on_download_client_choice())
       
    format_choice = ft.Dropdown(
    label="Codec",
    options=[
        ft.dropdown.Option("mp4"),
        ft.dropdown.Option("mp3"),
        ft.dropdown.Option("m4a"),
        ft.dropdown.Option("opus"),
        ft.dropdown.Option("flac")], on_change=on_format_select, width="350", disabled=True)

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
        ft.dropdown.Option("480p"),
        ft.dropdown.Option("480p")], width="350", disabled=True)

    format_unselected = ft.Dropdown(      
    label="Select quality",
    options=[
        ft.dropdown.Option("select a format first")], width="350", disabled=True)

    global preview_placeholder
    preview_placeholder = ft.Card(
        content=ft.Container(
            content=ft.Text("Download previews will appear here."),
            width=700,
            height=290,
            padding=0,
            border_radius=5,
            bgcolor=ft.colors.BLACK54,
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
                        ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='green', icon =ft.icons.SAVE, height = 40, width = 150),
                        ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.icons.DELETE,  height = 40, width = 150)
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
            bgcolor=ft.colors.BLACK54,
            alignment=ft.alignment.center))
    
    global lv
    lv = ft.Card(content=ft.ListView(spacing=1, padding=5, auto_scroll=False, expand=True),height=200, expand=True)
    lv.content.controls.append(preview_placeholder)
    #lv.controls.append(preview_tab_example)
    terminal = ft.Card(content=ft.ListView(spacing=1, padding=5, auto_scroll=True, expand=False, height='50'))
    

    align_video_quality = ft.Container(
        content=video_quality,
        alignment=ft.alignment.center_right  # Aligns to the right
    )
    align_audio_quality = ft.Container(
        content=audio_quality,
        alignment=ft.alignment.top_right  # Aligns to the right
    )
    align_unselected_quality = ft.Container(
        content=format_unselected,
        alignment=ft.alignment.top_right  # Aligns to the right
    )
    align_format_choice = ft.Container(
        content=format_choice,
        alignment=ft.alignment.top_right  # Aligns to the right
    )
      
    add_metadata = ft.Switch(label="  Include metadata", active_color='green', value=True)
    embed_thumbnail = ft.Switch(label="  Embed thumbnail/album art", active_color='green', value=True)
    global link_entry
    link_entry = ft.TextField(label="song, album, playlist, or video", width="470", height='50')
    
    settings_text=ft.Text('Settings', color="green", weight=ft.FontWeight.BOLD, size=20)
    settings_list=ft.ListView(spacing=1, padding=5, auto_scroll=False, expand=True)
    settings_back_button = ft.IconButton(height="50", width=50, icon=ft.icons.ARROW_BACK, style=ft.ButtonStyle(color=ft.colors.GREEN), on_click=lambda e: draw_main_page())
    settings_page = ft.Container(content=ft.Column([ft.Row([settings_back_button, settings_text,],alignment=ft.MainAxisAlignment.SPACE_BETWEEN, height=50), settings_list]), padding=ft.Padding(left=5, top=5, right=15, bottom=5),width=700)
    
    finished_status=ft.Container(ft.Row([ft.Text('Finished.', size=16), ft.IconButton(icon=ft.icons.CHECK, style=ft.ButtonStyle(color=ft.colors.GREEN), disabled=True)],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=405, height=50, bgcolor=ft.colors.BLACK12,padding=ft.Padding(left=10, top=5, right=10, bottom=5))

    global on_download
    def on_download(link):
        global download_command_line 
        format_selection = format_choice.value
        downloader_selection = downloader.value
        audio_quality_selection = audio_quality.value
        video_quality_selection = video_quality.value
        embed_thumbnail_selection = embed_thumbnail.value
        add_metadata_selection = add_metadata.value
        #client choice
        if downloader_selection == 'spotdl':
            if format_selection == 'm4a':
                download_command_line += '--format m4a '
            elif format_selection == 'mp3':
                download_command_line += '--format mp3 '
            elif format_selection == 'flac':
                download_command_line += '--format flac '
            elif format_selection == 'opus':
                download_command_line += '--format opus '
            else:
                pass
            if audio_quality_selection == '128 kbps':
                download_command_line += '--bitrate 128K '
            elif audio_quality_selection == '160 kbps':
                download_command_line += '--bitrate 160K '
            elif audio_quality_selection == '80 kbps':
                download_command_line += '--bitrate 80K '
            else:
                pass
            subprocess.call(f'spotdl {download_command_line} --output {downloads_folder} {link}',  shell=True, text=True)
            return
        
        if downloader_selection == 'yt-dlp':
            #format choice
            if format_selection == 'mp4':
                download_command_line += '--merge-output-format mp4 '
            elif format_selection == 'm4a':
                download_command_line += '-x --audio-format m4a '
            elif format_selection == 'mp3':
                download_command_line += '-x --audio-format mp3 '
            elif format_selection == 'flac':
                download_command_line += '-x --audio-format flac '
            elif format_selection == 'opus':
                download_command_line += '-x --audio-format opus '
            else:
                pass
        
            #video quality choice
            if video_quality_selection == '1080p':
                download_command_line += '-f 137+bestaudio '
            elif video_quality_selection == '720p':
                download_command_line += '-f 136+bestaudio '
            elif video_quality_selection == '480p':
                download_command_line += '-f 135+bestaudio '
            elif video_quality_selection == '360p':
                download_command_line += '-f 134+bestaudio '
            else:
                pass

            #audio quality choice
            if audio_quality_selection == '128 kbps':
                download_command_line += '--audio-quality 128K '
            elif audio_quality_selection == '160 kbps':
                download_command_line += '--audio-quality 160K '
            elif audio_quality_selection == '70 kbps':
                download_command_line += '--audio-quality 70K '
            else:
                pass
            if add_metadata_selection == True:
                download_command_line += '--add-metadata '
            if embed_thumbnail_selection == True:
                download_command_line += '--embed-thumbnail '
            else:
                pass
            subprocess.call(f'yt-dlp {download_command_line} -P {downloads_folder} {link}',  shell=True, text=True)
            return
        else:
            if 'music' in link or 'spotify' in link:
                subprocess.call(f'spotdl --output {downloads_folder} {link}',  shell=True, text=True)
            else:
                subprocess.call(f'yt-dlp -P {downloads_folder} --add-metadata {link}',  shell=True, text=True)
        
        print(download_command_line)
        download_command_line = ''
    
    def show_previews(e):
        preview_status=ft.Container(ft.Row([ft.Text('Loading Preview...', size=16), ft.ProgressRing(color='green', width=30, height=30),],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=405, height=50, bgcolor=ft.colors.BLACK12,padding=ft.Padding(left=10, top=5, right=10, bottom=5))
        main_control_bar.content.content.controls.pop(2)
        main_control_bar.content.content.controls.insert(2, preview_status)
        main_control_bar.update()
        if link_entry.value.strip() in song_list or link_entry.value == ' ':
            return
        song_list.append(link_entry.value.strip())
        #print(song_list)
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
                        ft.ElevatedButton("Download", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='green', icon =ft.icons.SAVE, height = 40, width = 150,on_click=lambda e, link=link_entry.value, id=unique_id: indivudual_download(link)),
                        ft.ElevatedButton("Remove  ", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), color='grey', icon =ft.icons.DELETE,  height = 40, width = 150,on_click=lambda e, link=link_entry.value, id=unique_id: remove_control(link))
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
            bgcolor=ft.colors.BLACK54,
            alignment=ft.alignment.center))

            added_controls.append((link_entry.value.strip(), preview_tab))
            if preview_placeholder in lv.content.controls:
                lv.content.controls.remove(preview_placeholder)
            lv.content.controls.insert(0, preview_tab)

        main_control_bar.content.content.controls.remove(preview_status)
        main_control_bar.content.content.controls.insert(2, finished_status)
        main_control_bar.update()
        page.update()

    def clear_url(e):
        link_entry.value = ''
        link_entry.update()

    def show_terminal(e):
        if terminal in page.controls:
            page.controls.remove(terminal)
            page.update()
        else:
            page.controls.insert(-1, terminal)
            page.update()

    def settings(e):
        for control in page.controls[:]:
            page.remove(control)
        page.add(settings_page)
        page.update()

    global remove_control
    def remove_control(link):
        global song_list
        for i, (uid, control) in enumerate(added_controls):
            if uid == link:
                added_controls.pop(i)
                lv.content.controls.remove(control)  
                lv.update()
        song_list = [item for item in song_list if item != link.strip()]
        print(song_list)
        
        if len(lv.content.controls) < 1:
            song_list = []
            lv.content.controls.append(preview_placeholder)
        page.update()

    def remove_all_previews(e):
        global song_list
        global added_controls
        for control in lv.content.controls[:]:
            lv.content.controls.remove(control)  
            lv.update()
            time.sleep(.1)
        lv.content.controls.append(preview_placeholder)
        lv.update()
        song_list = []
        added_controls = []
        print(song_list)    

    global indivudual_download
    def indivudual_download(link):
        individual_status=ft.Container(ft.Row([ft.Text('Downloading...', size=16), ft.ProgressRing(color='green', width=30, height=30),],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=405, height=50, bgcolor=ft.colors.BLACK12,padding=ft.Padding(left=10, top=5, right=10, bottom=5))
        
        for i, (uid, control) in enumerate(added_controls):
            if uid == link:
                download_button = control.content.content.controls[2].content.controls[0]
                download_button.disabled = True
                control.update()
                main_control_bar.content.content.controls.pop(2)
                main_control_bar.content.content.controls.insert(2, individual_status)
                main_control_bar.update()
                on_download(link)
                main_control_bar.content.content.controls.remove(individual_status)
                main_control_bar.content.content.controls.insert(2, finished_status)
                main_control_bar.update()

    def download_all(e):
        download_number=0
        for i, (uid, control) in enumerate(added_controls):
            download_button = control.content.content.controls[2].content.controls[0]
            download_button.disabled = True
            control.update()
        for item in song_list[:]:
            download_number = download_number +1
            full_download_number=f"({download_number}/{len(song_list)})"
            multiple_status=ft.Container(ft.Row([ft.Text(f'Downloading... {full_download_number}', size=16), ft.ProgressRing(color='green', width=30, height=30),],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=405, height=50, bgcolor=ft.colors.BLACK12,padding=ft.Padding(left=10, top=5, right=10, bottom=5))
            main_control_bar.content.content.controls.pop(2)
            main_control_bar.content.content.controls.insert(2, multiple_status)
            main_control_bar.update()
            on_download(item)
        main_control_bar.content.content.controls.remove(multiple_status)
        main_control_bar.content.content.controls.insert(2, finished_status)
        main_control_bar.update()

    def on_download_client_choice():  
        if downloader.value == 'Auto':
            format_choice.disabled = True
            audio_quality.disabled = True
            video_quality.disabled = True
            format_unselected.disabled = True
        else:
            format_choice.disabled = False
            audio_quality.disabled = False
            video_quality.disabled = False
            format_unselected.disabled = False
        page.update()
        
    download_button = ft.IconButton( height="50", width='50', icon=ft.icons.ADD_LINK, tooltip='Add To Queue', style=ft.ButtonStyle(
                      shape=ft.RoundedRectangleBorder(radius=5),bgcolor=ft.colors.BLACK26, color=ft.colors.GREEN), on_click=show_previews)

    clear_url_entry = ft.IconButton( icon=ft.icons.CLEAR, height="50",width=50, style=ft.ButtonStyle(
                      shape=ft.RoundedRectangleBorder(radius=5),bgcolor=ft.colors.BLACK26, color='grey'), on_click=clear_url)
    
    main_control_bar = ft.Card(content=ft.Container(content=ft.Row([ft.IconButton( height="50", width=50, icon=ft.icons.DOWNLOADING_ROUNDED,  style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5), bgcolor=ft.colors.BLACK26,color=ft.colors.GREEN,), tooltip='Download All', on_click=download_all), ft.IconButton(height="50", width=50, icon=ft.icons.DELETE_FOREVER, style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5), bgcolor=ft.colors.BLACK26,color=ft.colors.GREY,), tooltip='Clear All', on_click=remove_all_previews), ft.Container(ft.Row([],expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,),width=405, height=50, bgcolor=ft.colors.BLACK12,padding=ft.Padding(left=10, top=5, right=10, bottom=5)), ft.IconButton( height="50", width=50,icon=ft.icons.SETTINGS, style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5), bgcolor=ft.colors.BLACK26,color=ft.colors.GREY,), tooltip='Settings',on_click=settings), ft.IconButton( height="50",width=50, icon=ft.icons.TERMINAL,  style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5), bgcolor=ft.colors.BLACK26,color=ft.colors.GREEN,), tooltip='Terminal output', on_click=show_terminal),], width=700, height=50), padding=ft.Padding(left=5, top=5, right=5, bottom=5)))

    status_display = main_control_bar.content.content.controls[2]
    #how to remove the current status display
    #main_control_bar.content.content.controls.remove(status_display)

    row_1 = ft.Card(content=ft.Container(content=ft.Row(controls=[
            ft.Text(value=" URL:", color="green", weight=ft.FontWeight.BOLD, size=15), 
            link_entry, clear_url_entry,
            download_button], alignment=ft.MainAxisAlignment.SPACE_EVENLY,  height='50', ),padding=ft.Padding(left=0, top=5, right=0, bottom=5) ))
    
    row_2 = ft.Row(controls=[
            edit_path_button,
            output_path,
            downloader], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    row_3 = ft.Row(controls=[
            add_metadata,
            align_format_choice
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    row_4 = ft.Row(controls=[
        embed_thumbnail,
        align_unselected_quality
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    #adds all the ui elements to the page

    def draw_main_page():    
        for control in page.controls[:]:
            page.remove(control)
        page.add(row_1, row_2, row_3, row_4, lv, main_control_bar,)
        page.update()
    
    draw_main_page()

ft.app(target=main)

#todo: rename lv to preview_list

#song_list now always contains a link for every song in the preview window. now
#need to write a function to check the kind of link, then download for each one
