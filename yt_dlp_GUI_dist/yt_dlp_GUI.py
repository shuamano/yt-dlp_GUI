import tkinter as tk
from tkinter.ttk import *
import subprocess
from tkinter.ttk import Combobox
from tkinter import ttk 
from tkinter import filedialog 

root = tk.Tk()
root.geometry('500x165')
root.title("Yt-dlp_GUI (©️ Mauhs lol)")

format_choice=tk.StringVar()
client_choice=tk.StringVar()
video_choice=tk.StringVar()
audio_choice=tk.StringVar()
include_metadata = tk.IntVar()
embedd_thumbnail = tk.IntVar()

download_command_line = ""

downloader_client_input = Combobox(root, textvariable=client_choice, values=["yt-dlp", "spotdl (for spotify links)"]).grid( row=1, column=5, padx=10, pady=0, sticky="e")
format_input = ttk.Combobox(root, textvariable=format_choice, values=["mp4", "mp3", 'm4a', 'flac'], state='readonly')
format_input.grid( row=2, column=5, padx=10, pady=10, sticky="e")

video_quality_input = Combobox(root, textvariable=video_choice, values=["best quality", "1080p", "720p", '480p', '360p'])
audio_quality_input = Combobox(root, textvariable=audio_choice, values=["best quality", "128 kbps", '160 kbps', '70 kbps'])

def on_format_select(event):
    if format_choice.get() == 'mp4':
        audio_quality_input.grid_forget()
        video_quality_input.grid( row=3, column=5, padx=10, pady=0, sticky="e")
    else:
        audio_quality_input.grid( row=3, column=5, padx=10, pady=0, sticky="e")

def choose_download_folder():
    global folder_path
    folder_path = tk.filedialog.askdirectory()
    print(folder_path)

def on_download():
    global download_command_line 
    #client choice
    if client_choice.get() == 'yt-dlp':
        download_command_line +='yt-dlp '
        download_command_line += f'-P {folder_path} '
    elif client_choice.get() == 'spotdl (for spotify links)':
        download_command_line +='spotdl '
    else:
        download_command_line +='yt-dlp '
        download_command_line += f'-P {folder_path} '
    #format choice
    if format_choice.get() == 'mp4':
        download_command_line += '--merge-output-format mp4 '
    elif format_choice.get() == 'm4a':
        download_command_line += '-x --audio-format m4a '
    elif format_choice.get() == 'mp3':
        download_command_line += '-x --audio-format mp3 '
    elif format_choice.get() == 'flac':
        download_command_line += '-x --audio-format flac '
    else:
        pass
    
    #video quality choice
    if video_choice.get() == '1080p':
        download_command_line += '-f 137+bestaudio '
    elif video_choice.get() == '720p':
        download_command_line += '-f 136+bestaudio '
    elif video_choice.get() == '480p':
        download_command_line += '-f 135+bestaudio '
    elif video_choice.get() == '360p':
        download_command_line += '-f 134+bestaudio '
    else:
        pass

    #audio quality choice
    if audio_choice.get() == '128 kbps':
        download_command_line += '--audio-quality 128K '
    elif audio_choice.get() == '160 kbps':
        download_command_line += '--audio-quality 160K '
    elif audio_choice.get() == '70 kbps':
        download_command_line += '--audio-quality 70K '
    else:
        pass
    if include_metadata.get() == 1:
        download_command_line += '--add-metadata '
    if embedd_thumbnail.get() == 1:
        download_command_line += '--embed-thumbnail '

    download_command_line += link_entry.get()
    result = subprocess.run(download_command_line, capture_output=True, text=True)
    print(result.stdout)
    print(download_command_line)
    download_command_line = ''
    audio_choice.set('')
    video_choice.set('')

tk.Label(root, text="URL:").grid(row=0, column=1, padx=10, pady=10, sticky="w")
tk.Label(root, text="downloader client:").grid(row=1, column=2, sticky="e")
tk.Label(root, text="format:").grid(row=2, column=2, sticky="e")
tk.Label(root, text="quality:").grid(row=3, column=2, sticky="e")
tk.Label(root, text="output location:").grid(row=4, column=2, pady=10, sticky="e")
tk.Label(root, text="add metadata:").grid(row=1, column=1, columnspan=2, padx=10, sticky="w")
tk.Label(root, text="embed thumbnail:").grid(row=2, column=1, columnspan=2, padx=10, sticky="w")

link_entry = Entry(root, width=50)
link_entry.grid(row=0, column=2, padx=0, pady=10, sticky="w")

download_button = Button(root, command=on_download, text="download").grid(row=0,column=5, padx=10, sticky="ew")
choose_path = Button(root, command=choose_download_folder, text="browse").grid(row=4,column=5, padx=10, sticky="ew")
add_metadata = ttk.Checkbutton(root, variable=include_metadata)
add_metadata.grid(row=1, column=1, columnspan=2, sticky='')
embed_thumbnail = ttk.Checkbutton(root, variable=embedd_thumbnail)
embed_thumbnail.grid(row=2, column=1, columnspan=2, sticky='')

root.columnconfigure(5, weight=1)
root.columnconfigure(4, weight=1)
root.columnconfigure(3, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(0, weight=1)
format_input.bind("<<ComboboxSelected>>", on_format_select)

root.mainloop()