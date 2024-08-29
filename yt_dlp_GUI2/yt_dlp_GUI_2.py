import flet as ft
import subprocess
import os

#these 2 line get the download directory and attach it to 'downloads_folder'
home_dir = os.path.expanduser("~")
downloads_folder = os.path.join(home_dir, "Downloads")

#this var stores the command run by subprocess when on_download is called
download_command_line = ""

si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
CREATE_NO_WINDOW = 0x08000000

#the main function of the flet application, contains all ui elements and logic
def main(page: ft.Page):
    #declares page size, title, etc
    page.window.width = 700
    page.window.height = 285
    page.title = "yt-dlp_GUI2 (©️ Mauhs lol)"
    page.icon = "C:/Users/shuam/Downloads/yt_dlp_GUI2_icon.png"

    #this function updates the value of the  'output_path' var after a new download path is chosen, called after filepicker returns a result
    def on_dialog_result(e: ft.FilePickerResultEvent):
        global downloads_folder
        downloads_folder = e.path
        output_path.value=downloads_folder
        output_path.update()
    
    #creates the filepicker object, and adds it without rendering to the page
    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)
    page.update()

    #this button and textfield make up the ui elements for choosing an output path
    edit_path_button = ft.IconButton(icon=ft.icons.EDIT, on_click=lambda _: file_picker.get_directory_path(), icon_color='green')
    output_path = ft.TextField(label="Output destination", read_only=True, value=downloads_folder, width='250')

    #this function dynamically updates the qaulity options based on the format chosen. (for video you get resolutions, audio bitrates etc)
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

    #this control/widget gives the options for the downloader client
    downloader = ft.Dropdown(
    label="Downloader Client",
    options=[
        ft.dropdown.Option("yt-dlp"),
        ft.dropdown.Option("spot_dl (for spotify links)")], width="350")
    
    #gives options for format   
    format_choice = ft.Dropdown(
    label="Select format",
    options=[
        ft.dropdown.Option("mp4"),
        ft.dropdown.Option("mp3"),
        ft.dropdown.Option("m4a"),
        ft.dropdown.Option("flac")], on_change=on_format_select, width="350")
    
    #gives options for audio quality
    audio_quality = ft.Dropdown(
    label="Select Audio quality",
    options=[
        ft.dropdown.Option("Best available quality"),
        ft.dropdown.Option("160 kbps"),
        ft.dropdown.Option("128 kbps"),
        ft.dropdown.Option("70 kbps")], width="350")

    #gives options for video quality
    video_quality = ft.Dropdown(
    label="Select Video quality",
    options=[
        ft.dropdown.Option("Best available quality"),
        ft.dropdown.Option("1080p"),
        ft.dropdown.Option("720p"),
        ft.dropdown.Option("480p"),
        ft.dropdown.Option("480p")], width="350")
    
    #if no format is selected yet, this is the placeholder dropdown menu
    format_unselected = ft.Dropdown(
    label="Select quality",
    options=[
        ft.dropdown.Option("select a format first")], width="350")
    
    #all of the following containers hold the dropdownmenus declared above and align them to right
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

    #these switches control metadata options 
    add_metadata = ft.Switch(label="  Include metadata", active_color='green')
    embed_thumbnail = ft.Switch(label="  Embed thumbnail/album art", active_color='green')
    #this is the textfield for entering a url
    link_entry = ft.TextField(label="song, album, playlist, or video", width="490")

    #this huge function is called when the download button is pressed. it checks the value of every input element and based on that adds the correct parameters to 'download_command_line'
    #it then runs 'download_command_line' with subprocess
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
        result = subprocess.call(download_command_line, shell=True, text=True)
        #print(result.stdout)
        print(download_command_line)
        download_command_line = ''
        print(embed_thumbnail_selection)
    
    #this declares the download button
    download_button = ft.ElevatedButton(text="Download", height="50", color="green", on_click=on_download)

    #this places all the ui elements at the top of the page into the first row to be rendered
    row_1 = ft.Row(controls=[
            ft.Text(value="  URL:", color="green", width='42', weight=ft.FontWeight.BOLD), 
            link_entry,
            download_button])
    #the second row of elements to be rendered
    row_2 = ft.Row(controls=[
            edit_path_button,
            output_path,
            downloader], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    #third row to be rendered
    row_3 = ft.Row(controls=[
            add_metadata,
            align_format_choice
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    #3 different variations neede for row4 so they are all created here
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

    #this single line adds every single ui element to the page to make them visible
    page.add(row_1, row_2, row_3, row_4_unselected)

#this runs the main function, and starts the app
ft.app(target=main)
