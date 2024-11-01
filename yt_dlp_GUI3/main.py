#v.0.4
import flet as ft
import subprocess
import os
import requests
from base64 import b64encode
import yt_dlp

home_dir = os.path.expanduser("~")
downloads_folder = os.path.join(home_dir, "Downloads")
download_command_line = ""
si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
CREATE_NO_WINDOW = 0x08000000

#spotify api stuff
client_id = ''
client_secret = ''

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
    song_name = data.get("name", "Unknown Song")
    album_name = data.get("album", {}).get("name", "Unknown Album")
    artist_name = data.get("artists", [{}])[0].get("name", "Unknown Artist")
    album_art_url = data.get("album", {}).get("images", [{}])[0].get("url", "No album art available")
    length_ms = data.get('duration_ms') 
    minutes =(length_ms // 1000) // 60
    seconds = length_ms // 1000 - (minutes * 60)
    if seconds < 10:
        seconds = f"0{seconds}"

    #print(data)     
    preview_tab_example = ft.Card(
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
                        ft.Text(f"{minutes}:{seconds}", size = 14,  weight=ft.FontWeight.W_500)
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
    
    added_controls.append((unique_id, preview_tab_example))
    if preview_placeholder in lv.controls:    
        lv.controls.remove(preview_placeholder)
    lv.controls.insert(0, preview_tab_example)

def youtube_link():
    global added_controls
    global number_of_songs
    global song_list
    unique_id = link_entry.value

    ydl_opts = {'dump_single_json': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        song_info = ydl.extract_info(link_entry.value, download=False)
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

    preview_tab_example = ft.Card(
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
                        ft.Text(f"{minutes}:{seconds} - {megabytes}.{str(decimal_place)[:-4]} MB", size = 14,  weight=ft.FontWeight.W_500)
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
    
    added_controls.append((unique_id, preview_tab_example))
    if preview_placeholder in lv.controls:
        lv.controls.remove(preview_placeholder)
    lv.controls.insert(0, preview_tab_example)

def main(page: ft.Page):
    page.window.width = 700
    page.window.height = 600
    page.title = "yt-dlp_GUI3 (©️ Mauhs lol)"
    page.icon = "C:/Users/shuam/Downloads/yt_dlp_GUI2_icon.png"       
    #page.window.opacity = 0.95

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
        elif format_choice.value in ['m4a', 'mp3', 'flac', 'opus']:
            row_4.controls.append(align_audio_quality)
        else:
           row_4.controls.append(align_unselected_quality)
        page.update()
    
    downloader = ft.Dropdown(
    label="Downloader Client",
    options=[
        ft.dropdown.Option("yt-dlp (For Videos)"),
        ft.dropdown.Option("spotdl (For Music)")], width="350")
       
    format_choice = ft.Dropdown(
    label="Codec",
    options=[
        ft.dropdown.Option("mp4"),
        ft.dropdown.Option("mp3"),
        ft.dropdown.Option("m4a"),
        ft.dropdown.Option("opus"),
        ft.dropdown.Option("flac")], on_change=on_format_select, width="350")

    audio_quality = ft.Dropdown(
    label="Bitrate",
    options=[
        ft.dropdown.Option("Best available quality"),
        ft.dropdown.Option("160 kbps"),
        ft.dropdown.Option("128 kbps"),
        ft.dropdown.Option("70 kbps")], width="350")

    video_quality = ft.Dropdown(
    label="Resolution",
    options=[
        ft.dropdown.Option("Best available quality"),
        ft.dropdown.Option("1080p"),
        ft.dropdown.Option("720p"),
        ft.dropdown.Option("480p"),
        ft.dropdown.Option("480p")], width="350")

    format_unselected = ft.Dropdown(      
    label="Select quality",
    options=[
        ft.dropdown.Option("select a format first")], width="350")

    global preview_placeholder
    preview_placeholder = ft.Card(
        content=ft.Container(
            content=ft.Text("Download previews will appear here."),
            width=700,
            height=290,
            padding=0,
            border_radius=5,
            bgcolor=ft.colors.BLACK54,
            alignment=ft.alignment.center))

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
    lv = ft.ListView(spacing=1, padding=5, auto_scroll=False, expand=True)
    lv.controls.append(preview_placeholder)
    #lv.controls.append(preview_tab_example)

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
    link_entry = ft.TextField(label="song, album, playlist, or video", width="465")

    global on_download
    def on_download(e, link):
        global download_command_line 
        format_selection = format_choice.value
        downloader_selection = downloader.value
        audio_quality_selection = audio_quality.value
        video_quality_selection = video_quality.value
        embed_thumbnail_selection = embed_thumbnail.value
        add_metadata_selection = add_metadata.value
        #client choice
        if 'spotify' in link or 'music' in link:
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
            download_command_line +='yt-dlp '
            download_command_line += f'-P {downloads_folder} '
        elif downloader_selection == 'spot_dl (for spotify links)':
            download_command_line +='spotdl '
        else:
            download_command_line +='yt-dlp '
            download_command_line += f'-P {downloads_folder} '
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
            download_command_line += '-x --audio-format mp3 '
    
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
            
        download_command_line += link
        subprocess.call(download_command_line, shell=True, text=True)
        #print(result.stdout)
        print(download_command_line)
        download_command_line = ''
    
    def show_previews(e):
        if link_entry.value in song_list:
            return
        song_list.append(link_entry.value)
        #print(song_list)
        if 'spotify' in link_entry.value:
            spotify_link()
        else:
            youtube_link()
        page.update()

    global remove_control
    def remove_control(link):
        global song_list
        for i, (uid, control) in enumerate(added_controls):
            if uid == link:
                added_controls.pop(i)
                lv.controls.remove(control)  
                lv.update()
        song_list = [item for item in song_list if item != link]
        print(song_list)
        if len(song_list) < 1:
            lv.controls.append(preview_placeholder)
        page.update()

    global indivudual_download
    def indivudual_download(link):
        e= 1
        on_download(e, link)

    download_button = ft.ElevatedButton(text="Add to Queue", height="50", color="green", style=ft.ButtonStyle(
                      shape=ft.RoundedRectangleBorder(radius=5)), on_click=show_previews)

    row_1 = ft.Row(controls=[
            ft.Text(value="  URL:", color="green", width='42', weight=ft.FontWeight.BOLD), 
            link_entry,
            download_button])
    
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
    page.add(row_1, row_2, row_3, row_4, lv)

ft.app(target=main)

#todo: rename lv to preview_list

#song_list now always contains a link for every song in the preview window. now
#need to write a function to check the kind of link, then download for each one

#todo: rename lv to preview_list
