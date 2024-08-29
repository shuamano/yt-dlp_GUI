import flet as ft
import subprocess
import os

home_dir = os.path.expanduser("~")
downloads_folder = os.path.join(home_dir, "Downloads")
download_command_line = ""

def main(page: ft.Page):
    page.window.width = 700
    page.window.height = 285
    page.title = "yt-dlp_GUI2 (©️ Mauhs lol)"
    
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
        if row_4_video in page.controls:
            page.controls.remove(row_4_video)
        if row_4_audio in page.controls:
            page.controls.remove(row_4_audio)
        if row_4_unselected in page.controls:
            page.controls.remove(row_4_unselected)     

        if format_choice.value == "mp4":
            page.add(row_4_video)
        elif format_choice.value in ['m4a', 'mp3', 'flac']:
            page.add(row_4_audio)
        else:
            page.add(row_4_unselected)
        page.update()
    
    downloader = ft.Dropdown(
    label="Downloader Client",
    options=[
        ft.dropdown.Option("yt-dlp"),
        ft.dropdown.Option("spot_dl (for spotify links)")], width="350")
       
    format_choice = ft.Dropdown(
    label="Select format",
    options=[
        ft.dropdown.Option("mp4"),
        ft.dropdown.Option("mp3"),
        ft.dropdown.Option("m4a"),
        ft.dropdown.Option("flac")], on_change=on_format_select, width="350")

    audio_quality = ft.Dropdown(
    label="Select Audio quality",
    options=[
        ft.dropdown.Option("Best available quality"),
        ft.dropdown.Option("160 kbps"),
        ft.dropdown.Option("128 kbps"),
        ft.dropdown.Option("70 kbps")], width="350")

    video_quality = ft.Dropdown(
    label="Select Video quality",
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
      
    add_metadata = ft.Switch(label="  Include metadata", active_color='green')
    embed_thumbnail = ft.Switch(label="  Embed thumbnail/album art", active_color='green')
    link_entry = ft.TextField(label="song, album, playlist, or video", width="490")

    def on_download(e):
        global download_command_line 
        format_selection = format_choice.value
        downloader_selection = downloader.value
        audio_quality_selection = audio_quality.value
        video_quality_selection = video_quality.value
        embed_thumbnail_selection = embed_thumbnail.value
        add_metadata_selection = add_metadata.value
        #client choice
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

        download_command_line += link_entry.value
        result = subprocess.run(download_command_line, capture_output=True, text=True)
        print(result.stdout)
        print(download_command_line)
        download_command_line = ''
        print(embed_thumbnail_selection)
    download_button = ft.ElevatedButton(text="Download", height="50", color="green", on_click=on_download)

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
    
    row_4_unselected = ft.Row(controls=[
        embed_thumbnail,
        align_unselected_quality
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    row_4_video = ft.Row(controls=[
        embed_thumbnail,
        align_video_quality
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    row_4_audio = ft.Row(controls=[
        embed_thumbnail,
        align_audio_quality
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    page.add(row_1, row_2, row_3, row_4_unselected)

ft.app(target=main)
