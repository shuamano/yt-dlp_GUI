# yt-dlp_GUI

### A simple GUI for yt-dlp and spotdl (work in progress)


* enter a link
* add it the queue
* configure download settings, download path, metadata etc
* download or remove songs/videos in the queue



![Screenshot 2024-11-21 111650](https://github.com/user-attachments/assets/0cb98d9d-d838-4a20-8377-50b24611f04f)



### Installation:
simply download "yt-dlp_GUI.pyw" and run it. 
The only prerequisite required is python itself; the GUI script will install dependancies on its own if they aren't already present.

### Usage:
* Links:
  you can enter links from any site that is supported by yt-dlp.  
   Only youtube and (most) spotify links get the cool previews tho.

* Download behaviour:
  In 'Auto' mode, ytmusic/spotify links will downoad as 128kps mp3's with metadata attached.
  regular yt links will be downloaded as mp4s w/audio, and other links will be determined by yt-dlp.

### Missing features:
* no error messages on failure
* light theme looks abysmally terrible
* proper progress tracking is non existant
